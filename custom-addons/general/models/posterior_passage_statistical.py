from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class General(models.Model):
    """ 继承总检"""
    _inherit = 'general.general'


    posterior_passage_statistical_id = fields.Many2one("posterior_passage_statistical", string="后道返修统计")

    def set_posterior_passage_statistical(self):
        for record in self:
            if record.item_no:
                posterior_passage_statistical_obj = self.env["posterior_passage_statistical"].sudo().search([
                    ("dDate", "=", record.date),
                    ("group", "=", record.group),
                    ("general", "=", record.general1),
                    ("style_number", "=", record.item_no.id)
                ])
                if not posterior_passage_statistical_obj:

                    posterior_passage_statistical_obj = self.env["posterior_passage_statistical"].sudo().create({
                        "dDate": record.date,
                        "group": record.group,
                        "general": record.general1,
                        "style_number": record.item_no.id
                    })
                
                record.posterior_passage_statistical_id = posterior_passage_statistical_obj.id

                posterior_passage_statistical_obj.sudo().set_finished_product_ware_line_ids()

    @api.model
    def create(self, vals):

        res = super(General, self).create(vals)

        res.sudo().set_posterior_passage_statistical()

        return res


class DayQingDayBi(models.Model):
    """ 继承日清日毕"""
    _inherit = 'day_qing_day_bi'



class FinishedProductWareLine(models.Model):
    """ 继承出入库明细"""
    _inherit = 'finished_product_ware_line'


    def set_posterior_passage_statistical(self):
        for record in self:
            if record.style_number:
                posterior_passage_statistical_obj = self.env["posterior_passage_statistical"].sudo().search([
                    ("dDate", "=", record.date),
                    ("style_number", "=", record.style_number.id)
                ])
                if posterior_passage_statistical_obj:
                    posterior_passage_statistical_obj.finished_product_ware_line_ids = [(4, record.id)]

    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine, self).create(vals)

        res.sudo().set_posterior_passage_statistical()

        return res


class SuspensionSystemStationSummary(models.Model):
    """ 继承吊挂产量汇总"""
    _inherit = 'suspension_system_station_summary'



    def set_posterior_passage_statistical(self):

        for record in self:
            try:
                if record.style_number and record.employee_id:
                    posterior_passage_statistical_obj = self.env["posterior_passage_statistical"].sudo().search([
                        ("dDate", "=", record.dDate),
                        ("style_number", "=", record.style_number.id),
                        ("general", "=", record.employee_id.name),
                    ])
                    if posterior_passage_statistical_obj:
                        posterior_passage_statistical_obj.dg_detail_ids = [(4, record.id)]

            except Exception as e:
                _logger.info(e)

    @api.model
    def create(self, vals):

        res = super(SuspensionSystemStationSummary, self).create(vals)

        res.sudo().set_posterior_passage_statistical()

        return res


class SuspensionSystemRework(models.Model):
    """ 继承吊挂返修"""
    _inherit = 'suspension_system_rework'

    posterior_passage_statistical_id = fields.Many2one("posterior_passage_statistical", string="后道返修统计")

    def set_posterior_passage_statistical(self):
        map_groups = {
            "车缝一组": "1",
            "车缝二组": "2",
            "车缝三组": "3",
            "车缝四组": "4",
            "车缝五组": "5",
            "车缝六组": "6",
            "车缝七组": "7",
            "车缝八组": "8",
            "车缝九组": "9",
            "车缝十组": "10",
            "整件一组": "整件一组",
        }

        for record in self:
            try:
                posterior_passage_statistical_obj = self.env["posterior_passage_statistical"].sudo().search([
                    ("dDate", "=", record.date),
                    ("style_number", "=", record.style_number.id),
                    ("general", "=", record.qc_employee_id.name),
                    ("group", "=", map_groups[record.group.group])
                ])
                if not posterior_passage_statistical_obj:
                    posterior_passage_statistical_obj = self.env['posterior_passage_statistical'].sudo().create({
                        "dDate": record.date,
                        "style_number": record.style_number.id,
                        "general": record.qc_employee_id.name,
                        "group": map_groups[record.group.group]
                    })
                record.posterior_passage_statistical_id = posterior_passage_statistical_obj.id
            except Exception as e:
                _logger.info(e)

    @api.model
    def create(self, vals):

        res = super(SuspensionSystemRework, self).create(vals)

        res.sudo().set_posterior_passage_statistical()

        return res



