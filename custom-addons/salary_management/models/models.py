# -*- coding: utf-8 -*-
import datetime
import calendar
from re import template
import time
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class salary(models.Model):
    _name = 'salary'
    _inherit = ['mail.thread']
    _description = '薪酬管理'

    date = fields.Char(string='月份', required=True, track_visibility='onchange')
    serial_number = fields.Integer('序号')
    name = fields.Many2one('hr.employee', string='姓名', track_visibility='onchange')
    id_card = fields.Char(string="身份证号", compute="_set_emp_message", store=True, track_visibility='onchange')
    first_level_department = fields.Many2one("hr.department", string="部门", compute="_set_emp_message", store=True, track_visibility='onchange')

    secondary_department = fields.Char(string='二级部门', compute="_set_emp_message", store=True, track_visibility='onchange')
    department_position = fields.Char(string='岗位(旧)')
    job_id = fields.Many2one('hr.job', string='岗位', compute="_set_emp_message", store=True, track_visibility='onchange')
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
    ], string='工种', compute="_set_emp_message", store=True, track_visibility='onchange')
    time_plan = fields.Selection([
        ('8:00 - 21:00, 单休', '8:00 - 21:00, 单休'),
        ('9:00 - 18:00, 单休', '9:00 - 18:00, 单休'),
        ('9:00 - 18:00, 大小休', '9:00 - 18:00, 大小休'),
        ('9:00 - 18:00, 双休', '9:00 - 18:00, 双休'),
        ('8:00 - 18:00, 单休', '8:00 - 18:00, 单休'),
        ('7:30 - 17:00, 单休', '7:30 - 17:00, 单休'),
        ('8:00 - 19:00, 单休', '8:00 - 19:00, 单休'),
    ], string='上下班时间', compute="_set_emp_message", store=True, track_visibility='onchange')
    entry_time = fields.Date(string='入职日期', compute="_set_emp_message", store=True, track_visibility='onchange')
    turn_positive_time = fields.Date(string='转正时间', compute="_set_emp_message", store=True, track_visibility='onchange')
    is_delete_date = fields.Date(string='离职日期', compute="_set_emp_message", store=True, track_visibility='onchange')

    # 设置员工信息
    @api.depends('name')
    def _set_emp_message(self):
        for record in self:
            # 身份证号
            record.id_card = record.name.id_card
            # 部门
            record.first_level_department = record.name.department_id.id
            # 二级部门
            record.secondary_department = record.name.second_dapartment
            # 岗位
            record.job_id = record.name.job_id.id
            # 合同/工种
            record.contract = record.name.is_it_a_temporary_worker
            # 出勤类型
            record.time_plan = record.name.time_plan
            # 入职日期
            record.entry_time = record.name.entry_time
            # 转正实际
            record.turn_positive_time = record.name.turn_positive_time
            # 离职日期
            record.is_delete_date = record.name.is_delete_date


    should_attend = fields.Float(string='应出勤(天)', track_visibility='onchange')
    should_attend_hours = fields.Float(string="应出勤(时)", compute='set_should_attend_hours', store=True, track_visibility='onchange')

    leave_days = fields.Float(string='事假(时)', track_visibility='onchange')
    sick_leave_days = fields.Float(string='病假(时)', track_visibility='onchange')
    absenteeism_time = fields.Float(string='旷工（时)', track_visibility='onchange')
    matter_days = fields.Float(string="事假(天)", track_visibility='onchange')
    disease_days = fields.Float(string="病假(天)", track_visibility='onchange')
    absenteeism_days = fields.Float(string="旷工(天)", track_visibility='onchange')

    clock_in_time = fields.Float(string='实出勤（天)', track_visibility='onchange')
    rest_time = fields.Float(string='休息时间(天)', track_visibility='onchange')
    actual_attendance = fields.Float(string='实出勤(时)', track_visibility='onchange')
    work_time = fields.Float(string="在职时长(天)", track_visibility='onchange')
    number_of_people = fields.Integer('人数')
    whether_to_turn_positive = fields.Boolean(string='是否转正', compute='_dormitory_depends', store=True, track_visibility='onchange')
    salary_type = fields.Char('工资类型', track_visibility='onchange')
    pay_now = fields.Float(string='正常薪资', track_visibility='onchange')
    performance_pay = fields.Float('绩效工资', track_visibility='onchange')
    recruitment_reward = fields.Float(string="招聘奖金", track_visibility='onchange')
    basic_wage = fields.Float('基本工资', track_visibility='onchange')
    job_allowance = fields.Float('春节补贴', track_visibility='onchange')
    meal_allowance = fields.Float(string="饭补", track_visibility='onchange')
    rice_tonic = fields.Float(string='饭补扣款', track_visibility='onchange')
    rice_tonic1 = fields.Float(string='饭补(减去)', track_visibility='onchange')
    overtime_pay = fields.Float('加班工资', track_visibility='onchange')
    overtime_allowance = fields.Float('加班补贴', track_visibility='onchange')
    social_security_allowance = fields.Float('社保津贴', track_visibility='onchange')
    rental_allowance = fields.Float(string='租房津贴', track_visibility='onchange')
    seniority_award = fields.Float('工龄奖', track_visibility='onchange')
    # fixed_part = fields.Float(string='正常薪资')
    # performance_amount = fields.Float('绩效金额')
    performance_ratio = fields.Float('绩效比例', track_visibility='onchange')
    performance_worker = fields.Float('应发绩效工', track_visibility='onchange')
    perfect_attendance_award = fields.Float('全勤奖', track_visibility='onchange')
    resident_subsidy = fields.Float('外住补贴', track_visibility='onchange')
    high_temperature_subsidy_or_other = fields.Float('高温补贴或其他', track_visibility='onchange')
    leave_deduction = fields.Float('事假扣款', track_visibility='onchange')
    sick_leave_deduction = fields.Float('病假扣款', track_visibility='onchange')
    absenteeism_deduction = fields.Float(string="旷工扣款", track_visibility='onchange')
    be_late_time = fields.Float(string="迟到早退分钟数", track_visibility='onchange')
    late_arrival_and_early_refund_deduction = fields.Float('迟到早退扣款', track_visibility='onchange')
    dormitory_water_and_electricity_deduction = fields.Float('宿舍水电扣款', track_visibility='onchange')
    other_deductions = fields.Float('其他扣款', track_visibility='onchange')
    blue_collar_apartment_dormitory_deposit_deduction = fields.Float('宿舍押金扣款', track_visibility='onchange')
    rent_deduction = fields.Float('房租扣款', track_visibility='onchange')
    # deductions_for_meals = fields.Float('餐费扣款')
    advanced = fields.Float('已预支', track_visibility='onchange')


    pension_individual = fields.Float('养老（个人)', track_visibility='onchange')
    medical_personal = fields.Float('医疗（个人）', track_visibility='onchange')
    unemployed_individual = fields.Float('失业（个人）', track_visibility='onchange')
    provident_fund_deduction = fields.Float('公积金扣款', track_visibility='onchange')


    salary_payable1 = fields.Float(string='应发工资1', compute='set_salary_payable1', store=True, digits=[12, 2], track_visibility='onchange')


    dimission_subsidy = fields.Float(string="离职补贴", track_visibility='onchange')
    month_workpiece_ratio = fields.Float(string="自动月平均效率(%)", track_visibility='onchange')
    manual_month_workpiece_ratio = fields.Float(string="手工月平均效率(%)", track_visibility='onchange')
    customer_subsidy = fields.Float('客户补贴', groups='salary_management.kehubutie', track_visibility='onchange')
    salary_payable2 = fields.Float(string='应发工资2', compute='set_salary_payable2', store=True, digits=[12, 2], track_visibility='onchange')
    day_average_salary = fields.Float(string="日均工资", compute='set_day_average_salary', store=True)

    # 计算日平均工资（实出勤天数，应发工资2）
    @api.depends('clock_in_time', 'salary_payable2')
    def set_day_average_salary(self):
        for record in self:
            if record.clock_in_time:
                record.day_average_salary = record.salary_payable2 / record.clock_in_time

    social_security_deductions = fields.Float('社保扣款', track_visibility='onchange')
    tax = fields.Float('个税', track_visibility='onchange')
    paid_wages = fields.Float(string='实发工资', compute='set_paid_wages', store=True, digits=[12, 2], track_visibility='onchange')


    state = fields.Selection([('已确认','已确认'), ('未确认','未确认'), ('有更改', '有更改')], string='状态', default="未确认", track_visibility='onchange')
    confirm_date = fields.Datetime(string="确认日期", track_visibility='onchange')


    def set_confirm(self):
        for record in self:
            record.write({
                "state": "已确认",
                "confirm_date": fields.Datetime.now()
            })
    
    # 判断更改
    def judge_change(self):

        date_list = self.message_ids.mapped('date')

        if date_list and self.confirm_date:
            max_change_date = max(date_list)
            # print(max_change_date, self.confirm_date)
            if max_change_date >= self.confirm_date:
                self.state = "有更改"




    def write(self, vals):

        res = super(salary, self).write(vals)

        if "state" in vals and len(vals) == 1:
            pass
        else:
            self.judge_change()

        return res


    # 设置预支工资
    def set_advanced(self):
        for record in self:
            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            # return {"begin": date_end, "end": date_end_of_the_month6}
            this_month["begin"]     # 当月第一天
            this_month["end"]   # 当月最后一天
            # 查询预支工资
            advance_of_wages_objs = self.env["advance_of_wages"].sudo().search([
                ("employee_id", "=", record.name.id),
                ("dDate", ">=", this_month["begin"]),
                ("dDate", "<=", this_month["end"]),
                ("approve_state", "=", "已审批"),
                ("wages_type", "!=", "补发"),
            ])
            tem_advanced = 0
            for advance_of_wages_obj in advance_of_wages_objs:
                tem_advanced = tem_advanced + advance_of_wages_obj.money



            this_month = record.set_begin_and_end()
            last_day = this_month["end"]     # 当月最后一天
            first_day = this_month["begin"]      # 当月第一天

            # 查询饭卡充值记录
            meal_subsidy_top_up_obj = self.env["meal_subsidy_top_up"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("name", "=", record.name.id)
            ])

            if meal_subsidy_top_up_obj:

                # 已预支
                record.advanced = tem_advanced + meal_subsidy_top_up_obj.amount

            else:
                # 已预支
                record.advanced = tem_advanced



    # 计算应出勤小时数
    @api.depends('should_attend')
    def set_should_attend_hours(self):

        # 计算小时
        def t2s(t):
            h, m, s = str(t).strip().split(":")
            return int(h) + int(m) / 60 + int(s) / 3600

        for record in self:

            if record.name.time_plan:

                work_time = record.name.time_plan
                work_time_end = work_time.split(',')[0].split('-')[1].strip()
                work_time_begin = work_time.split(',')[0].split('-')[0].strip()
                new_work_time_end = datetime.datetime.strptime(work_time_end, '%H:%M')
                new_work_time_begin = datetime.datetime.strptime(work_time_begin, '%H:%M')
                last_work_time = new_work_time_end - new_work_time_begin
                last_work_time = t2s(last_work_time)

                record.should_attend_hours = last_work_time * record.should_attend



    # 计算在职天数
    def be_on_the_job_days(self, entry_date, dimission_date, this_month_first_day, this_month_last_day):
        # print(type(entry_date), type(dimission_date), type(this_month_first_day), type(this_month_last_day))
        # entry_date = datetime.combine(entry_date,time())
        # dimission_date = datetime.combine(dimission_date,time())
        # this_month_first_day = datetime.combine(this_month_first_day,time())
        # this_month_last_day = datetime.combine(this_month_last_day,time())

        tem_work_time = 0

        # 如果当月之前入职的
        if entry_date < this_month_first_day:
            # 如果离职了
            if dimission_date:
                # 离职日期大于当月最后一天
                if dimission_date > this_month_last_day:
                    tem_work_time = this_month_last_day.day
                else:
                    tem_work_time = dimission_date.day - 1
            else:
                tem_work_time = this_month_last_day.day
        else:
            # 如果离职了
            if dimission_date:
                # 离职日期大于当月最后一天
                if dimission_date > this_month_last_day:
                    tem_work_time = (this_month_last_day - entry_date).days + 1
                else:
                    tem_work_time = (dimission_date - entry_date).days
            else:
                tem_work_time = (this_month_last_day - entry_date).days + 1

        self.work_time = tem_work_time

        return tem_work_time





    # 计算应发工资1 = 正常薪资 + 租房津贴 + 春节补贴 + 全勤奖 + 饭补 + 招聘奖金 - （事假扣款 + 病假扣款 + 其他扣款 + 迟到早退扣款 + 宿舍水电物业费 + 宿舍房租扣款 + 旷工扣款) - 已预支
    @api.depends('pay_now', 'rental_allowance', 'perfect_attendance_award', 'job_allowance', 'rice_tonic', 'leave_deduction', 'sick_leave_deduction', 'other_deductions', 'late_arrival_and_early_refund_deduction', 'dormitory_water_and_electricity_deduction', 'rent_deduction', 'advanced')
    def set_salary_payable1(self):
        for record in self:
            # 津贴 = 租房津贴 + 全勤奖 + 春节补贴 + 招聘奖金
            allowance = record.rental_allowance + record.perfect_attendance_award + record.meal_allowance + record.job_allowance + record.recruitment_reward
            # 扣款 = 饭补扣款 + 事假扣款 + 病假扣款 + 其他扣款 + 迟到早退扣款 + 宿舍水电物业费 + 宿舍房租扣款 + 旷工扣款
            deduct_money = record.rice_tonic + record.leave_deduction + record.sick_leave_deduction + record.other_deductions + record.late_arrival_and_early_refund_deduction + record.dormitory_water_and_electricity_deduction + record.rent_deduction + record.absenteeism_deduction

            # 应发工资1 = 正常薪资 + 津贴 + 绩效工资 - 扣款 - 已预支
            record.salary_payable1 = record.pay_now + allowance + record.performance_pay - deduct_money - record.advanced





    # 计算应发工资2 = 应该发工资1 + 客户补贴
    @api.depends('salary_payable1', 'customer_subsidy')
    def set_salary_payable2(self):
        for record in self:
            # 如果离职了
            if record.name.is_delete:

                # 查询扣款设置里面的离职补贴设置
                deduct_money_setting_obj = self.env["deduct_money_setting"].sudo().search([("month", "=", record.date)])
                # 如果扣款设置里面设置了离职补贴
                if deduct_money_setting_obj.is_dimission_subsidy:
                    # 并且离职日期在当月
                    if record.date == f"{record.name.is_delete_date.year}-{'%02d' % record.name.is_delete_date.month}":
                        # 并且离职性质为“急辞”
                        if record.name.dimission_nature == "急辞":

                            if (record.salary_payable1 * 0.3) > 0:
                                # 离职补贴
                                record.dimission_subsidy = -(record.salary_payable1 * 0.3)
                            else:
                                # 离职补贴
                                record.dimission_subsidy = (record.salary_payable1 * 0.3)


            # 应发工资2 = 应发工资1 + 客户补贴 + 离职补贴
            record.salary_payable2 = record.salary_payable1 + record.customer_subsidy + record.dimission_subsidy


    # 计算实发工资 = 应发工资2 - （社保扣款 + 个税）
    @api.depends('salary_payable2', 'social_security_deductions', 'tax')
    def set_paid_wages(self):
        for record in self:

            record.paid_wages = record.salary_payable2 - (record.social_security_deductions + record.tax)




    # 获取当月第一天和最后一天
    def set_begin_and_end(self):

        for record in self:

            date = str(record.date)
            date2 = date.split('-')
            year = date2[0]
            month = date2[1]
            day = 1
            date_pinjie = year + '-' + month + '-' + str(day)

            #    这就是年月的算法，返回本月天数
            month_math = calendar.monthrange(int(year), int(month))[1]

            #  本月的最大时间
            date_end_of_the_month5 = year + '-' + str(month) + '-' + str(month_math)
            date_end_of_the_month6 = datetime.datetime.strptime(date_end_of_the_month5, '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

            date_end = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')      # 当月第一天

            return {"begin": date_end, "end": date_end_of_the_month6}


    # 社保刷新
    def social_security_refresh(self):
        #  从员工里判断要不要交社保
        #
        for record in self:

            demo = self.env['socail.base'].sudo().search([])
            ids = []
            for i in demo:
                ids.append(i.id)
            max_id = max(ids)
            demo1 = self.env['socail.base'].sudo().search([('id', '=', max_id)])

            # 如果员工里面勾选了交社保
            if record.name.is_social_security == "交":
                # 判断员工有离职日期，如果离职时间大于最后一天则交社保
                if record.is_delete_date:

                    # 获取当月第一天和最后一天
                    this_month = self.set_begin_and_end()

                    if record.is_delete_date > this_month["end"].date():

                        record.pension_individual = demo1.base * demo1.pension      # 养老
                        record.medical_personal = demo1.base * demo1.medical_treatment      # 医疗
                        record.unemployed_individual = demo1.base * demo1.unemployment      # 失业
                        record.provident_fund_deduction = demo1.Provident_Fund_Base * demo1.provident_fund_ratio    # 公积金
                        record.social_security_deductions = demo1.base * demo1.pension + demo1.base * demo1.medical_treatment + demo1.base * demo1.unemployment     # 社保

                    else:
                        record.pension_individual = 0
                        record.medical_personal = 0
                        record.unemployed_individual = 0
                        record.social_security_deductions = 0
                        record.provident_fund_deduction = 0

                else:

                    record.pension_individual = demo1.base * demo1.pension      # 养老
                    record.medical_personal = demo1.base * demo1.medical_treatment      # 医疗
                    record.unemployed_individual = demo1.base * demo1.unemployment      # 失业
                    record.provident_fund_deduction = demo1.Provident_Fund_Base * demo1.provident_fund_ratio    # 公积金
                    record.social_security_deductions = demo1.base * demo1.pension + demo1.base * demo1.medical_treatment + demo1.base * demo1.unemployment     # 社保

            elif record.name.is_social_security == "不交":
                record.pension_individual = 0
                record.medical_personal = 0
                record.unemployed_individual = 0
                record.social_security_deductions = 0
                record.provident_fund_deduction = 0

            else:
                raise ValidationError('员工社保出错！')



    # 查询请假天数
    def set_every_detail(self):

        # 获取当月第一天和最后一天
        this_month = self.set_begin_and_end()
        # 获取部门id
        department_id = self.first_level_department.id
        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]

        # 查询请假记录
        every_detail_objs = self.env["every.detail"].sudo().search([
            ("leave_officer", "=", self.name.id),
            ("date", ">=", this_month["begin"]),
            ("end_date", "<=", this_month["end"])
        ])

        # 如果有请假记录
        if every_detail_objs:

            matter_days = 0     # 事假
            disease_days = 0    # 病假

            for every_detail_obj in every_detail_objs:


                tem_matter_days = 0     # 事假临时变量
                tem_disease_days = 0    # 病假临时变量
                rest_days = 0   # 休息天数

                # 查询>= 请假开始时间 和<= 请假结束时间的日历，获取请假中的休息天数
                custom_calendar_objs = self.env["custom.calendar"].sudo().search([
                    ('date', '>=', every_detail_obj.date),
                    ('date', '<=', every_detail_obj.end_date),
                    ])
                if custom_calendar_objs:
                    # 休息天数
                    for custom_calendar_obj in custom_calendar_objs:
                        custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                            ("custom_calendar_id", "=", custom_calendar_obj.id),    # 日历id
                            ("department", "=", department_id)   # 部门id
                            ])
                        if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                            rest_days = rest_days + 1
                        elif rest_type == "大小休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息"):
                            rest_days = rest_days + 1
                        elif rest_type == "双休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息" or custom_calendar_line_id.state== "仅双休休息"):
                            rest_days = rest_days + 1

                # 如果没有请假条
                if every_detail_obj.are_there_any_leave_slips == False:

                    # tem_absenteeism_days = tem_absenteeism_days + (every_detail_obj.end_date - every_detail_obj.date).days - rest_days
                    # if tem_absenteeism_days == 0:
                    #     if every_detail_obj.days > 2:
                    #         tem_absenteeism_days = 1
                    pass

                else:
                    if every_detail_obj.reason_for_leave2 == "事假":

                        tem_matter_days = (every_detail_obj.end_date - every_detail_obj.date).days
                        if tem_matter_days == 0:
                            if every_detail_obj.days > 2:
                                tem_matter_days = 1
                        else:
                            tem_matter_days = tem_matter_days + 1

                        # 减去休息天数
                        tem_matter_days = tem_matter_days - rest_days

                        # tem_disease_days = every_detail_obj.fsn_days


                    elif every_detail_obj.reason_for_leave2 == "病假":

                        tem_disease_days = (every_detail_obj.end_date - every_detail_obj.date).days
                        if tem_disease_days == 0:
                            if every_detail_obj.days > 2:
                                tem_disease_days = 1
                        else:
                            tem_disease_days = tem_disease_days + 1

                        # 减去休息天数
                        tem_matter_days = tem_matter_days - rest_days

                        # tem_disease_days = every_detail_obj.fsn_days


                matter_days = matter_days + tem_matter_days
                disease_days = disease_days + tem_disease_days


            self.matter_days = matter_days  # 事假(天)
            self.disease_days = disease_days    # 病假(天)



    # 获取本月全部的天
    def get_this_month_days(self):

        date = str(self.date)
        date2 = date.split('-')
        year = int(date2[0])
        month = int(date2[1])

        num_days = calendar.monthrange(year,month)[1]## 最后一天
        start_date = datetime.date(year,month,1)
        end_date = datetime.date(year,month,num_days)

        entry_date = self.name.entry_time   # 入职日期
        dimission_date = self.name.is_delete_date   # 离职日期

        scope_1 = 0
        scope_2 = 0

        if entry_date < start_date:
            if dimission_date:
                if dimission_date > end_date:
                    days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
                elif dimission_date == end_date:
                    days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
                    days = days[0: -1]
                else:
                    days = [datetime.date(year, month, day) for day in range(1, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        else:
            if dimission_date:
                if dimission_date > end_date:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days+1)]
                elif dimission_date == end_date:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days+1)]
                    days = days[0: -1]
                else:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days+1)]


        # days = [datetime.date(year, month, day) for day in range(1, num_days+1)]

        # print(days)
        # print("------------")

        return days


    # 查询旷工天数:打卡和补卡
    def set_absenteeism_punch_card(self, day):
        tem_absenteeism_days = 1
        # 查询打卡记录
        punch_in_record_obj = self.env["punch.in.record"].sudo().search([
            ("employee", "=", self.name.id),
            ("date", "=", day),
        ])
        # 如果打卡记录
        if punch_in_record_obj:

            if punch_in_record_obj.check_sign[0: 5] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "上班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_absenteeism_days = 0
                else:
                    # 查询请假表
                    every_detail_objs  = self.env["every.detail"].sudo().search([
                        ("leave_officer", "=", self.name.id),
                        ("date", "<=", day),
                        ("end_date", ">=", day)
                    ])
                    # 如果查到了
                    if every_detail_objs:
                        tem_absenteeism_days = 0

                    else:
                        exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                            ("start_date", "<=", day),
                            ("end_date", ">=", day),
                            ("employee_id", "=", self.name.id)
                        ])
                        if exchange_rest_use_line_obj:
                            tem_absenteeism_days = 0

            elif punch_in_record_obj.check_sign[6: 11] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "下班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_absenteeism_days = 0
                else:
                    # 查询请假表
                    every_detail_objs  = self.env["every.detail"].sudo().search([
                        ("leave_officer", "=", self.name.id),
                        ("date", "<=", day),
                        ("end_date", ">=", day)
                    ])
                    # 如果查到了
                    if every_detail_objs:

                        tem_absenteeism_days = 0

                    else:
                        exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                            ("start_date", "<=", day),
                            ("end_date", ">=", day),
                            ("employee_id", "=", self.name.id)
                        ])
                        if exchange_rest_use_line_obj:
                            tem_absenteeism_days = 0
            else:
                tem_absenteeism_days = 0
        else:
            up_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "上班卡")
            ])
            below_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "下班卡")
            ])
            if up_repair_clock_in_line_obj and below_repair_clock_in_line_obj:
                tem_absenteeism_days = 0
            else:
                # 查询请假表
                every_detail_objs  = self.env["every.detail"].sudo().search([
                    ("leave_officer", "=", self.name.id),
                    ("date", "<=", day),
                    ("end_date", ">=", day)
                ])
                # 如果查到了
                if every_detail_objs:

                    tem_absenteeism_days = 0
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", self.name.id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_absenteeism_days = 0

        if tem_absenteeism_days == 1:
            print(day, "============")
        return tem_absenteeism_days



    # 查询旷工天数
    def set_absenteeism_days(self):

        # 获取部门id
        department_id = self.first_level_department.id
        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]
        # 获取当月第一天和最后一天
        # this_month = self.set_begin_and_end()
        # 获取部门id

        # 临时旷工天数
        tem_absenteeism_days = 0

        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)':

            # 循环当月的全部天
            for day in self.get_this_month_days():
                # 先查询日历
                custom_calendar_obj = self.env["custom.calendar"].sudo().search([
                    ("date", "=", day)
                ])
                # 如果日历有记录
                if custom_calendar_obj:
                    custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                        ("custom_calendar_id", "=", custom_calendar_obj.id),    # 日历id
                        ("department", "=", department_id)   # 部门id
                        ])
                    if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                        pass
                    elif rest_type == "大小休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息"):
                        pass
                    elif rest_type == "双休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息" or custom_calendar_line_id.state== "仅双休休息"):
                        pass
                    # 如果不休息
                    else:
                        # 查询统计员工信息
                        group_attendance_objs = self.env["memp.memp"].sudo().search([
                            ("employee", "=", self.name.id),
                            ("date", "=", day),
                        ])
                        # 如果有统计员工信息
                        if group_attendance_objs:
                            pass
                        # 如果没有统计员工信息
                        else:
                            # 查询请假表
                            every_detail_objs  = self.env["every.detail"].sudo().search([
                                ("leave_officer", "=", self.name.id),
                                ("date", "<=", day),
                                ("end_date", ">=", day)
                            ])
                            # 如果查到了
                            if every_detail_objs:
                                pass
                            # 如果没查到
                            else:
                                tem_absenteeism_days = tem_absenteeism_days + 1
                                print(day, "============")
                else:
                    group_attendance_objs = self.env["memp.memp"].sudo().search([
                        ("employee", "=", self.name.id),
                        ("date", "=", day),
                    ])
                    # 如果有统计员工信息
                    if group_attendance_objs:
                        pass
                    else:
                        # 查询请假表
                        every_detail_objs  = self.env["every.detail"].sudo().search([
                            ("leave_officer", "=", self.name.id),
                            ("date", "<=", day),
                            ("end_date", ">=", day)
                        ])
                        # 如果查到了
                        if every_detail_objs:
                            pass
                        # 如果没查到
                        else:
                            tem_absenteeism_days = tem_absenteeism_days + 1

                            print(day, "============")

        else:
            # 循环当月的全部天
            for day in self.get_this_month_days():
                # 先查询日历
                custom_calendar_obj = self.env["custom.calendar"].sudo().search([
                    ("date", "=", day)
                ])
                # 如果日历有记录
                if custom_calendar_obj:
                    custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                        ("custom_calendar_id", "=", custom_calendar_obj.id),    # 日历id
                        ("department", "=", department_id)   # 部门id
                        ])
                    if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                        pass
                    elif rest_type == "大小休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息"):
                        pass
                    elif rest_type == "双休" and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state== "大小休休息" or custom_calendar_line_id.state== "仅双休休息"):
                        pass
                    # 如果不休息
                    else:
                        tem_absenteeism_days = tem_absenteeism_days + self.set_absenteeism_punch_card(day)


                else:
                    tem_absenteeism_days = tem_absenteeism_days + self.set_absenteeism_punch_card(day)


        self.absenteeism_days = tem_absenteeism_days    # 旷工(天)


    # 房补计算
    def set_rental_allowance(self, entry_time, first_day, last_day):

        # 查询房补基数
        set_up_base_objs = self.env["set.up.base"].sudo().search([("date", "=", self.date)])

        if self.should_attend:
            # （房补基数/应出勤天数) * 实出勤天数
            return (set_up_base_objs.housing_supplement / self.should_attend) * self.clock_in_time
        else:
            return 0



    # 饭补计算
    def set_rice_tonic(self, entry_time, departure_date, first_day, last_day):

        # 查询有没有退卡记录
        refill_card_return_obj = self.env["refill_card_return"].sudo().search([
            ("employee_id", "=", self.name.id),
            ("month", "=", self.date)
        ])
        if refill_card_return_obj:
            # 饭补
            self.meal_allowance = refill_card_return_obj.recharge_amount

            return refill_card_return_obj.refund_amount
            # (1 - (self.clock_in_time / self.should_attend))
        else:

            this_month = self.set_begin_and_end()

            last_day = this_month["end"]     # 当月最后一天
            first_day = this_month["begin"]      # 当月第一天
            meal_subsidy_top_up_obj = self.env["meal_subsidy_top_up"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("name", "=", self.name.id)
            ])

            if meal_subsidy_top_up_obj:
                # 饭补
                self.meal_allowance = meal_subsidy_top_up_obj.amount
                # 饭补扣款 = 饭补额度 * （1-（实际出勤/饭卡充值里面的出勤天数）)
                # working_time = self.be_on_the_job_days(entry_time, departure_date, first_day, last_day)
                return self.meal_allowance * (1 - (self.clock_in_time / meal_subsidy_top_up_obj.attendance_day))
            else:
                return 0



    # 设置全勤奖  入职时间 当月第一天 当月最后一天
    def set_perfect_attendance(self, entry_time, first_day, last_day):

        attendance_bonus_limit = self.name.attendance_bonus_limit

        # 本月之前入职
        if entry_time <= first_day:

            # 未离职或离职时间在本月之后
            if not self.name.is_delete_date:

                # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                if self.should_attend == self.clock_in_time:

                    # 查询全勤奖基数set_up_base_objs.perfect_attendance
                    # set_up_base_objs = self.env["set.up.base"].sudo().search([("date", "=", self.date)])

                    # return set_up_base_objs.perfect_attendance
                    return attendance_bonus_limit
                else:
                    return 0

            else:

                if self.name.is_delete_date >= last_day.date():

                    # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                    if self.should_attend == self.clock_in_time:

                        # 查询全勤奖基数set_up_base_objs.perfect_attendance
                        # set_up_base_objs = self.env["set.up.base"].sudo().search([("date", "=", self.date)])

                        # return set_up_base_objs.perfect_attendance
                        return attendance_bonus_limit
                    else:
                        return 0

                else:

                    return 0

        else:
            return 0


    # 设置工资之内的全勤奖计算
    def set_internal_perfect_attendance(self):

        attendance_bonus_limit = self.name.attendance_bonus_limit


        if self.should_attend == self.clock_in_time:

            return 0
        else:

            return attendance_bonus_limit




    # 全勤奖查询日历
    def attendance_bonus_calendar(self, date_end):

        while True:

            custom_calendar_obj = self.env["custom.calendar"].sudo().search([
                ("date", "=", date_end)
            ])
            if custom_calendar_obj:
                # 获取员工的休息类型(单休还是双休或者大小休息)
                rest_type = self.name.time_plan.split(' ')[-1]

                custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([
                    ("custom_calendar_id", "=", custom_calendar_obj.id),
                    ("department", "=", self.first_level_department.id),
                ])
                if rest_type == "单休" and custom_calendar_line_obj.state == "休息":

                    date_end = date_end + datetime.timedelta(days=1)
                    continue
                elif rest_type == "大小休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息"):

                    date_end = date_end + datetime.timedelta(days=1)
                    continue
                elif rest_type == "双休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息" or custom_calendar_line_obj.state== "仅双休休息"):

                    date_end = date_end + datetime.timedelta(days=1)
                    continue
                else:
                    break
            else:

                break

        return date_end



    # 全勤奖perfect_attendance_award   饭补rice_tonic rice_tonic1   租房津贴rental_allowance  招聘奖金
    def allowance_refresh(self):
        # 全勤奖   饭补   房补
        for record in self:

            # 获取当月第一天和最后一天
            this_month = record.set_begin_and_end()

            date_end_of_the_month6 = this_month["end"]     # 当月最后一天
            date_end = this_month["begin"]      # 当月第一天
            date_fanbu = datetime.datetime.strptime(str(record.entry_time), '%Y-%m-%d')     # 入职时间
            if record.is_delete_date:
                departure_date = datetime.datetime.strptime(str(record.is_delete_date), '%Y-%m-%d')     # 离职时间
            else:
                departure_date = False

            if record.name.attendance_bonus_type == "薪酬之外":

                # 全勤奖查询日历
                first_day = record.attendance_bonus_calendar(date_end)

                record.perfect_attendance_award = record.set_perfect_attendance(date_fanbu, first_day, date_end_of_the_month6)
            # elif record.name.attendance_bonus_type == "薪酬之内":

            #     # 全勤奖查询日历
            #     first_day = record.attendance_bonus_calendar(date_end)

            #     record.perfect_attendance_award = -record.set_internal_perfect_attendance(date_fanbu, first_day, date_end_of_the_month6)
            # else:
            #     pass

            if record.name.dormitory_subsidy == "有":
                # 房补(入职时间, 当月第一天, 当月最后一天)
                record.rental_allowance = record.set_rental_allowance(date_fanbu, date_end, date_end_of_the_month6)

            if record.name.rice_tonic == "有":
                # 饭补扣款(入职时间, 当月第一天, 当月最后一天)
                record.rice_tonic = record.set_rice_tonic(date_fanbu, departure_date, date_end, date_end_of_the_month6)

            # 招聘奖金
            record.recruitment_reward = record.set_recruitment_reward(date_end, date_end_of_the_month6)


    # 设置招聘奖金
    def set_recruitment_reward(self, first_day, last_day):

        if self.name.department_id.name == "人事行政部":

            pass
        else:
            personnel_award_objs = self.env["personnel_award"].sudo().search([
                ("introducer", "=", self.name.id),  # 员工id
                ("working_time", ">=", 30),     # 在职时长大于30天
                ("satisfy_date", ">=", first_day),  # 满足30天日期大于等于当月第一天
                ("satisfy_date", "<=", last_day),  # 满足30天日期小于等于当月第一天
            ])

            tem_award_money = 0
            for personnel_award_obj in personnel_award_objs:

                personnel_award_line_obj = personnel_award_obj.personnel_award_line_ids.sudo().search([
                    ("personnel_award_id", "=", personnel_award_obj.id),
                    ("award_month", "=", f"{first_day.year}-{'%02d' % first_day.month}")
                ])

                tem_award_money = tem_award_money + personnel_award_line_obj.award_money

            return (tem_award_money / 100) * 3



    # 查询是否旷工
    def query_absenteeism(self, dDate):
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            # 查询统计员工信息
            group_attendance_objs = self.env["memp.memp"].sudo().search([
                ("employee", "=", self.name.id),
                ("date", "=", dDate),
            ])
            # 如果有统计员工信息
            if group_attendance_objs:
                return False
            # 如果没有统计员工信息
            else:
                # 查询请假表
                every_detail_objs  = self.env["every.detail"].sudo().search([
                    ("leave_officer", "=", self.name.id),
                    ("date", "<=", dDate),
                    ("end_date", ">=", dDate)
                ])
                # 如果查到了
                if every_detail_objs:
                    return False
                # 如果没查到
                else:
                    return True
        else:
            # 查询旷工天数:打卡和补卡
            if self.set_absenteeism_punch_card(dDate):
                return True
            else:
                return False


    # 查询是否请假
    def query_leave(self, dDate):

        # 查询请假表
        every_detail_objs  = self.env["every.detail"].sudo().search([
            ("leave_officer", "=", self.name.id),
            ("date", "<=", dDate),
            ("end_date", ">=", dDate)
        ])
        if every_detail_objs:
            return True
        else:
            return False


    # 查询补卡
    def query_reissue_a_card(self, dDate):

        # 查询调休使用
        # exchange_rest_use_line
        exchange_rest_use_line_objs = self.env["exchange_rest_use_line"].sudo().search([
            ("employee_id", "=", self.name.id),
            ("start_date", "<=", dDate),
            ("end_date", ">=", dDate)
        ])
        if exchange_rest_use_line_objs:
            return True
        else:
            return False




    # 迟到早退扣款
    def set_be_late_deduct_money(self, first_day, last_day, deduct_money_setting_obj):

        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]

        come_to_work_objs = self.env["come.to.work"].sudo().search([
            ("name", "=", self.name.id),
            ("date", ">=", first_day),
            ("date", "<=", last_day)
        ])
        tem_total_time = 0

        for come_to_work_obj in come_to_work_objs:

            if self.name.entry_time == come_to_work_obj.date:
                pass
            else:

                custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", come_to_work_obj.date)])
                if custom_calendar_obj:
                    custom_calendar_line_objs = self.env["custom_calendar_line"].sudo().search([
                        ("custom_calendar_id", "=", custom_calendar_obj.id),
                        ("department", "=", self.first_level_department.id)
                        ])

                    if rest_type == "单休" and custom_calendar_line_objs.state == "休息":
                        pass
                    elif rest_type == "大小休" and (custom_calendar_line_objs.state == "休息" or custom_calendar_line_objs.state== "大小休休息"):
                        pass
                    elif rest_type == "双休" and (custom_calendar_line_objs.state == "休息" or custom_calendar_line_objs.state== "大小休休息" or custom_calendar_line_objs.state== "仅双休休息"):
                        pass
                    else:
                        # 判断是否旷工或请假
                        if self.query_absenteeism(come_to_work_obj.date) or self.query_leave(come_to_work_obj.date) or self.query_reissue_a_card(come_to_work_obj.date):
                            pass
                        else:
                            tem_total_time = tem_total_time + (come_to_work_obj.minutes_late + come_to_work_obj.total_time_early)

                else:
                    # 判断是否旷工或请假
                    if self.query_absenteeism(come_to_work_obj.date) or self.query_leave(come_to_work_obj.date) or self.query_reissue_a_card(come_to_work_obj.date):
                        pass
                    else:
                        tem_total_time = tem_total_time + (come_to_work_obj.minutes_late + come_to_work_obj.total_time_early)


        # 迟到早退分钟数
        self.be_late_time = tem_total_time

        # 如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工":

                self.late_arrival_and_early_refund_deduction = (self.pay_now * (tem_total_time / (21.75 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio
        if self.name.is_it_a_temporary_worker == '临时工':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":

                self.late_arrival_and_early_refund_deduction = (self.pay_now * (tem_total_time / (21.75 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio

        else:
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":

                self.late_arrival_and_early_refund_deduction = (self.pay_now * (tem_total_time / (21.75 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio



    # 请假扣款
    def set_ask_for_leave_deduct_money(self, deduct_money_setting_obj):


        # 如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工":

                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "仅计件工种" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "非临时工":

                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio

        # 如果是临时工
        elif self.name.is_it_a_temporary_worker == '临时工':

            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":

                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "仅临时工" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "非计件工种":

                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio


        else:

            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件和临时工" or \
                deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":

                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "非临时工" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "非计件和临时工" or \
                deduct_money_setting_obj.sick_leave_deduct_money == "非计件工种":

                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio


            # if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":
            #     # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
            #     self.leave_deduction = (self.leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            # if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or deduct_money_setting_obj.sick_leave_deduct_money == "非计件工种":
            #     # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
            #     self.sick_leave_deduction = (self.sick_leave_days * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio




    # 旷工扣款
    def set_absenteeism_deduct_money(self, deduct_money_setting_obj):
        # 如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':

            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "仅计件工种" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "非临时工":
                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio

        elif self.name.is_it_a_temporary_worker == '临时工':

            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "仅临时工" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "仅计件和临时工" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "非计件工种":
                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio

        else:
            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "非临时工" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "非计件和临时工" or \
                deduct_money_setting_obj.absenteeism_deduct_money == "非计件工种":

                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.pay_now / (21.75 * 8))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio



    # 设置其他扣款(奖罚记录单)
    def set_other_deductions(self, first_day, last_day):

        reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
            ("emp_id", "=", self.name.id),
            ("declare_time", ">=", first_day),
            ("declare_time", "<=", last_day)
        ])
        tem_money_amount = 0
        for reward_punish_record_obj in reward_punish_record_objs:
            # 如果奖惩记录单的类型为惩罚
            if reward_punish_record_obj.record_type == "punish" or reward_punish_record_obj.record_type == "compensation":
                tem_money_amount = tem_money_amount + reward_punish_record_obj.money_amount

        self.other_deductions = tem_money_amount


    # 设置扣款
    def set_deduct_money(self):
        for record in self:
            # 获取当月第一天和最后一天
            this_month = record.set_begin_and_end()
            # 当月第一天
            this_month_first_day = this_month["begin"]
            # 当月最后一天
            this_month_last_day = this_month["end"]

            # 查询扣款设置
            deduct_money_setting_obj = self.env["deduct_money_setting"].sudo().search([("month", "=", record.date)])

            if deduct_money_setting_obj:

                # 设置请假扣款
                record.set_ask_for_leave_deduct_money(deduct_money_setting_obj)
                # 设置迟到早退扣款
                record.set_be_late_deduct_money(this_month_first_day, this_month_last_day, deduct_money_setting_obj)
                # 设置旷工扣款
                record.set_absenteeism_deduct_money(deduct_money_setting_obj)
                # 设置其他扣款
                record.set_other_deductions(this_month_first_day, this_month_last_day)
            else:
                raise ValidationError(f"未设置当月的扣款记录信息！")



    # 判断是否转正
    @api.depends('name')
    def _dormitory_depends(self):
        for record in self:
            # 是否转正  whether_to_turn_positive
            #  转正时间
            turn_positive_time = record.name.turn_positive_time
            if turn_positive_time:
                #    这个月的一号换成时间类型
                date = record.date
                date2 = date.split('-')
                year = date2[0]
                month = date2[1]
                day = 1
                date_pinjie = year + '-' + month + '-' + str(day)
                date_end = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')
                turn_positive_time = datetime.datetime.strptime(str(turn_positive_time), '%Y-%m-%d')
                if turn_positive_time <= date_end:
                    record.whether_to_turn_positive = True
                else:
                    record.whether_to_turn_positive = False
            else:
                record.whether_to_turn_positive = False


    #  宿舍费用刷新
    def dormitory_salary_refresh(self):
        for record in self:
            # 月份       姓名
            date = record.date
            name = record.name
            demo = self.env['dormitory.property'].sudo().search([
                ('month', '=', date),
                ('name', '=', name.id)
            ])
            if demo:
                # 水电物业费扣款
                record.dormitory_water_and_electricity_deduction = demo.water_and_electricity_property_fee_deduction
                # 租金扣款
                # record.rent_deduction = demo.rent_deduction

            else:
                pass

            # 判断是否入住公司宿舍
            if record.name.is_dormitory == "入住":
                # 获取房租 set_up_base_obj.housing_supplement
                set_up_base_obj = self.env["set.up.base"].sudo().search([("date", "=", record.date)])

                # record.rent_deduction = (set_up_base_obj.housing_supplement / record.should_attend) * (record.should_attend - record.clock_in_time)
                # 房租扣款 = （房租 / 21.75） * （旷工天数 + 病假天数 + 事假天数）
                tem_rent_deduction = (set_up_base_obj.housing_supplement / 21.75) * (record.matter_days + record.disease_days + record.absenteeism_days)

                extra_expense = 0
                if demo:
                    # 额外租金
                    extra_expense = demo.rent_deduction
                # 租金扣款 = 正常租金扣款 + 额外租金扣款
                record.rent_deduction = tem_rent_deduction + extra_expense

            elif record.name.is_dormitory == "不入住":

                record.rent_deduction = 0

            else:

                raise ValidationError("员工宿舍设置错误！")








    @api.constrains('date', 'name')
    def check_date(self):
        def is_valid_date(strdate):
            '''判断是否是一个有效的日期字符串'''
            try:
                if "-" in strdate:
                    if strdate.split('-')[1] in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                        datetime.datetime.strptime(strdate, "%Y-%m")
                        return True
                    else:
                        return False
            except:
                return False
        date = is_valid_date(self.date)
        if date:
            pass
        else:
            raise ValidationError("日期要符合类似1990-01")
        #    同一个人同一个月份不能有多条记录
        demo = self.env['salary'].sudo().search([
            ('date', '=', self.date),
            ('name', '=', self.name.id)
        ])
        if len(demo) > 1:
            raise ValidationError('同一个人同一个月份不能有多条记录')
        else:
            pass



    @api.model
    def create(self, val):

        return super(salary, self).create(val)




    # 获取应出勤天数
    def attendance_days_refresh(self):
        """    可以让每个工种的人的应出勤天数从设置里读出    """
        for record in self:

            # 获取员工的休息类型(单休还是双休或者大小休息)
            rest_type = record.name.time_plan.split(' ')[-1]
            # 获取员工所在部门
            department_id = record.first_level_department.id

            year = int(record.date.split("-")[0])
            month = int(record.date.split("-")[1])
            # 这个月的天数
            the_month_days = calendar.monthrange(year, month)[1]
            # 这个月的第一天
            the_month_first_day = datetime.date(year, month, 1)
            # 这个月的最后一天
            the_month_last_day = datetime.date(year, month, the_month_days)

            # 获取休息天数
            custom_calendar_objs = self.env["custom.calendar"].sudo().search([
                ('date', '>=', the_month_first_day),
                ('date', '<=', the_month_last_day),
                ])

            # 休息天数
            rest_days = 0
            for custom_calendar_obj in custom_calendar_objs:
                if rest_type == "单休":
                    for custom_calendar_line_id in custom_calendar_obj.custom_calendar_line_ids:
                        if department_id == custom_calendar_line_id.department.id and custom_calendar_line_id.state == "休息":
                            rest_days = rest_days + 1
                elif rest_type == "大小休":
                    for custom_calendar_line_id in custom_calendar_obj.custom_calendar_line_ids:
                        if department_id == custom_calendar_line_id.department.id and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                            rest_days = rest_days + 1
                elif rest_type == "双休":
                    for custom_calendar_line_id in custom_calendar_obj.custom_calendar_line_ids:
                        if department_id == custom_calendar_line_id.department.id and (custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
                            rest_days = rest_days + 1

            # 应出勤天数 = the_month_days - 休息的天数
            record.should_attend = the_month_days - rest_days




    # 设置请假小时数和旷工小时数
    def set_ask_for_leave_time(self):

        # 获取当月第一天和最后一天
        this_month = self.set_begin_and_end()
        # 获取部门id
        department_id = self.first_level_department.id
        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]

        # 查询请假记录
        every_detail_objs = self.env["every.detail"].sudo().search([
            ("leave_officer", "=", self.name.id),
            ("date", ">=", this_month["begin"]),
            ("end_date", "<=", this_month["end"])
        ])

        # 病假小时数
        sick_leave_time = 0
        # 事假小时数
        thing_leave_time = 0
        # 旷工小时数
        absenteeism = 0
        # 循环查询出来的请假记录
        for every_detail_obj in every_detail_objs:
            # 如果没有请假条
            if every_detail_obj.are_there_any_leave_slips == False:

                absenteeism = absenteeism + every_detail_obj.days

            else:

                if every_detail_obj.reason_for_leave2 == "事假":

                    thing_leave_time = thing_leave_time + every_detail_obj.days

                elif every_detail_obj.reason_for_leave2 == "病假":

                    sick_leave_time = sick_leave_time + every_detail_obj.days


        # leave_days = fields.Float(string='事假(时)')
        # sick_leave_days = fields.Float(string='病假(时)')
        # absenteeism_time = fields.Float(string='旷工（时)')
        self.leave_days = thing_leave_time
        self.sick_leave_days = sick_leave_time

        if self.name.time_plan[7:12] == "21:00":
            self.absenteeism_time = absenteeism + self.absenteeism_days * 11.5
        else:
            self.absenteeism_time = absenteeism + self.absenteeism_days * 8


    # 计算实际出勤时间
    def set_actual_attendance_time(self):
        # 设置请假小时数
        self.set_ask_for_leave_time()


    # 实出勤天数计算:打卡和补卡查询,调休记录
    def punch_card_and_fill_card(self, day):
        tem_clock_in_time = 0

        # 查询打卡机记录,如果有则+1,如果没有则查询补卡记录
        punch_in_record_obj = self.env["punch.in.record"].sudo().search([("date", "=", day), ("employee", "=", self.name.id)])

        # 如果有打卡记录
        if punch_in_record_obj:

            if punch_in_record_obj.check_sign[0: 5] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "上班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", self.name.id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1

            elif punch_in_record_obj.check_sign[6: 11] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "下班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", self.name.id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1
            else:
                tem_clock_in_time = 1

        # # 如果没有打卡记录
        else:
            up_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "上班卡")
            ])
            below_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "下班卡")
            ])
            if up_repair_clock_in_line_obj and below_repair_clock_in_line_obj:
                tem_clock_in_time = 1
            else:
                exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                    ("start_date", "<=", day),
                    ("end_date", ">=", day),
                    ("employee_id", "=", self.name.id)
                ])
                if exchange_rest_use_line_obj:
                    tem_clock_in_time = 1

        return tem_clock_in_time




    # 实出勤天数计算
    def punch_in_machine_refresh(self):

        for record in self:

            # 设置请假天数
            record.set_every_detail()
            # 设置旷工天数
            record.set_absenteeism_days()

            # 计算实际出勤时间
            record.set_actual_attendance_time()
            # matter_days = fields.Float(string="事假(天)")
            # disease_days = fields.Float(string="病假(天)")

            if record.name.is_it_a_temporary_worker == '正式工(计件工资)' or record.name.is_it_a_temporary_worker == '临时工' or record.name.is_it_a_temporary_worker == '实习生(计件)':

                this_month = record.set_begin_and_end()
                # return {"begin": date_end, "end": date_end_of_the_month6}

                name_list = []
                # 查询统计中的员工信息表
                memp_memp_objs = self.env["memp.memp"].sudo().search([
                    ("employee", "=", record.name.id),
                    ("date", ">=", this_month["begin"]),
                    ("date", "<=", this_month["end"])
                ])

                for memp_memp_obj in memp_memp_objs:
                    name_list.append(memp_memp_obj.date)
                # 按日期去重后存放到列表中
                name_list = list(set(name_list))
                # 实际出勤天数 = 列表长度 - 请假天数(病假+事假)
                # clock_in_time = len(name_list) - (record.matter_days + record.disease_days + record.absenteeism_days)
                clock_in_time = len(name_list)

                # 如果实际出勤天数大于应出勤天数，则实际出勤天数=应出勤天数
                if clock_in_time > record.should_attend:
                    record.clock_in_time = record.should_attend
                else:
                    record.clock_in_time = clock_in_time

            else:
                # 获取员工部门
                # record.first_level_department
                # 获取员工的休息类型(单休还是双休或者大小休息)
                rest_type = record.time_plan.split(' ')[-1]
                # 出勤天数
                clock_in_time = 0

                # 循环当月全部天
                for day in record.get_this_month_days():

                    # 默认为不休息
                    is_rest = False
                    # 先查询日历，这天是否是休息，如果查询到是休息，则将is_rest = True
                    custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", day)])
                    if custom_calendar_obj:
                        custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([("custom_calendar_id", "=", custom_calendar_obj.id), ("department", "=", record.first_level_department.id)])

                        if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                            is_rest = True
                        elif rest_type == "大小休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息"):
                            is_rest = True
                        elif rest_type == "双休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息" or custom_calendar_line_obj.state== "仅双休休息"):
                            is_rest = True
                    # 如果休息则跳过，如果不休息则查询考勤机 计算实出勤天数
                    if is_rest:
                        pass
                    else:

                        clock_in_time = clock_in_time + record.punch_card_and_fill_card(day)


                record.clock_in_time = clock_in_time






    # 计算月平均效率
    def set_month_workpiece_ratio(self):

        for record in self:


            # 获取当月第一天和最后一天
            this_month = record.set_begin_and_end()
            first_day = this_month["begin"]
            last_day = this_month["end"]

            eff_eff_objs = self.env["automatic_efficiency_table"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("employee_id", "=", record.name.id)
            ])

            if eff_eff_objs:

                record.month_workpiece_ratio = sum(eff_eff_objs.mapped('efficiency')) / len(eff_eff_objs)

            else:

                record.month_workpiece_ratio = 0

            # 人工效率
            eff_eff_objs = self.env["eff.eff"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("employee", "=", record.name.id)
            ])

            if eff_eff_objs:

                record.manual_month_workpiece_ratio = sum(eff_eff_objs.mapped('totle_eff')) / len(eff_eff_objs)

            else:

                record.manual_month_workpiece_ratio = 0



    # 组长薪资刷新
    def group_leader_assess(self):
        for record in self:

            this_month = self.set_begin_and_end()
            this_month["end"]

            if record.job_id.name == "流水组长":

                # 如果离职了
                if record.is_delete_date:
                    pass
                # 如果没离职
                else:
                    tem_sum = 0
                    objs = self.search([
                        ("first_level_department", "=", record.first_level_department.id),
                        ("id", "!=", record.id),
                        ])
                    for obj in objs:
                        # if obj.is_delete_date == False or obj.is_delete_date
                        tem_sum = tem_sum + obj.pay_now
                    tem_salary = (tem_sum * 0.12)

                    # if tem_salary > record.salary_payable1:
                    if tem_salary > 10000:
                        record.sudo().write({
                            "salary_payable1": tem_salary
                        })
            else:
                raise ValidationError(f"{record.name.name}不是组长！")


class social_base(models.Model):
    _name = 'socail.base'
    _description = '社会保障'

    date = fields.Date('日期')
    base = fields.Float('社保基数', digits=(16, 3))
    pension = fields.Float('养老金比列', digits=(16, 3))
    medical_treatment = fields.Float('医疗比列', digits=(16, 3))
    unemployment = fields.Float('失业比列', digits=(16, 3))
    Provident_Fund_Base = fields.Float('公积金基数', digits=(16, 3))
    provident_fund_ratio = fields.Float('公积金比列', digits=(16, 3))
