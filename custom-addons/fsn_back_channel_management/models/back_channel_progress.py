from odoo import models, fields, api


class SuspensionSystemStationSummary(models.Model):
    """ 继承吊挂产量汇总"""
    _inherit = 'suspension_system_station_summary'

    back_channel_progress_id = fields.Many2one("back_channel_progress", string="后整进度表")


    def set_back_channel_progress(self):
        for record in self:
            if record.group.department_id == "后道":
                back_channel_progress_obj = self.env['back_channel_progress'].sudo().search([("date", "=", record.dDate)])

                if not back_channel_progress_obj:
                    back_channel_progress_obj = self.env['back_channel_progress'].sudo().create({
                        "date": record.dDate
                    })
                record.back_channel_progress_id = back_channel_progress_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemStationSummary, self).create(vals)

        res.sudo().set_back_channel_progress()

        return res



class SuspensionSystemRework(models.Model):
    """ 继承吊挂返修信息"""
    _inherit = 'suspension_system_rework'

    back_channel_progress_id = fields.Many2one("back_channel_progress", string="后整进度表")


    def set_back_channel_progress(self):
        for record in self:

            back_channel_progress_obj = self.env['back_channel_progress'].sudo().search([("date", "=", record.date)])

            if not back_channel_progress_obj:
                back_channel_progress_obj = self.env['back_channel_progress'].sudo().create({
                    "date": record.date
                })
            record.back_channel_progress_id = back_channel_progress_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemRework, self).create(vals)

        res.sudo().set_back_channel_progress()

        return res


class FinishedProductWareLine(models.Model):
    """ 仓库明细"""
    _inherit = 'finished_product_ware_line'

    back_channel_progress_id = fields.Many2one("back_channel_progress", string="后整进度表")

    def set_back_channel_progress(self):
        for record in self:

            if record.date:

                temp = record.back_channel_progress_id

                back_channel_progress_obj = self.env['back_channel_progress'].sudo().search([("date", "=", record.date)])

                if not back_channel_progress_obj:
                    back_channel_progress_obj = self.env['back_channel_progress'].sudo().create({
                        "date": record.date
                    })
                record.back_channel_progress_id = back_channel_progress_obj.id

                if temp:
                    temp.set_finished_product_ware_line_info()


    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine, self).create(vals)

        res.sudo().set_back_channel_progress()

        return res
    

class PlanningSlot(models.Model):
    ''' 日计划'''
    _inherit = 'planning.slot'

    back_channel_progress_id = fields.Many2one("back_channel_progress", string="后整进度表", compute="set_back_channel_progress", store=True)

    @api.depends("dDate")
    def set_back_channel_progress(self):
        for record in self:

            if record.dDate:


                temp = record.back_channel_progress_id

                back_channel_progress_obj = self.env['back_channel_progress'].sudo().search([("date", "=", record.dDate)])

                if not back_channel_progress_obj:
                    back_channel_progress_obj = self.env['back_channel_progress'].sudo().create({"date": record.dDate})
                record.back_channel_progress_id = back_channel_progress_obj.id

                if temp:
                    temp.set_plan_number()




    @api.model
    def create(self, vals):

        res = super(PlanningSlot, self).create(vals)

        res.sudo().set_back_channel_progress()

        return res



