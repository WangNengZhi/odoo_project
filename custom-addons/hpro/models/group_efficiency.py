from odoo.exceptions import ValidationError

from odoo import models, fields, api


class group_efficiency(models.Model):
    _name = "group.efficiency"
    _description = '每组每天效率表'
    _order = "date desc"

    date = fields.Date(string='日期')
    group = fields.Char(string="组")
    totle_eff = fields.Float(string='总效率(%)', group_operator="avg")


    # 计算总效率
    def set_totle_eff(self):
        for record in self:

            on_work_objs = self.env["on.work"].sudo().search([
                ("date1", "=", record.date),
                ("group", "=", record.group)
            ])

            tem_totle_eff = 0
            for on_work_obj in on_work_objs:
                tem_totle_eff = tem_totle_eff + ((on_work_obj.standard_time * on_work_obj.over_number) / 396)
            
            record.totle_eff = tem_totle_eff




class group_efficiency_week(models.Model):
    _name = "group.efficiency.week"
    _description = '每组每周效率表'
    _order = "week desc"

    week = fields.Char(string="周")
    group = fields.Char(string="组")
    work_days = fields.Integer(string="工作天数")
    avg_totle_eff = fields.Float(string="平均效率(%)")
    totle_eff = fields.Float('总效率(%)')