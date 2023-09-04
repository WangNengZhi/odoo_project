from odoo import models, fields, api
from odoo.exceptions import ValidationError

class InvestInvest(models.Model):
    '''中查'''
    _inherit = 'invest.invest'

    def set_middle_check_missed_details(self):
        for record in self:

            middle_check_missed_details_objs = self.env["middle_check_missed_details"].sudo().search([
                ("date", ">=", record.date),
                ("group", "=", record.group),
                ("ib_detail_id", "=", record.style_number.id),
                ("middle_check_principal", "=", record.invest)
            ])
            if middle_check_missed_details_objs and middle_check_missed_details_objs.filtered(lambda x: x.date == record.date):
                pass

            else:
                today_record = middle_check_missed_details_objs.sudo().create({
                    "date": record.date,
                    "group": record.group,
                    "ib_detail_id": record.style_number.id,
                    "middle_check_principal": record.invest
                })
                middle_check_missed_details_objs = list(middle_check_missed_details_objs)
                middle_check_missed_details_objs.append(today_record)

            for obj in middle_check_missed_details_objs:
                obj.sudo().set_invest_invest_line_ids()     # 中查
                obj.sudo().set_general_general_line_ids()   # 总检


    @api.model
    def create(self, vals):

        res = super(InvestInvest, self).create(vals)

        res.sudo().set_middle_check_missed_details()

        return res


    def unlink(self):

        always_check_omission_details_obj_list = []
        for record in self:
            middle_check_missed_details_obj = self.env["middle_check_missed_details"].sudo().search([
                ("date", "=", record.date),
                ("group", "=", record.group),
                ("ib_detail_id", "=", record.style_number.id),
                ("middle_check_principal", "=", record.invest)
            ])

            always_check_omission_details_obj_list.append(middle_check_missed_details_obj)

        res = super(InvestInvest, self).unlink()


        for obj in always_check_omission_details_obj_list:
            obj.sudo().set_invest_invest_line_ids()

        return res



class GeneralGeneral(models.Model):
    '''总检'''
    _inherit = 'general.general'



    def set_middle_check_missed_details(self):
        for record in self:

            middle_check_missed_details_objs = self.env["middle_check_missed_details"].sudo().search([
                ("date", ">=", record.date),
                ("group", "=", record.group),
                ("ib_detail_id", "=", record.item_no.id),
                ("middle_check_principal", "=", record.invest)
            ])
            if middle_check_missed_details_objs and middle_check_missed_details_objs.filtered(lambda x: x.date == record.date):
                pass

            else:
                today_record = middle_check_missed_details_objs.sudo().create({
                    "date": record.date,
                    "group": record.group,
                    "ib_detail_id": record.item_no.id,
                    "middle_check_principal": record.invest
                })
                middle_check_missed_details_objs = list(middle_check_missed_details_objs)
                middle_check_missed_details_objs.append(today_record)

            for obj in middle_check_missed_details_objs:
                obj.sudo().set_general_general_line_ids()   # 总检
                obj.sudo().set_invest_invest_line_ids()     # 中查


    @api.model
    def create(self, vals):

        res = super(GeneralGeneral, self).create(vals)

        res.sudo().set_middle_check_missed_details()

        return res



    def unlink(self):

        always_check_omission_details_obj_list = []
        for record in self:
            middle_check_missed_details_obj = self.env["middle_check_missed_details"].sudo().search([
                ("date", "=", record.date),
                ("group", "=", record.group),
                ("ib_detail_id", "=", record.item_no.id),
                ("middle_check_principal", "=", record.invest)
            ])

            always_check_omission_details_obj_list.append(middle_check_missed_details_obj)

        res = super(GeneralGeneral, self).unlink()


        for obj in always_check_omission_details_obj_list:
            obj.sudo().set_general_general_info()

        return res



class product(models.Model):
    """ 继承组产值"""
    _inherit = 'pro.pro'


    def set_middle_check_missed_details_id(self):
        for record in self:
            middle_check_missed_details_objs = self.env['middle_check_missed_details'].sudo().search([("date", "=", record.date), ("group", "=", record.group), ("ib_detail_id", "=", record.style_number.id)])
            if middle_check_missed_details_objs:
                for middle_check_missed_details_obj in middle_check_missed_details_objs:
                    middle_check_missed_details_obj.pro_pro_ids = [(4, record.id)]


    @api.model
    def create(self, vals):

        res = super(product, self).create(vals)

        res.sudo().set_middle_check_missed_details_id()

        return res



