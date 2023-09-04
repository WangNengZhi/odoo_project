from odoo import models, fields, api
import calendar, datetime



class ClientWare(models.Model):
    '''客仓'''
    _inherit = 'client_ware'

    general_inspection_month_efficiency_id = fields.Many2one("general_inspection_month_efficiency", string="总检月效率表", compute="set_general_inspection_month_efficiency", store=True)

    @api.depends("general")
    def set_general_inspection_month_efficiency(self):
        ''' 设置总检月效率表'''
        for record in self:

            if record.dDate and record.gGroup and record.style_number and record.general:

                year, month, _ = str(record.dDate).split("-")
                year_month = f"{year}-{month}"
                general_inspection_month_efficiency_obj = self.env['general_inspection_month_efficiency'].sudo().search([
                    ("month", "=", year_month),
                    ("group", "=", record.gGroup),
                    ("style_number", "=", record.style_number.id),
                    ("general", "=", record.general)
                ])
                if not general_inspection_month_efficiency_obj:
                    general_inspection_month_efficiency_obj = self.env['general_inspection_month_efficiency'].sudo().create({
                        "month": year_month,
                        "group": record.gGroup,
                        "style_number": record.style_number.id,
                        "general": record.general
                    })
                
                record.general_inspection_month_efficiency_id = general_inspection_month_efficiency_obj.id

                general_inspection_month_efficiency_obj.sudo().set_general_ids()

                general_inspection_month_efficiency_obj.sudo().set_dg_ids()

                general_inspection_month_efficiency_obj.sudo().set_dg_repair_ids()
            

    @api.model
    def create(self, vals):

        res = super(ClientWare, self).create(vals)

        res.sudo().set_general_inspection_month_efficiency()

        return res
    

class GeneralGeneral(models.Model):
    '''总检'''
    _inherit = 'general.general'


    def set_general_inspection_month_efficiency(self):
        ''' 设置总检月效率表'''
        for record in self:
                
            year, month, _ = str(record.date).split("-")
            year_month = f"{year}-{month}"
            general_inspection_month_efficiency_objs = self.env['general_inspection_month_efficiency'].sudo().search([
                ("month", "=", year_month),
                ("group", "=", record.group),
                ("style_number", "=", record.item_no.id),
                ("general", "like", record.general1)
            ])
            if general_inspection_month_efficiency_objs:
                for general_inspection_month_efficiency_obj in general_inspection_month_efficiency_objs:
                    general_inspection_month_efficiency_obj.general_ids = [(4, record.id)]


    @api.model
    def create(self, vals):

        res = super(GeneralGeneral, self).create(vals)

        res.sudo().set_general_inspection_month_efficiency()

        return res



