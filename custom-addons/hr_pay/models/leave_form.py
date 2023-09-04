from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LeaveForm(models.Model):
    _name = 'leave.form'
    _description = '外出申请单'



    name = fields.Many2one('hr.employee', string='员工姓名', required=True)
    department_id = fields.Many2one('hr.department', compute="set_employee_messages", store=True, string='部门')
    application_time = fields.Date(string='申请日期', required=True)
    time_out = fields.Datetime(string='开始时间', required=True)
    time_end = fields.Datetime(string='结束时间', required=True)
    send_car = fields.Selection([
        ('需要', '需要'),
        ('不需要', '不需要'),
    ], string='是否派车', required=True)
    customer = fields.Char(string="客户")
    style_number = fields.Many2one('ib.detail', string='款号')
    number = fields.Integer(string="数量")
    job_content = fields.Text(string="工作内容")
    # personnel_registration = fields.Selection([
    #     ('已登记', '已登记'),
    #     ('未登记', '未登记'),
    # ], string='人事部是否登记')
    # immediate_superior = fields.Many2one('hr.employee', '直属上级')
    person_charge = fields.Many2one('hr.employee', '分管负责人')
    # general_manager = fields.Many2one('hr.employee', '总经理')
    # time_off = fields.Datetime('销假时间')
    # comment = fields.Char('备注外出/出差事由')

    @api.depends('name')
    def set_employee_messages(self):
        for record in self:
            self.department_id = self.name.department_id.id