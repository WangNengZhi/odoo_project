from odoo import models, fields, api
import calendar, datetime


class MiddleCheckDayLeak(models.Model):
    _name = 'middle_check_day_leak'
    _description = '中查漏查表(日：按中查)'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期")
    group_line_ids = fields.One2many("day_leak_group_line", "middle_check_day_leak_id", string="组别")
    style_number_line_ids = fields.One2many("day_leak_style_number_line", "middle_check_day_leak_id", string="款号")
    middle_check_principal = fields.Char(string="中查")

    repair_quantity = fields.Float(string="当日返修数量(总检)")
    intraday_always_check_quantity = fields.Float(string="当日总检数量(总检)")
    intraday_repair_ratio = fields.Float(string="当日返修率", compute="set_intraday_repair_ratio", store=True)



    repair_value_sum = fields.Float(string="返修总数量(总检)")
    check_quantity = fields.Float(string="查货总数量(中查)")


    repair_ratio = fields.Float(string="总返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)



    # 设置当日返修率
    @api.depends('repair_quantity', 'intraday_always_check_quantity')
    def set_intraday_repair_ratio(self):
        for record in self:
            if record.intraday_always_check_quantity:
                record.intraday_repair_ratio = (record.repair_quantity / record.intraday_always_check_quantity) * 100


    # 设置返修率
    @api.depends('repair_quantity', 'repair_value_sum', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_value_sum and record.repair_quantity:
                # 返修率
                record.repair_ratio = (record.repair_value_sum / record.check_quantity) * 100

                if record.repair_value_sum > (record.check_quantity * 0.03):

                    record.assess_index = record.repair_quantity * 2
                else:
                    record.assess_index = 0

            else:

                record.repair_ratio = 0
                record.assess_index = 0



    # 设置中查漏查表数据
    def set_date(self):
        for record in self:
            
            record.group_line_ids.sudo().unlink()
            record.style_number_line_ids.sudo().unlink()

            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.date),
                ("invest", "=", record.middle_check_principal),
                ("repair_type", "=", "车位返修"),
            ])


            # 临时组别明细
            tem_group_line_ids = []
            # 临时款号明细
            tem_style_number_line_ids = []

            for general_general_obj in general_general_objs:

                tem_group_line_ids.append((0, 0, {"name": general_general_obj.group}))
                tem_style_number_line_ids.append((0, 0,{"name": general_general_obj.item_no.id}))




            record.group_line_ids = tem_group_line_ids
            record.style_number_line_ids = tem_style_number_line_ids


            # 临时查货数量
            tem_check_quantity = 0
            # 临时当日查货数
            tem_intraday_always_check_quantity = 0
            # 临时返修件数
            tem_repair_value = 0
            # 临时返修总数
            tem_repair_value_sum = 0
            
            for tem_obj in record.style_number_line_ids:

                general_general_objs = self.env["general.general"].sudo().search([
                    ("item_no", "=", tem_obj.name.id),
                    ("invest", "=", record.middle_check_principal),
                    ("date", "<=", record.date),
                    ("repair_type", "=", "车位返修"),
                ])
                for general_general_obj in general_general_objs:
                    tem_repair_value_sum = tem_repair_value_sum + general_general_obj.repair_number
                    if general_general_obj.date == record.date:
                        tem_repair_value = tem_repair_value + general_general_obj.repair_number
                        tem_intraday_always_check_quantity = tem_intraday_always_check_quantity + general_general_obj.general_number

                tem_general_general_objs = self.env["invest.invest"].sudo().search([
                    ("style_number", "=", tem_obj.name.id),
                    ("invest", "=", record.middle_check_principal),
                    ("date", "<=", record.date)
                ])
                for tem_obj in tem_general_general_objs:
                    tem_check_quantity = tem_check_quantity + tem_obj.check_the_quantity

            record.repair_quantity = tem_repair_value

            record.intraday_always_check_quantity = tem_intraday_always_check_quantity

            record.repair_value_sum = tem_repair_value_sum

            record.check_quantity = tem_check_quantity






class DayLeakGroupLine(models.Model):
    _name = 'day_leak_group_line'
    _description = '中查漏查组别明细'
    _order = "name"


    middle_check_day_leak_id = fields.Many2one("middle_check_day_leak")
    name = fields.Char(string="组名")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        day_leak_group_line_obj = self.env["day_leak_group_line"].sudo().search([
            ("middle_check_day_leak_id", "=", vals["middle_check_day_leak_id"]),
            ("name", "=", vals["name"]),
            ])
        if day_leak_group_line_obj:
            day_leak_group_line_obj.unlink()
            

        instance = super(DayLeakGroupLine, self).create(vals)
    
        return instance


class DayLeakStyleNumberLine(models.Model):

    _name = 'day_leak_style_number_line'
    _description = '中查漏查款号明细'
    _order = "name"

    middle_check_day_leak_id = fields.Many2one("middle_check_day_leak")
    name = fields.Many2one("ib.detail", string="款号")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        day_leak_style_number_line_obj = self.env["day_leak_style_number_line"].sudo().search([
            ("middle_check_day_leak_id", "=", vals["middle_check_day_leak_id"]),
            ("name", "=", vals["name"])
            ])
        if day_leak_style_number_line_obj:
            day_leak_style_number_line_obj.unlink()
            

        instance = super(DayLeakStyleNumberLine, self).create(vals)
    
        return instance
