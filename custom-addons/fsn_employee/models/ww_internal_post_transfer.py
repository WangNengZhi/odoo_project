# -*- coding: utf-8 -*-
#               wwr
#           2021-10-16
import datetime
import calendar

from odoo.exceptions import ValidationError
from odoo import models, fields, api

class material_list(models.Model):
    _name = 'internal.post.transfer'
    _description = '内部调岗表'


    state = fields.Selection([('草稿', '草稿'), ('确认', '确认')], string="状态", default="草稿")
    
    name = fields.Many2one('hr.employee', string='员工姓名', required=True)
    entry_time = fields.Date(string='入职时间', compute="set_employee_messages", store=True)
    application_time = fields.Date(string='申请时间', required=True)

    department_id = fields.Many2one('hr.department', compute="set_employee_messages", string='原部门', store=True)
    raw_job_id = fields.Many2one('hr.job', string='原岗位', compute="set_employee_messages", store=True)

    proposed_department = fields.Many2one('hr.department', string='部门', required=True)
    job_id = fields.Many2one('hr.job', string='岗位', required=True)

    adjust_salary = fields.Boolean(string='是否调整工资')
    before_pay = fields.Float(string="当前薪资", compute="set_employee_messages", store=True)
    before_post_commission = fields.Float(string="当前绩效奖金", compute="set_employee_messages", store=True)

    the_salary_adjustment_scheme = fields.Float(string='调整工资方案为')
    after_post_commission = fields.Float(string="之后绩效奖金")

    begin_start = fields.Date(string='开始执行日期', required=True)

    is_temporary_worker = fields.Boolean(string='是否调整工种')

    is_it_a_temporary_worker = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生', '实习生'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], compute="set_employee_messages", string='原工种', store=True)

    after_temporary_worker = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生', '实习生'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], string='调整之后的工种')


    # 设置当前薪资
    @api.depends('name')
    def set_employee_messages(self):
        for record in self:
            # 入职时间
            record.entry_time = record.name.entry_time
            # 部门
            record.department_id = record.name.department_id.id
            # 原岗位
            record.raw_job_id = record.name.job_id.id
            # 原薪资
            record.before_pay = record.name.fixed_salary
            # 原工种
            record.is_it_a_temporary_worker = record.name.is_it_a_temporary_worker
            # 原绩效奖金
            record.before_post_commission = record.name.performance_money


    # 确认
    def action_affirm(self):
        
        self.state = "确认"

    
    def rollback(self):
        self.state = "草稿"




    @api.model
    def create(self, vals):

        res = super(material_list, self).create(vals)


        return res




    def write(self, vals):

        

        if self.state == "确认":
            if "state" not in vals and len(vals) != 1:
                raise ValidationError(f"该调岗已经确认，不可修改!")

        res = super(material_list, self).write(vals)


        return res



    def unlink(self):

        if self.state == "确认":
            raise ValidationError(f"该调岗已经确认，不可删除!")

        res = super(material_list, self).unlink()

        return res
            


    def sync_emp_info(self, today):
        ''' 同步调岗员工信息'''

        twenty_day = datetime.date(today.year, today.month, 20)

        first_day = datetime.date(today.year, today.month, 1)

        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])     # 当月最后一天

        if twenty_day <= today <= last_day:

            internal_post_transfer_objs = self.env['internal.post.transfer'].sudo().search([
                ("begin_start", ">=", first_day),
                ("begin_start", "<=", last_day),
                ("state", "=", "确认"),
            ])

            for internal_post_transfer_obj in internal_post_transfer_objs:

                # 岗位
                internal_post_transfer_obj.name.job_id = internal_post_transfer_obj.job_id.id
                # 部门
                internal_post_transfer_obj.name.department_id = internal_post_transfer_obj.proposed_department.id

                # 是否调整薪资
                if internal_post_transfer_obj.adjust_salary:
                    internal_post_transfer_obj.name.fixed_salary = internal_post_transfer_obj.the_salary_adjustment_scheme
                    internal_post_transfer_obj.name.performance_money = internal_post_transfer_obj.after_post_commission

                # 是否工种
                if internal_post_transfer_obj.is_temporary_worker:
                    internal_post_transfer_obj.name.is_it_a_temporary_worker = internal_post_transfer_obj.after_temporary_worker





