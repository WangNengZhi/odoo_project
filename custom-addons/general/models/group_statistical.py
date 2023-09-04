
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class Invest(models.Model):
    """ 继承中查"""
    _inherit = 'invest.invest'

    group_statistical_id = fields.Many2one("group_statistical", string="组返修统计")


    def set_group_statistical(self):
        for record in self:
            group_statistical_obj = self.env["group_statistical"].sudo().search([
                ("dDate", "=", record.date),
                ("group", "=", record.group),
                ("invest", "=", record.invest),
                ("style_number", "=", record.style_number.id)
            ])
            if not group_statistical_obj:

                group_statistical_obj = self.env["group_statistical"].sudo().create({
                    "dDate": record.date,
                    "group": record.group,
                    "invest": record.invest,
                    "style_number": record.style_number.id
                })
            
            record.group_statistical_id = group_statistical_obj.id

    @api.model
    def create(self, vals):

        res = super(Invest, self).create(vals)

        res.sudo().set_group_statistical()

        return res

class DayQingDayBi(models.Model):
    """ 继承日清日毕"""
    _inherit = 'day_qing_day_bi'


    group_statistical_id = fields.Many2one("group_statistical", string="组返修统计")


class SuspensionSystemStationSummary(models.Model):
    """ 继承吊挂产量汇总"""
    _inherit = 'suspension_system_station_summary'


    group_statistical_id = fields.Many2one("group_statistical", string="组返修统计")


    def set_group_statistical(self):

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
                if record.group.department_id == "车间" and\
                    record.station_number in record.group.position_line_ids.mapped("position") and\
                        record.style_number and record.employee_id:
                    group_statistical_obj = self.env['group_statistical'].sudo().search([
                        ("dDate", "=", record.dDate),
                        ("group", "=", map_groups[record.group.group]),
                        ("invest", "=", record.employee_id.name),
                        ("style_number", "=", record.style_number.id)
                    ])
                    if not group_statistical_obj:
                        
                        group_statistical_obj = self.env['group_statistical'].sudo().create({
                            "dDate": record.dDate,
                            "group": map_groups[record.group.group],
                            "invest": record.employee_id.name,
                            "style_number": record.style_number.id
                        })
                    record.group_statistical_id = group_statistical_obj.id
            except Exception as e:
                _logger.info(e)

    @api.model
    def create(self, vals):

        res = super(SuspensionSystemStationSummary, self).create(vals)

        res.sudo().set_group_statistical()

        return res



class product(models.Model):
    """ 继承组产值"""
    _inherit = 'pro.pro'


    group_statistical_id = fields.Many2one("group_statistical", string="组返修统计")

    def set_group_statistical_id(self):
        for record in self:
            group_statistical_objs = self.env['group_statistical'].sudo().search([("dDate", "=", record.date), ("group", "=", record.group), ("style_number", "=", record.style_number.id)])
            if group_statistical_objs:
                for group_statistical_obj in group_statistical_objs:
                    record.group_statistical_id = group_statistical_obj.id

    @api.model
    def create(self, vals):

        res = super(product, self).create(vals)

        res.sudo().set_group_statistical_id()

        return res



