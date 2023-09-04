
from odoo.exceptions import ValidationError
from odoo import models, fields, api


import datetime
import calendar


class BecomeFullMember(models.Model):
    _name = 'become_full_member'
    _description = '转正记录单'
    _rec_name='employee_id'
    _order = "turn_positive_date desc"


    state = fields.Selection([('草稿', '草稿'), ('确认', '确认')], string="状态", default="草稿")

    employee_id = fields.Many2one('hr.employee', string='员工')
    age = fields.Integer(string="年龄", compute="set_employee_messages", store=True)
    education_background = fields.Char(string="学历", compute="set_employee_messages", store=True)
    department_id = fields.Many2one('hr.department', compute="set_employee_messages", store=True, string='部门')
    job_id = fields.Many2one('hr.job', compute="set_employee_messages", store=True, string='岗位')
    # probation_period_time = fields.Float(string="试用期时长(月)")
    probation_period_treatment = fields.Float(string="试用期薪资", compute="set_employee_messages", store=True)
    before_performance = fields.Float(string="试用期绩效", compute="set_employee_messages", store=True)
    entry_date = fields.Date(string="入职日期", compute="set_employee_messages", store=True)
    turn_positive_date = fields.Date(string="转正日期", compute="set_employee_messages", store=True)

    after_pay = fields.Float(string="转正之后薪资")
    after_performance = fields.Float(string="转正之后绩效")

    department_manager = fields.Many2one('hr.employee', string='部门主管签字')
    factory_manager = fields.Many2one('hr.employee', string='厂长签字')
    general_manager = fields.Many2one('hr.employee', string='总经理签字')


    # 检查员工转正次数，一个员工只能转正一次
    @api.constrains('employee_id')
    def _check_employee_id(self):

        for record in self:

            demo = self.env[record._name].sudo().search([
                ("employee_id", "=", record.employee_id.id),
                ])
            if len(demo) > 1:
                raise ValidationError(f"每个员工只能转正一次!")

    # 设置当前薪资
    @api.depends('employee_id')
    def set_employee_messages(self):
        for record in self:
            # 试用期薪资
            record.probation_period_treatment = record.employee_id.fixed_salary
            # 学历
            record.education_background = record.employee_id.education1
            # 年龄
            record.age = record.employee_id.age
            # 部门
            record.department_id = record.employee_id.department_id.id
            # 岗位
            record.job_id = record.employee_id.job_id.id
            # 入职日期
            record.entry_date = record.employee_id.entry_time
            # 转正日期
            record.turn_positive_date = record.employee_id.turn_positive_time
            # 试用期绩效
            record.before_performance = record.employee_id.performance_money


    # 确认
    def action_affirm(self):

        if self.general_manager:

            # self.employee_id.fixed_salary = self.after_pay
            self.state = "确认"
        
        else:
            raise ValidationError(f"不满足！确认条件，无法确认。请检查是否有领导签字！")

    @api.model
    def create(self, vals):

        res = super(BecomeFullMember, self).create(vals)


        return res




    def write(self, vals):

        if self.state == "确认":
            raise ValidationError(f"该转正已经确认，不可修改!")

        res = super(BecomeFullMember, self).write(vals)


        return res



    def unlink(self):

        if self.state == "确认":
            raise ValidationError(f"该转正已经确认，不可删除!")

        res = super(BecomeFullMember, self).unlink()

        return res



    def sync_emp_info(self, today):
        ''' 同步调岗员工信息'''

        twenty_day = datetime.date(today.year, today.month, 20)

        first_day = datetime.date(today.year, today.month, 1)

        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])     # 当月最后一天

        if twenty_day <= today <= last_day:

            become_full_member_objs = self.env['become_full_member'].sudo().search([
                ("turn_positive_date", ">=", first_day),
                ("turn_positive_date", "<=", last_day),
                ("state", "<=", "确认"),
            ])

            for become_full_member_obj in become_full_member_objs:

                become_full_member_obj.employee_id.fixed_salary = become_full_member_obj.after_pay


            
    

