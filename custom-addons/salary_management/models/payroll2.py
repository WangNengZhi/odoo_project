from odoo.exceptions import ValidationError
from odoo import models, fields, api


'''工资表'''


class salary(models.Model):
    _inherit = "payroll1"


    # 生成工资表
    def generate_salary_sheet(self):
        for record in self:

            state_list = self.mapped('state')
            if "未确认" in state_list or "有更改" in state_list:

                raise ValidationError("工资明细存在未确认或者有更改，请确认后再操作！")

            else:

                # 先查询一下工资表，有没有当前月份该员工的工资条，如果有则删除重新创建
                fsn_salary_sheet_obj = self.env["payroll2"].sudo().search([("month", "=", record.date), ("employee_id", "=", record.name.id)])

                if fsn_salary_sheet_obj:
                    fsn_salary_sheet_obj.sudo().unlink()

                self.env["payroll2"].sudo().create({
                    "payroll1_id": record.id,
                    "month": record.date,   # 月份
                    "employee_id": record.name.id,  # 员工
                    "is_delete_date": record.is_delete_date, #离职日期

                    "normal_working_days": record.should_attend,    # 应出勤天数
                    "clock_in_time": record.clock_in_time,
                    # clock_in_time = fields.Float(string='实出勤（天)')
                    "work_time" : record.work_time,
                    # work_time = fields.Float(string="在职时长(天)")
                    "regular_payroll": record.pay_now,  # 正常薪资

                    "performance_pay": record.performance_pay,      # 绩效工资
                    "recruitment_reward": record.recruitment_reward,      # 招聘奖金

                    "rent_allowance": record.rental_allowance,    # 租房津贴
                    "attendance_bonus": record.perfect_attendance_award,    # 全勤奖
                    "meal_allowance": record.meal_allowance,
                    # meal_allowance = fields.Float(string="饭补")
                    "job_allowance": record.job_allowance,  # 春节补贴

                    "rice_tonic": record.rice_tonic,    # 饭补扣款
                    "leave_days": record.leave_days,    # 事假时间
                    "sick_leave_days": record.sick_leave_days,  # 病假时间
                    "absenteeism_time": record.absenteeism_time,    # 旷工时间
                    "leave_deduction": record.leave_deduction,      # 事假扣款
                    "sick_leave_deduction": record.sick_leave_deduction,    # 病假扣款
                    "absenteeism_deduction": record.absenteeism_deduction,  # 旷工扣款


                    "be_late_time": record.be_late_time,    # 迟到早退时间
                    "late_arrival_and_early_refund_deduction": record.late_arrival_and_early_refund_deduction,  # 迟到早退扣款
                    "dormitory_water_and_electricity_deduction": record.dormitory_water_and_electricity_deduction,  # 宿舍水电扣款

                    "other_deductions": record.other_deductions,    # 其他扣款

                    "rent_deduction": record.rent_deduction,    # 房租扣款

                    "advance_salary": record.advanced,    # 预支工资

                    "salary_payable": record.salary_payable1,   # 应发工资1

                    "dimission_subsidy": record.dimission_subsidy,      # 离职补贴

                    "performance_bonus": record.performance_bonus,      # 绩效奖金
                    "commission_bonus": record.commission_bonus,    # 提成


                    "salary_payable2": record.salary_payable2,      # 应发工资2
    
                    "salary_payable3": record.salary_payable3,      # 应发工资3

                    "customer_subsidy": record.customer_subsidy,    # 客户补贴

                    "compensation": record.compensation,    # 赔偿

                    "paid_wages": record.paid_wages,    # 实发工资

                    "pension_individual": record.pension_individual,
                    "medical_personal": record.medical_personal,
                    "unemployed_individual": record.unemployed_individual,
                    "provident_fund_deduction": record.provident_fund_deduction,
                    "social_security_allowance": record.social_security_allowance,  # 社保津贴

                    "social_security_deductions": record.social_security_deductions,    # 社保扣款
                    "tax": record.tax,      # 个税
                })




class FsnSalarySheet(models.Model):
    _name = 'payroll2'
    _description = 'FSN工资表'

    payroll1_id = fields.Many2one("payroll1", string="工资明细")
    month = fields.Char(string='月份', required=True)
    employee_id = fields.Many2one('hr.employee', string='员工')

    first_level_department = fields.Many2one("hr.department", string="部门", compute="_set_emp_message", store=True)
    contract = fields.Selection([
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
    ], string='工种', compute="_set_emp_message", store=True)
    is_delete_date = fields.Date(string='离职日期')

    normal_working_days = fields.Float(string="正常工作天数")

    clock_in_time = fields.Float(string='实出勤（天)')
    work_time = fields.Float(string="在职时长(天)")

    regular_payroll = fields.Float(string="正常薪资")
    performance_pay = fields.Float('绩效工资')
    recruitment_reward = fields.Float(string="招聘奖金")

    rent_allowance = fields.Float(string="租房津贴")
    attendance_bonus = fields.Float(string="全勤奖")
    meal_allowance = fields.Float(string="饭补")
    job_allowance = fields.Float('春节补贴')

    rice_tonic = fields.Float(string='饭补扣款')

    leave_days = fields.Float(string='事假时间(时)')
    sick_leave_days = fields.Float(string='病假时间(时)')
    absenteeism_time = fields.Float(string='旷工时间（时)')
    leave_deduction = fields.Float(string='事假扣款')
    sick_leave_deduction = fields.Float(string='病假扣款')
    absenteeism_deduction = fields.Float(string="旷工扣款")

    be_late_time = fields.Float(string="迟到早退时间(分)")
    late_arrival_and_early_refund_deduction = fields.Float(string='迟到早退扣款')

    dormitory_water_and_electricity_deduction = fields.Float(string='宿舍水电扣款')

    other_deductions = fields.Float(string='绩效扣除')

    rent_deduction = fields.Float(string='房租扣款')

    advance_salary = fields.Float(string="预支工资")

    pension_individual = fields.Float('养老（个人)')
    medical_personal = fields.Float('医疗（个人）')
    unemployed_individual = fields.Float('失业（个人）')
    provident_fund_deduction = fields.Float('公积金扣款')
    social_security_allowance = fields.Float(string='社保津贴')
    social_security_deductions = fields.Float(string='社保扣款')
    tax = fields.Float(string='个税')

    salary_payable = fields.Float(string="应发工资1")

    dimission_subsidy = fields.Float(string="离职补贴")


    tax = fields.Float(string="个税")
    customer_subsidy = fields.Float(string="客户补贴")
    compensation = fields.Float(string="赔偿")

    performance_bonus = fields.Float(string="绩效奖金")

    commission_bonus = fields.Float(string="提成")

    salary_payable2 = fields.Float(string="应发工资2")

    rent_deduction = fields.Float(string='房租扣款')
    rice_tonic = fields.Float(string='饭补扣款')
    dormitory_water_and_electricity_deduction = fields.Float(string='宿舍水电扣款')
    advance_salary = fields.Float(string="预支工资")

    salary_payable3 = fields.Float(string="实发")

    paid_wages = fields.Float(string="实发2")


    # 设置员工信息
    @api.depends('employee_id')
    def _set_emp_message(self):
        for record in self:

            # 部门
            record.first_level_department = record.employee_id.department_id.id
            # 合同/工种
            record.contract = record.employee_id.is_it_a_temporary_worker

    is_grant = fields.Boolean(string="是否发放", related="payroll1_id.is_grant", store=True)