class MiddleCheckMissedDetails(models.Model):
    _name = 'middle_check_missed_details'
    _description = '中查每日漏查(按款号)'
    _rec_name = 'ib_detail_id'
    _order = "date desc"


    date = fields.Date(string="日期")

    ib_detail_id = fields.Many2one("ib.detail", string="款号")

    group = fields.Char(string="组别")

    middle_check_principal = fields.Char(string="中查")


    general_general_line_ids = fields.Many2many("general.general", string="总检")
    def set_general_general_line_ids(self):
        for record in self:
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "<=", record.date),
                ("group", "=", record.group),
                ("item_no", "=", record.ib_detail_id.id),
                ("invest", "=", record.middle_check_principal),
                ("repair_type", "=", "车位返修"),
            ])
            record.general_general_line_ids = [(6, 0, general_general_objs.ids)]

    repair_quantity = fields.Float(string="当日返修数量(总检)", compute="set_general_general_info", store=True)
    intraday_always_check_quantity = fields.Float(string="当日总检数量(总检)", compute="set_general_general_info", store=True)
    intraday_repair_ratio = fields.Float(string="当日返修率", compute="set_intraday_repair_ratio", store=True)
    repair_value_sum = fields.Float(string="返修总数量(总检)", compute="set_general_general_info", store=True)
    @api.depends("general_general_line_ids")
    def set_general_general_info(self):
        for record in self:
            # 当日返修数量
            record.repair_quantity = sum(record.general_general_line_ids.filtered(lambda x: x.date == record.date).mapped('repair_number'))
            # 返修总数量
            record.repair_value_sum = sum(record.general_general_line_ids.mapped('repair_number'))
            # 当日总监数量
            record.intraday_always_check_quantity = sum(record.general_general_line_ids.filtered(lambda x: x.date == record.date).mapped('general_number'))


    invest_invest_line_ids = fields.Many2many("invest.invest", string="中查")
    def set_invest_invest_line_ids(self):
        for record in self:
            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", "<=", record.date),
                ("group", "=", record.group),
                ("style_number", "=", record.ib_detail_id.id),
                ("invest", "=", record.middle_check_principal)
            ])
            record.invest_invest_line_ids = [(6, 0, invest_invest_objs.ids)]
    check_quantity = fields.Float(string="查货总数量(中查)", compute="set_invest_invest_info", store=True)
    @api.depends("invest_invest_line_ids")
    def set_invest_invest_info(self):
        for record in self:
            
            record.check_quantity = sum(record.invest_invest_line_ids.mapped('check_the_quantity'))

    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)


    # 设置当日返修率
    @api.depends('repair_quantity', 'intraday_always_check_quantity')
    def set_intraday_repair_ratio(self):
        for record in self:
            if record.intraday_always_check_quantity:
                record.intraday_repair_ratio = (record.repair_quantity / record.intraday_always_check_quantity) * 100


    # 设置总返修率和考核
    @api.depends('repair_value_sum', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_quantity:
                record.repair_ratio = (record.repair_value_sum / record.check_quantity) * 100

                if record.repair_value_sum > (record.check_quantity * 0.03):

                    record.assess_index = record.repair_quantity * 2
                else:
                    record.assess_index = 0

            else:

                record.repair_ratio = 0
                record.assess_index = 0


    pro_pro_ids = fields.Many2many("pro.pro", string="组产值")
    deliveries_number = fields.Integer(string="组上交货件数", compute="set_deliveries_number", store=True)
    @api.depends('pro_pro_ids', 'pro_pro_ids.number')
    def set_deliveries_number(self):
        for record in self:
            record.deliveries_number = sum(record.pro_pro_ids.mapped("number"))


    dg_ids = fields.Many2many("suspension_system_station_summary",
        relation='mcmd_ssss',
        column1='middle_check_missed_details_id',
        column2='suspension_system_station_summary_id',
        string="吊挂")
    dg_group_number = fields.Integer(string="吊挂生产件数", compute="set_dg_group_number", store=True)
    @api.depends('dg_ids', 'dg_ids.total_quantity')
    def set_dg_group_number(self):
        for record in self:
            record.dg_group_number = sum(record.dg_ids.mapped("total_quantity"))


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



    def set_pro_pro_ids(self):
        ''' 设置组上交货记录'''
        for record in self:
            if record.date and record.group and record.ib_detail_id:

                pro_pro_objs = self.env['pro.pro'].sudo().search([
                    ("date", "=", record.date),
                    ("group", "=", record.group),
                    ("style_number", "=", record.ib_detail_id.id)
                ])
                if pro_pro_objs:
                    record.pro_pro_ids = [(6, 0, pro_pro_objs.ids)]


    def set_dg_ids(self):
        ''' 设置吊挂生产记录'''

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
            "整件一组": "整件一组",
        }

        for record in self:
            if record.date and record.ib_detail_id and record.group and record.middle_check_principal:

                check_position_settings_obj = self.env['check_position_settings'].sudo().search([
                    ("group", "=", map_groups.get(record.group)),
                    ("department_id", "=", "车间")
                ])

                emp_obj = self.env['hr.employee'].sudo().search([("name", "=", record.middle_check_principal)])

                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", "=", record.date),
                    ("group", "=", check_position_settings_obj.id),
                    ("employee_id", "=", emp_obj.id),
                    ("style_number", "=", record.ib_detail_id.id),
                    ("station_number", "in", check_position_settings_obj.mapped('position_line_ids.position'))
                ])

                if suspension_system_station_summary_objs:
                    record.dg_ids = [(6, 0, suspension_system_station_summary_objs.ids)]




    @api.model
    def create(self, vals):

        res = super(MiddleCheckMissedDetails, self).create(vals)

        res.sudo().set_dg_ids()

        res.sudo().set_pro_pro_ids()

        return res



