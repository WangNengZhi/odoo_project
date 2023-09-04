from odoo.exceptions import ValidationError

from odoo import models, fields, api



class efficiency(models.Model):
    _name = 'eff.eff'
    _description = '每人每天效率表'
    _order = "date desc"

    employee = fields.Many2one('hr.employee', string="员工")
    jobs = fields.Many2one("hr.job", string="岗位", compute="_value_info", store=True)
    work_type = fields.Char(string="工种", compute="_value_info", store=True)
    departure_date = fields.Date(string="离职时间", compute="_value_info", store=True)
    date = fields.Date(string='日期')
    group = fields.Char(string="组")
    totle_eff = fields.Float(string='总效率(%)', group_operator="avg")


    # 设置员工信息
    @api.depends('employee')
    def _value_info(self):
        for record in self:
            # 岗位
            record.jobs = record.employee.job_id.id
            # 工种
            record.work_type = record.employee.is_it_a_temporary_worker
            # 离职时间
            record.departure_date = record.employee.is_delete_date



    # 计算总效率
    def set_totle_eff(self):
        for record in self:

            on_work_objs = self.env["on.work"].sudo().search([
                ("date1", "=", record.date),
                ("employee", "=", record.employee.id)
            ])

            tem_totle_eff = 0
            for on_work_obj in on_work_objs:
                tem_totle_eff = tem_totle_eff + ((on_work_obj.standard_time * on_work_obj.over_number) / 396)

            record.totle_eff = tem_totle_eff


class efficiency_week(models.Model):
    _name = 'eff.eff.week'
    _description = '每人每周效率表'
    _order = "week desc"

    employee = fields.Many2one('hr.employee', string="员工")
    week = fields.Char(string="周")
    group = fields.Char(string="组")
    work_days = fields.Integer(string="工作天数")
    avg_totle_eff = fields.Float(string="平均效率(%)")
    totle_eff = fields.Float('总效率(%)')