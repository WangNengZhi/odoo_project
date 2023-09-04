from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar, datetime

class MealSubsidyTopUp(models.Model):
    _name = 'meal_subsidy_top_up'
    _description = '餐补充值'
    _order = 'date desc'

    date = fields.Date(string='日期')
    name = fields.Many2one('hr.employee', string='姓名')
    department_id = fields.Many2one('hr.department', string='部门', compute="set_employee_messages", store=True)
    job_id = fields.Many2one('hr.job', string='岗位', compute="set_employee_messages", store=True)
    entry_time = fields.Date(string='入职时间', compute="set_employee_messages", store=True)
    identity_card = fields.Char(string="身份证号")
    attendance_day = fields.Float(string="出勤")
    unit_price = fields.Float(string="餐补")
    amount = fields.Float(string="金额")
    remarks = fields.Char(string="备注")



    # 计算月的第一天和最后一天
    def compute_start_and_end(self):

        if self.date:

            date_year = self.date.year
            date_month = self.date.month
            last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
            start = datetime.date(date_year, date_month, 1)
            end = datetime.date(date_year, date_month, last_day)

            return {"start": start, "end": end}



    @api.constrains('date', 'name')
    def _check_unique(self):

        for record in self:

            date_dict = record.compute_start_and_end()

            demo = self.env[self._name].sudo().search([
                ('name', '=', record.name.id),
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ])
            if len(demo) > 1:
                raise ValidationError(f"{record.name.name}的当月记录已经存在了！不可重复创建。")


    @api.depends('name')
    def set_employee_messages(self):
        for record in self:
            # 入职时间
            record.entry_time = record.name.entry_time
            # 部门
            record.department_id = record.name.department_id.id
            # 岗位
            record.job_id = record.name.job_id.id
            # 身份证号
            record.identity_card = record.name.id_card