class GroupStatistical(models.Model):
    _name = 'group_statistical'
    _description = '组返修统计'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    group = fields.Char(string="组别")
    invest = fields.Char(string='中查')
    group_statistical_style_number = fields.One2many("group_statistical_style_number", "group_statistical_id", string="款号明细", compute="_set_hang_the_stranded", store=True)
    style_number = fields.Many2one('ib.detail', string='款号')


    invest_invest_ids = fields.One2many("invest.invest", "group_statistical_id", string="中查")
    repair_quantity = fields.Integer(string='返修数量', compute="_set_invest_invest_info", store=True)
    check_quantity = fields.Integer(string='查货数量', compute="_set_invest_invest_info", store=True)
    group_secondary_repair_number = fields.Integer(string="小组二次返修数", compute="_set_invest_invest_info", store=True)
    group_secondary_check_number = fields.Integer(string="小组二次返修查货数", compute="_set_invest_invest_info", store=True)
    @api.depends('invest_invest_ids',\
        'invest_invest_ids.repairs_number',\
            'invest_invest_ids.check_the_quantity',\
                'invest_invest_ids.group_secondary_repair_number',\
                    'invest_invest_ids.group_secondary_check_number')
    def _set_invest_invest_info(self):
        for record in self:

            record.repair_quantity = sum(record.invest_invest_ids.mapped('repairs_number'))
            record.check_quantity = sum(record.invest_invest_ids.mapped('check_the_quantity'))
            record.group_secondary_repair_number = sum(record.invest_invest_ids.mapped('group_secondary_repair_number'))
            record.group_secondary_check_number = sum(record.invest_invest_ids.mapped('group_secondary_check_number'))


    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)



    day_qing_day_bi_ids = fields.One2many("day_qing_day_bi", "group_statistical_id", string="日清日毕")
    dg_number = fields.Float(string="吊挂件数", compute="_set_hang_the_stranded", store=True)
    hang_the_stranded = fields.Float(string="吊挂滞留", compute="_set_hang_the_stranded", store=True)
    repair_ratio_a = fields.Float(string="返修率（件）", compute="_set_hang_the_stranded", store=True, group_operator='avg')

    @api.depends('day_qing_day_bi_ids', 'day_qing_day_bi_ids.stranded_number', 'day_qing_day_bi_ids.dg_number')
    def _set_hang_the_stranded(self):
        for record in self:

            record.dg_number = sum(record.day_qing_day_bi_ids.mapped('dg_number'))
        
            record.hang_the_stranded = sum(record.day_qing_day_bi_ids.mapped('stranded_number'))

            record.repair_ratio_a = record.hang_the_stranded / record.dg_number if record.dg_number else 0

    dg_ids = fields.One2many("suspension_system_station_summary", "group_statistical_id", string="吊挂")
    dg_group_number = fields.Integer(string="吊挂件数", compute="set_dg_group_number", store=True)
    @api.depends('dg_ids', 'dg_ids.total_quantity')
    def set_dg_group_number(self):
        for record in self:

            record.dg_group_number = sum(record.dg_ids.mapped("total_quantity"))

    pro_pro_ids = fields.One2many("pro.pro", "group_statistical_id", string="组产值")
    deliveries_number = fields.Integer(string="组上交货件数", compute="set_deliveries_number", store=True)
    @api.depends('pro_pro_ids', 'pro_pro_ids.number')
    def set_deliveries_number(self):
        for record in self:
            record.deliveries_number = sum(record.pro_pro_ids.mapped("number"))
    
    auto_repair_number = fields.Integer(string="返修件数（自动）", compute="set_auto_repair_number", store=True)
    @api.depends('dg_group_number', 'deliveries_number')
    def set_auto_repair_number(self):
        for record in self:
            auto_repair_number = record.dg_group_number - record.deliveries_number
            if auto_repair_number > 0:
                record.auto_repair_number = auto_repair_number
            else:
                record.auto_repair_number = 0
    
    auto_repair_ratio = fields.Float(string="返修率（自动）", compute="set_auto_repair_ratio", store=True)
    @api.depends('dg_group_number', 'auto_repair_number')
    def set_auto_repair_ratio(self):
        for record in self:
            if record.dg_group_number:
                record.auto_repair_ratio = record.auto_repair_number / record.dg_group_number
            else:
                record.auto_repair_ratio = 0



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


    @api.model
    def create(self, vals):

        res = super(GroupStatistical, self).create(vals)

        return res


class GroupStatisticalStyleNumber(models.Model):
    _name = 'group_statistical_style_number'
    _description = '组返修统计款号明细'
    _rec_name = "style_number"


    group_statistical_id = fields.Many2one("group_statistical", string="组返修统计")
    style_number = fields.Many2one("ib.detail", string="款号")