class GeneralInspectionMonthEfficiency(models.Model):
    _name = 'general_inspection_month_efficiency'
    _description = '总检月效率表'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group = fields.Char(string='组别')
    general = fields.Char(string='总检')
    style_number = fields.Many2one('ib.detail', string='款号')

    client_ware_ids = fields.One2many("client_ware", "general_inspection_month_efficiency_id", string="客仓")
    client_ware_repair_number = fields.Integer(string="尾查返修件数", compute="set_client_ware_repair_number", store=True)
    @api.depends("client_ware_ids", "client_ware_ids.repair_number")
    def set_client_ware_repair_number(self):
        for record in self:
            record.client_ware_repair_number = sum(record.client_ware_ids.filtered(lambda x: x.check_type == "尾查").mapped("repair_number"))

    general_ids = fields.Many2many("general.general", string="总检")
    general_repair_number = fields.Integer(string="总检返修数", compute="set_general_info", store=True)
    general_check_number = fields.Integer(string="总检查货数", compute="set_general_info", store=True)
    @api.depends("general_ids", "general_ids.general_number", "general_ids.repair_number")
    def set_general_info(self):
        for record in self:
            record.general_repair_number = sum(record.general_ids.mapped("repair_number"))
            record.general_check_number = sum(record.general_ids.mapped("general_number"))
            print(record.general_repair_number)

    repair_rate = fields.Float(string="返修率", compute="set_repair_rate", store=True, group_operator='avg')
    @api.depends("general_check_number", "general_repair_number")
    def set_repair_rate(self):
        ''' 计算返修率'''
        for record in self:
            if record.general_check_number:
                record.repair_rate = record.general_repair_number / record.general_check_number
            else:
                record.repair_rate = 0

    omission_rate = fields.Float(string="漏查率", compute="set_omission_rate", store=True, group_operator='avg')
    @api.depends("client_ware_repair_number", "general_check_number")
    def set_omission_rate(self):
        ''' 计算漏查率'''
        for record in self:
            if record.general_check_number:
                record.omission_rate = record.client_ware_repair_number / record.general_check_number
            else:
                record.omission_rate = 0


    punishment = fields.Float(string="扣款", compute="set_punishment", store=True)
    @api.depends("client_ware_repair_number")
    def set_punishment(self):
        for record in self:
            record.punishment = record.client_ware_repair_number * 5



    dg_ids = fields.Many2many("suspension_system_station_summary",
        relation='gime_ssss',
        column1='general_inspection_month_efficiency_id',
        column2='suspension_system_station_summary_id',
        string="吊挂")
    dg_check_number = fields.Integer(string="总检吊挂查货件数", compute="set_dg_check_number", store=True)
    @api.depends('dg_ids', 'dg_ids.total_quantity')
    def set_dg_check_number(self):
        for record in self:
            record.dg_check_number = sum(record.dg_ids.mapped("total_quantity"))
            print(record.dg_check_number)

    dg_repair_ids = fields.Many2many("suspension_system_rework",
        relation='gime_ssr',
        column1='general_inspection_month_efficiency_id',
        column2='suspension_system_rework_id',
        string="吊挂返修")
    dg_repair_number = fields.Integer(string="总检吊挂返修件数", compute="set_dg_repair_number", store=True)
    @api.depends('dg_repair_ids', 'dg_repair_ids.number')
    def set_dg_repair_number(self):
        for record in self:
            record.dg_repair_number = sum(record.dg_repair_ids.mapped("number"))


    dg_rate_repair = fields.Float(string="总检吊挂返修率", compute="set_dg_rate_repair", store=True, group_operator='avg')
    @api.depends("dg_repair_number", "dg_check_number")
    def set_dg_rate_repair(self):
        for record in self:
            if record.dg_check_number:
                record.dg_rate_repair = record.dg_repair_number / record.dg_check_number
            else:
                record.dg_rate_repair = 0


    def set_begin_and_end(self, year, month):
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end


    def set_general_ids(self):
        ''' 设置总检'''
        for record in self:
            
            if record.month and record.group and record.style_number and record.general:

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                general_lst = record.general.split(" ")

                general_objs = self.env['general.general'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", record.group),
                    ("item_no", "=", record.style_number.id),
                    ("general1", "in", general_lst)
                ])
                if general_objs:
                    record.general_ids = [(6, 0, general_objs.ids)]


    def set_dg_ids(self):
        ''' 设置吊挂'''

        for record in self:
             
             if record.month and record.style_number and record.group and record.general:

                check_position_settings_obj = self.env['check_position_settings'].sudo().search([
                    ("group", "=", "后整"),
                    ("department_id", "=", "后道")
                ])

                general_lst = record.general.split(" ")

                emp_obj_ids = self.env['hr.employee'].sudo().search([("name", "in", general_lst)]).ids

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", ">=", this_month_start),
                    ("dDate", "<=", this_month_end),
                    ("group", "=", check_position_settings_obj.id),
                    ("employee_id", "in", emp_obj_ids),
                    ("style_number", "=", record.style_number.id),
                    ("station_number", "in", check_position_settings_obj.mapped('position_line_ids.position'))
                ])

                if suspension_system_station_summary_objs:
                    record.dg_ids = [(6, 0, suspension_system_station_summary_objs.ids)]



    def set_dg_repair_ids(self):
        ''' 设置吊挂漏查'''
        for record in self:
             
             if record.month and record.style_number and record.group and record.general:

                general_lst = record.general.split(" ")

                emp_obj_ids = self.env['hr.employee'].sudo().search([("name", "in", general_lst)]).ids

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                suspension_system_rework_objs = self.env['suspension_system_rework'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("qc_employee_id", "in", emp_obj_ids),
                    ("style_number", "=", record.style_number.id),
                    ("qc_type", "=", "总检"),
                ])

                if suspension_system_rework_objs:
                    record.dg_repair_ids = [(6, 0, suspension_system_rework_objs.ids)]
    
    def update_general_inspection_month_efficiency(self):
        for record in self:
            year, month = map(int, record.month.split("-"))   
            this_month_start, this_month_end = self.set_begin_and_end(year, month)
            general_general_dates = self.env['general.general'].sudo().search([
                ("date", ">=", this_month_start),
                ("date", "<=", this_month_end),
                ("general1", "=", record.general),
            ])
            for general_general_date in general_general_dates:
                general_general_date_old = self.env['general_inspection_month_efficiency'].sudo().search([
                ("month", "=", record.month),
                ("style_number", "=", general_general_date.item_no.id),
                ("general", "=", record.general),
                ("group", "=", general_general_date.group),
            ])
                client_ware_date = self.env['client_ware'].sudo().search([
                    ("dDate", ">=", this_month_start),
                    ("dDate", "<=", this_month_end),
                    #("gGroup", "=", general_general_date.group),
                    ("style_number", "=", general_general_date.item_no.id),
                    ("general", "=", general_general_date.general1),
                    ("check_type", "=", '尾查')
                ])
                general_repair_number_datas  = self.env['general.general'].sudo().search([
                ("date", ">=", this_month_start),
                ("date", "<=", this_month_end),
                ("general1", "=", general_general_date.general1),
                ("item_no", "=", general_general_date.item_no.id),
            ])
                dg_ids = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", ">=", this_month_start),
                    ("dDate", "<=", this_month_end),
                    ("employee_id.name", "=", general_general_date.general1),
                    ("style_number", "=", general_general_date.item_no.id),
                    ("group", "=", general_general_date.group),
                ])
                dg_repair_ids = self.env['suspension_system_rework'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("qc_employee_id.name", "=", general_general_date.general1),
                    ("style_number", "=", general_general_date.item_no.id),
                    ("qc_type", "=", "总检"),
                ])
                if sum(general_repair_number_datas.mapped('general_number')):
                    omission_rate = sum(client_ware_date.mapped('repair_number')) / sum(general_repair_number_datas.mapped('general_number'))
                else:
                    omission_rate = 0
                if sum(dg_ids.mapped('total_quantity')):
                   dg_rate_repair = sum(dg_repair_ids.mapped('number')) / sum(dg_ids.mapped('total_quantity'))
                else:
                   dg_rate_repair = 0
                year, month, _ = str(general_general_date.date).split("-")
                year_month = f"{year}-{month}"
                data = {
                        'month':year_month,
                        'group':general_general_date.group,
                        'general':general_general_date.general1,
                        'style_number':general_general_date.item_no.id,
                        'client_ware_repair_number':sum(client_ware_date.mapped('repair_number')),
                        'general_ids':general_general_date,
                        'general_repair_number':sum(general_repair_number_datas.mapped('repair_number')),
                        'general_check_number':sum(general_repair_number_datas.mapped('general_number')),
                        'omission_rate':omission_rate,
                        'punishment':sum(client_ware_date.mapped('repair_number')) * 5,
                        'dg_ids':dg_ids,
                        'dg_check_number':sum(dg_ids.mapped('total_quantity')),
                        'dg_repair_number':sum(dg_repair_ids.mapped('number')),
                        'dg_rate_repair':dg_rate_repair
                    }
                datas = {
                        'client_ware_repair_number':sum(client_ware_date.mapped('repair_number')),
                        'general_repair_number':sum(general_repair_number_datas.mapped('repair_number')),
                        'general_check_number':sum(general_repair_number_datas.mapped('general_number')),
                        'omission_rate':omission_rate,
                        'punishment':sum(client_ware_date.mapped('repair_number')) * 5,
                        'dg_check_number':sum(dg_ids.mapped('total_quantity')),
                        'dg_repair_number':sum(dg_repair_ids.mapped('number')),
                        'dg_rate_repair':dg_rate_repair
                    }
                if not general_general_date_old:
                    self.sudo().create(data)
                else:
                   self.env['general_inspection_month_efficiency'].sudo().search([("month", "=", record.month),
                                                                                  ("style_number", "=", general_general_date.item_no.id),
                                                                                  ("general", "=", record.general),
                                                                                  ("group", "=", general_general_date.group),]).write(datas)
   