class BackChannelProgress(models.Model):
    _name = 'back_channel_progress'
    _description = '后整进度表'
    _rec_name = 'date'
    _order = "date desc"


    suspension_system_station_summary_ids = fields.One2many("suspension_system_station_summary", "back_channel_progress_id", string="吊挂站位")
    date = fields.Date(string="日期")
    planning_slot_ids = fields.One2many("planning.slot", "back_channel_progress_id", string="计划")
    plan_number = fields.Integer(string="计划产量", compute="set_plan_number", store=True)
    @api.depends('planning_slot_ids', 'planning_slot_ids.plan_number', 'planning_slot_ids.department_id')
    def set_plan_number(self):
        for record in self:
            print(record.planning_slot_ids)
            record.plan_number = sum(record.planning_slot_ids.filtered(lambda x: x.department_id == "后道").mapped("plan_number"))


    number = fields.Integer(string="人数", compute="set_number", store=True)
    @api.depends('suspension_system_station_summary_ids', 'suspension_system_station_summary_ids.employee_id')
    def set_number(self):
        for record in self:
            record.number = len(record.suspension_system_station_summary_ids.mapped("employee_id"))
    manual_number = fields.Integer(string="手工产量", compute="set_back_channel_progress_info", store=True)
    special_number = fields.Integer(string="专机产量", compute="set_back_channel_progress_info", store=True)
    big_iron_number = fields.Integer(string="大烫产量", compute="set_back_channel_progress_info", store=True)
    up_coat_hanger_number = fields.Integer(string="上衣架产量", compute="set_back_channel_progress_info", store=True)
    @api.depends('suspension_system_station_summary_ids', 'suspension_system_station_summary_ids.total_quantity')
    def set_back_channel_progress_info(self):
        check_position_settings_objs = self.env['check_position_settings'].sudo().search([("department_id", "=", "后道")])
        position_line_ids_list = check_position_settings_objs.position_line_ids.mapped('position')

        for record in self:
            manual_jobs_list = self.env.ref('fsn_back_channel_management.back_channel_progress_job_setting_manual').values.ids
            record.manual_number = sum(record.suspension_system_station_summary_ids.filtered\
                (lambda x: x.employee_id.job_id.id in manual_jobs_list and x.station_number not in position_line_ids_list and x.station_number != 0).mapped('total_quantity'))

            special_jobs_list = self.env.ref('fsn_back_channel_management.back_channel_progress_job_setting_special').values.ids
            record.special_number = sum(record.suspension_system_station_summary_ids.filtered\
                (lambda x: x.employee_id.job_id.id in special_jobs_list and x.station_number not in position_line_ids_list and x.station_number != 0).mapped('total_quantity'))

            big_iron_jobs_list = self.env.ref('fsn_back_channel_management.back_channel_progress_job_setting_big_iron').values.ids
            record.big_iron_number = sum(record.suspension_system_station_summary_ids.filtered\
                (lambda x: x.employee_id.job_id.id in big_iron_jobs_list and x.station_number not in position_line_ids_list and x.station_number != 0).mapped('total_quantity'))
            
            record.up_coat_hanger_number = sum(record.suspension_system_station_summary_ids.filtered(lambda x: x.station_number == 0).mapped('total_quantity'))



    always_check_number = fields.Integer(string="总检产量", compute="set_always_check_number", store=True)
    @api.depends('suspension_system_station_summary_ids', 'suspension_system_station_summary_ids.total_quantity')
    def set_always_check_number(self):
        check_position_settings_objs = self.env['check_position_settings'].sudo().search([("department_id", "=", "后道")])
        always_check_position_list = check_position_settings_objs.position_line_ids.filtered(lambda x: x.type == "总检").mapped('position')
        for record in self:

            record.always_check_number = sum(record.suspension_system_station_summary_ids.filtered(lambda x: x.station_number in always_check_position_list).mapped('total_quantity'))



    tail_check_number = fields.Integer(string="尾查产量", compute="set_tail_check_number", store=True)
    @api.depends('suspension_system_station_summary_ids', 'suspension_system_station_summary_ids.total_quantity')
    def set_tail_check_number(self):

        check_position_settings_objs = self.env['check_position_settings'].sudo().search([("department_id", "=", "后道")])
        tail_check_position_list = check_position_settings_objs.position_line_ids.filtered(lambda x: x.type == "尾查").mapped('position')

        for record in self:
            
            record.tail_check_number = sum(record.suspension_system_station_summary_ids.filtered(lambda x: x.station_number in tail_check_position_list).mapped('total_quantity'))



    
    suspension_system_rework_ids = fields.One2many("suspension_system_rework", "back_channel_progress_id", string="吊挂返修")
    always_check_repair_number = fields.Integer(string="总检返修数", compute="set_suspension_system_rework_info", store=True)
    tail_check_repair_number = fields.Integer(string="尾查返修数", compute="set_suspension_system_rework_info", store=True)

    @api.depends('suspension_system_rework_ids', 'suspension_system_rework_ids.number')
    def set_suspension_system_rework_info(self):
        for record in self:
            
            record.always_check_repair_number = sum(record.suspension_system_rework_ids.filtered(lambda x: x.qc_type == "总检").mapped("number"))

            record.tail_check_repair_number = sum(record.suspension_system_rework_ids.filtered(lambda x: x.qc_type == "尾查").mapped("number"))


    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "back_channel_progress_id", string="仓库明细")
    put_storage_number = fields.Integer(string="入库数", compute="set_finished_product_ware_line_info", store=True)


    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.process_type',\
            'finished_product_ware_line_ids.type',\
                'finished_product_ware_line_ids.state',\
                    'finished_product_ware_line_ids.number',\
                        'finished_product_ware_line_ids.quality',\
                            'finished_product_ware_line_ids.character')
    def set_finished_product_ware_line_info(self):
        for record in self:

            record.put_storage_number = sum(record.finished_product_ware_line_ids.filtered(\
                lambda x: x.process_type in ["工厂", "外发"] and x.type == "入库" and x.state == "确认" and x.quality == "合格" and x.character == "正常"\
                    ).mapped('number'))



    def action_suspension_system_station_summary_ids(self):

        action = {
            'name': "后道吊挂明细",
            'view_mode': 'tree',
            'res_model': 'suspension_system_station_summary',
            'view_id': self.env.ref('suspension_system.suspension_system_station_summary_tree').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('id', "in", self.suspension_system_station_summary_ids.ids)],
            'context': {'create': False, 'edit': False, 'delete': False},
        }

        return action