class PosteriorPassageStatistical(models.Model):
    _name = 'posterior_passage_statistical'
    _description = '后道返修统计'
    _rec_name = 'dDate'
    _order = "dDate desc"

    dDate = fields.Date(string="日期")
    group = fields.Char(string="组别")
    general = fields.Char(string="总检")
    style_number = fields.Many2one('ib.detail', string='款号')
    general_general_ids = fields.One2many("general.general", "posterior_passage_statistical_id", string="总检")

    repair_quantity = fields.Integer(string='返修数量', compute="_set_general_general_info", store=True)
    check_quantity = fields.Integer(string='查货数量', compute="_set_general_general_info", store=True)
    secondary_repair_number = fields.Integer(string="二次返修数", compute="_set_general_general_info", store=True)
    secondary_check_number = fields.Integer(string="二次返修查货数", compute="_set_general_general_info", store=True)
    @api.depends('general_general_ids',\
        'general_general_ids.repair_number',\
            'general_general_ids.general_number',\
                'general_general_ids.secondary_repair_number',\
                    'general_general_ids.secondary_check_number')
    def _set_general_general_info(self):
        for record in self:

            record.repair_quantity = sum(record.general_general_ids.mapped('repair_number'))
            record.check_quantity = sum(record.general_general_ids.mapped('general_number'))
            record.secondary_repair_number = sum(record.general_general_ids.mapped('secondary_repair_number'))
            record.secondary_check_number = sum(record.general_general_ids.mapped('secondary_check_number'))


    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)



    day_qing_day_bi_ids = fields.Many2many("day_qing_day_bi", string="日清日毕")
    dg_number = fields.Float(string="吊挂件数", compute="_set_hang_the_stranded", store=True)
    hang_the_stranded = fields.Float(string="吊挂滞留", compute="_set_hang_the_stranded", store=True)
    repair_ratio_a = fields.Float(string="返修率（件）", compute="_set_hang_the_stranded", store=True)

    @api.depends('day_qing_day_bi_ids', 'day_qing_day_bi_ids.stranded_number', 'day_qing_day_bi_ids.dg_number')
    def _set_hang_the_stranded(self):
        for record in self:

            record.dg_number = sum(record.day_qing_day_bi_ids.mapped('dg_number'))
        
            record.hang_the_stranded = sum(record.day_qing_day_bi_ids.mapped('stranded_number'))

            record.repair_ratio_a = record.hang_the_stranded / record.dg_number if record.dg_number else 0


    finished_product_ware_line_ids = fields.Many2many("finished_product_ware_line", string="仓库明细")
    quantity_put_storage = fields.Float(string="入库件数", compute="set_quantity_put_storage", store=True)

    @api.depends('finished_product_ware_line_ids', 'finished_product_ware_line_ids.state')
    def set_quantity_put_storage(self):
        for record in self:
            record.quantity_put_storage = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.state == "确认"\
            and x.quality == "合格" and x.character == "正常" and x.finished_product_ware_id.processing_type == "工厂").mapped('number'))


    dg_detail_ids = fields.Many2many("suspension_system_station_summary", "pps_dg_rel", string="吊挂")
    hang_number = fields.Integer(string="吊挂件数", compute="set_hang_number", store=True)
    @api.depends('dg_detail_ids', 'dg_detail_ids.total_quantity')
    def set_hang_number(self):
        for record in self:
            record.hang_number = sum(record.dg_detail_ids.mapped('total_quantity'))


    dg_rework_ids = fields.One2many("suspension_system_rework", "posterior_passage_statistical_id", string="吊挂返修")
    dg_rework_number = fields.Integer(string="吊挂返修件数", compute="set_dg_rework_number", store=True)
    @api.depends('dg_rework_ids', 'dg_rework_ids.number')
    def set_dg_rework_number(self):
        for record in self:
            record.dg_rework_number = sum(record.dg_rework_ids.mapped('number'))

    # 设置返修率
    @api.depends('repair_quantity', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_quantity:

                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100

                tem_assess_index = record.repair_quantity - record.check_quantity * 0.1
                if tem_assess_index < 0:

                    record.assess_index = 0

                else:

                    record.assess_index = tem_assess_index

            else:
                record.assess_index = 0
                record.repair_ratio = 0

    


    def set_day_qing_day_bi_ids(self):
        for record in self:
        
            day_qing_day_bi_objs = self.env["day_qing_day_bi"].sudo().search([("date", "=", record.dDate), ("group", "=", "后道"), ("style_number", "=", record.style_number.id)])
            if day_qing_day_bi_objs:

                record.day_qing_day_bi_ids = [(6, 0, day_qing_day_bi_objs.ids)]


    def set_finished_product_ware_line_ids(self):
        for record in self:

            finished_product_ware_line_objs = self.env["finished_product_ware_line"].sudo().search([("date", "=", record.dDate), ("style_number", "=", record.style_number.id)])

            if finished_product_ware_line_objs:

                record.finished_product_ware_line_ids = [(6, 0, finished_product_ware_line_objs.ids)]


    def set_suspension_system_station_summary_ids(self):

        for record in self:
            
            suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                ("dDate", "=", record.dDate),
                ("style_number", "=", record.style_number.id),
                ("employee_id.name", "=", record.general),
            ])
            if suspension_system_station_summary_objs:
                record.dg_detail_ids = [(6, 0, suspension_system_station_summary_objs.ids)]


    def set_dg_rework_ids(self):

        map_groups = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            "整件一组": "整件一组"
        }

        for record in self:

            if map_groups.get(record.group):
            
                suspension_system_rework_objs = self.env['suspension_system_rework'].sudo().search([
                    ("date", "=", record.dDate),
                    ("qc_employee_id.name", "=", record.general),
                    ("group.group", "=", map_groups[record.group]),
                    ('style_number', "=", record.style_number.id)
                ])
                if suspension_system_rework_objs:
                    for suspension_system_rework_obj in suspension_system_rework_objs:
                        suspension_system_rework_obj.posterior_passage_statistical_id = record.id
            


    @api.model
    def create(self, vals):

        res = super(PosteriorPassageStatistical, self).create(vals)

        # res.sudo().set_day_qing_day_bi_ids()
        # res.sudo().set_finished_product_ware_line_ids()
        res.sudo().set_suspension_system_station_summary_ids()
        # res.sudo().set_dg_rework_ids()

        return res



class PosteriorPassageStatisticalLine(models.Model):
    _name = 'pp_statistical_line'
    _description = '后道返修统计款号明细'
    _rec_name = "style_number"


    posterior_passage_statistical_id = fields.Many2one("posterior_passage_statistical", string="组返修统计")
    style_number = fields.Many2one("ib.detail", string="款号")