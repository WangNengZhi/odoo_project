from odoo.exceptions import ValidationError
from odoo import models, fields, api
import datetime
import calendar

'''工资条'''

class FsnSalarySheet(models.Model):
    _inherit = "fsn_salary_sheet"


    # 获取本月全部的天
    def get_this_month_days(self):

        date = str(self.month)
        date2 = date.split('-')
        year = int(date2[0])
        month = int(date2[1])

        num_days = calendar.monthrange(year,month)[1]## 最后一天
        start_date = datetime.date(year,month,1)
        end_date = datetime.date(year,month,num_days)

        entry_date = self.employee_id.entry_time
        dimission_date = self.employee_id.is_delete_date


        if entry_date < start_date:
            if dimission_date:
                if dimission_date >= end_date:
                    days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
                else:
                    days = [datetime.date(year, month, day) for day in range(1, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        else:
            if dimission_date:
                if dimission_date >= end_date:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days+1)]
                else:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days+1)]


        # days = [datetime.date(year, month, day) for day in range(1, num_days+1)]

        return days


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



    # 设置基本工资
    def set_basic_wage(self):

        # 获取基本工资数额
        set_up_base_obj = self.env["set.up.base"].sudo().search([
            ("date", "=", self.month)
        ])

        # 获取当月第一天和最后一天
        # this_month = self.set_begin_and_end()
        # 获取当月该员工在职的全部天
        job_day_list = self.get_this_month_days()

        work_days = 0  # 工作日出勤天数

        overtime_days = 0   # 加班出勤天数

        statutory_holiday_days = 0  # 法定节假日出勤天数

        # 循环该员工在职的全部天
        for job_day in job_day_list:

            if self.contract == "正式工(计件工资)" or self.contract == "临时工" or self.contract == "实习生(计件)":
                # 查询现场工序员工记录
                memp_memp_objs = self.env["memp.memp"].sudo().search([
                    ("employee", "=", self.employee_id.id),
                    ("date", "=", job_day),
                ])
                if memp_memp_objs:

                    # 查询日历
                    custom_calendar_obs = self.env["custom.calendar"].sudo().search([("date", "=", job_day)])
                    # 如果查询到,并且是法定节假日
                    if custom_calendar_obs and custom_calendar_obs.extra_work_type == "法定节假日":

                        statutory_holiday_days = statutory_holiday_days + 1

                    elif custom_calendar_obs and custom_calendar_obs.extra_work_type == "非法定节假日":

                        overtime_days = overtime_days + 1
                    else:

                        week = job_day.weekday()
                        if week < 5 or week == 6:    # 周一到周五或者周日
                            work_days = work_days + 1
                        elif week == 5:    # 周六
                            overtime_days = overtime_days + 1
                else:
                    # 查询调休记录
                    exchange_rest_use_line_objs = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", job_day),
                        ("end_date", ">=", job_day),
                        ("employee_id", "=", self.employee_id.id)
                    ])
                    if exchange_rest_use_line_objs:

                        # 查询日历
                        custom_calendar_obs = self.env["custom.calendar"].sudo().search([("date", "=", job_day)])
                        # 如果查询到,并且是法定节假日
                        if custom_calendar_obs and custom_calendar_obs.extra_work_type == "法定节假日":

                            statutory_holiday_days = statutory_holiday_days + 1

                        elif custom_calendar_obs and custom_calendar_obs.extra_work_type == "非法定节假日":

                            overtime_days = overtime_days + 1
                        else:

                            week = job_day.weekday()
                            if week < 5 or week == 6:    # 周一到周五或者周日
                                work_days = work_days + 1
                            elif week == 5:    # 周六
                                overtime_days = overtime_days + 1
            else:
                # 查询打卡记录
                punch_in_record_objs = self.env["punch.in.record"].sudo().search([
                    ("date", "=", job_day),
                    ("employee", "=", self.employee_id.id)
                ])
                if punch_in_record_objs:
                    # 查询日历
                    custom_calendar_obs = self.env["custom.calendar"].sudo().search([("date", "=", job_day)])
                    # 如果查询到,并且是法定节假日
                    if custom_calendar_obs and custom_calendar_obs.extra_work_type == "法定节假日":

                        statutory_holiday_days = statutory_holiday_days + 1

                    elif custom_calendar_obs and custom_calendar_obs.extra_work_type == "非法定节假日":

                        overtime_days = overtime_days + 1
                    else:

                        week = job_day.weekday()
                        if week < 5 or week == 6:    # 周一到周五或者周日
                            work_days = work_days + 1
                        elif week == 5:    # 周六
                            overtime_days = overtime_days + 1
                else:
                    # 查询补卡记录
                    repair_clock_in_line_objs = self.env["repair_clock_in_line"].sudo().search([
                        ("employee_id", "=", self.employee_id.id),
                        ("line_date", "=", job_day),
                    ])
                    if repair_clock_in_line_objs:
                        # 查询日历
                        custom_calendar_obs = self.env["custom.calendar"].sudo().search([("date", "=", job_day)])
                        # 如果查询到,并且是法定节假日
                        if custom_calendar_obs and custom_calendar_obs.extra_work_type == "法定节假日":

                            statutory_holiday_days = statutory_holiday_days + 1

                        elif custom_calendar_obs and custom_calendar_obs.extra_work_type == "非法定节假日":

                            overtime_days = overtime_days + 1
                        else:

                            week = job_day.weekday()
                            if week < 5 or week == 6:    # 周一到周五或者周日
                                work_days = work_days + 1
                            elif week == 5:    # 周六
                                overtime_days = overtime_days + 1
                    else:
                        # 查询调休记录
                        exchange_rest_use_line_objs = self.env["exchange_rest_use_line"].sudo().search([
                            ("start_date", "<=", job_day),
                            ("end_date", ">=", job_day),
                            ("employee_id", "=", self.employee_id.id)
                        ])
                        if exchange_rest_use_line_objs:
                            # 查询日历
                            custom_calendar_obs = self.env["custom.calendar"].sudo().search([("date", "=", job_day)])
                            # 如果查询到,并且是法定节假日
                            if custom_calendar_obs and custom_calendar_obs.extra_work_type == "法定节假日":

                                statutory_holiday_days = statutory_holiday_days + 1
                            elif custom_calendar_obs and custom_calendar_obs.extra_work_type == "非法定节假日":

                                overtime_days = overtime_days + 1
                            else:

                                week = job_day.weekday()
                                if week < 5 or week == 6:    # 周一到周五或者周日
                                    work_days = work_days + 1
                                elif week == 5:    # 周六
                                    overtime_days = overtime_days + 1





        day_wage = set_up_base_obj.base_pay / 21.75     # 日工资

        basic_wage = day_wage * work_days   # 工作日工资
        # 晚上9点下班的
        if self.employee_id.time_plan == "8:00 - 21:00, 单休":
            overtime_wage = (day_wage / 8) * 11 * 2 * overtime_days + (day_wage / 8) * 3 * 1.5 * work_days + (day_wage / 8) * 11 * 3 * statutory_holiday_days # 加班工资
        # 晚上6点下班的
        elif self.employee_id.time_plan == "9:00 - 18:00, 单休"\
            or self.employee_id.time_plan == "8:00 - 18:00, 单休"\
                or self.employee_id.time_plan == "7:30 - 17:00, 单休"\
                    or self.employee_id.time_plan == "9:00 - 18:00, 双休"\
                        or self.employee_id.time_plan == "8:00 - 19:00, 单休":
            overtime_wage = (day_wage / 8) * 8 * 2 * overtime_days + (day_wage / 8) * 11 * 3 * statutory_holiday_days # 加班工资
        return basic_wage, overtime_wage




    # 设置加班工资
    def set_overtime_wage(self):

        set_up_base_obj = self.env["set.up.base"].sudo().search([
            ("date", "=", self.month)
        ])

        # 临时加班工资
        tem_overtime_wage = 0

        # 晚上9点下班的
        if self.employee_id.time_plan == "8:00 - 21:00, 单休":

            # 获取本月在职的全部天
            job_day_list = self.get_this_month_days()
            # 循环当月的全部天
            for day in job_day_list:
                # 获取当前是周几
                week = day.weekday() + 1
                if week == 6:
                    tem_overtime_wage = tem_overtime_wage + ((set_up_base_obj.base_pay / 21.75) / 8) * 11 * 2
                elif week == 7:
                    pass
                else:
                    tem_overtime_wage = tem_overtime_wage + ((set_up_base_obj.base_pay / 21.75) / 8) * 3 * 2

            return tem_overtime_wage

        # 晚上6点下班的
        elif self.employee_id.time_plan == "9:00 - 18:00, 单休" or self.employee_id.time_plan == "8:00 - 18:00, 单休" or self.employee_id.time_plan == "7:30 - 17:00, 单休":
            # 获取本月在职的全部天
            job_day_list = self.get_this_month_days()
            # 循环当月的全部天
            for day in job_day_list:
                # 获取当前是周几
                week = day.weekday() + 1
                if week == 6:
                    tem_overtime_wage = tem_overtime_wage + ((set_up_base_obj.base_pay / 21.75) / 8) * 11 * 2

            return tem_overtime_wage

    # 设置补贴
    def set_subsidy(self):

        # 补贴 = 饭补 + 全勤 + 房补 + 客户补贴(客户补贴移动到业绩工资) + 春节补贴 + 离职补贴
        # subsidy = self.meal_allowance + self.attendance_bonus + self.rent_allowance + self.customer_subsidy
        subsidy = self.meal_allowance + self.attendance_bonus + self.rent_allowance + self.job_allowance + self.dimission_subsidy

        return subsidy

    # 设置离职补贴
    def set_dimission_subsidy(self):
        
        return self.dimission_subsidy

    # 设置奖金
    def set_bonus(self):
        # 奖金 = 招聘奖金
        bonus = self.recruitment_reward

        return bonus

    # 设置税
    def set_tax(self):

        # 税 = 社保 + 个税
        tax = self.social_security_deductions + self.tax

        return tax

    # 设置扣款
    def set_deduct_money(self):
        # 扣款 = 事假扣款 + 病假扣款 + 旷工扣款 + 其他扣款 + 宿舍水电扣款 + 房租扣款 + 饭补扣款
        deduct_money = self.leave_deduction + self.sick_leave_deduction + self.absenteeism_deduction + self.other_deductions + self.dormitory_water_and_electricity_deduction + self.rent_deduction + self.rice_tonic

        return deduct_money

    # 生成工资条
    def generate_true_salary_sheet(self):
        for record in self:

            # 先查询一下工资表，有没有当前月份该员工的工资条，如果有则删除重新创建
            fsn_salary_sheet_obj = self.env["fsn_true_salary_sheet"].sudo().search([("month", "=", record.month), ("name", "=", record.employee_id.id)])

            if fsn_salary_sheet_obj:
                fsn_salary_sheet_obj.sudo().unlink()


            # 设置基本工资, 加班工资
            basic_wage, overtime_wage = record.set_basic_wage()
            # 设置加班工资
            # overtime_wage = record.set_overtime_wage()
            # 设置补贴
            subsidy = record.set_subsidy()
            # 设置税
            tax = record.set_tax()
            # 扣款
            deduct_money = record.set_deduct_money()
            # 奖金
            bonus = record.set_bonus()
            # 离职补贴
            dimission_subsidy = record.set_dimission_subsidy()



            self.env["fsn_true_salary_sheet"].sudo().create({
                "month": record.month,   # 日期
                "name": record.employee_id.id,     # 姓名
                "practical_attendance_day": record.clock_in_time,   # 实出勤天数
                "basic_wage": basic_wage,   # 基本工资
                "overtime_wage": overtime_wage,     # 加班工资
                "subsidy": subsidy,   # 补贴
                "deduct_money": deduct_money,       # 扣款
                "dimission_subsidy": dimission_subsidy,     # 离职补贴
                "advance": record.advance_salary,       # 预支
                "tax": tax,     # 税
                "bonus": bonus,     # 奖金
            })




class FsnTrueSalarySheet(models.Model):
    _name = 'fsn_true_salary_sheet'
    _description = 'fsn_工资条'

    month = fields.Char(string='月份', required=True)
    name = fields.Many2one('hr.employee', string='姓名')
    practical_attendance_day = fields.Integer(string="实际出勤天数")
    first_level_department = fields.Many2one("hr.department", string="部门", compute="_set_emp_message", store=True)
    contract = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('实习生', '实习生'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], string='工种', compute="_set_emp_message", store=True)
    is_delete_date = fields.Date(string='离职日期', compute="_set_emp_message", store=True)
    basic_wage = fields.Float(string="基本工资")
    overtime_wage = fields.Float(string="加班工资")
    subsidy = fields.Float(string="补贴")
    bonus = fields.Float(string="奖金")
    performance = fields.Float(string="业绩工资", compute="set_performance", store=True)
    deduct_money = fields.Float(string="扣款")
    advance = fields.Float(string="预支")
    should_wage1 = fields.Float(string="应付工资1", compute="set_should_wage1", store=True)
    dimission_subsidy = fields.Float(string="离职补贴")
    tax = fields.Float(string="税")
    should_wage2 = fields.Float(string="应付工资2", compute="set_should_wage2", store=True)

    is_abnormal = fields.Boolean(string="是否异常", compute="_set_is_abnormal", store=True)

    is_grant = fields.Boolean(string="是否发放", default=True)




    # 检测数据是否异常
    @api.depends('basic_wage', 'overtime_wage', 'should_wage1')
    def _set_is_abnormal(self):
        for record in self:
                        # (基本工资 + 加班工资) - (扣款 + 预支工资)
            tem_var = (record.basic_wage + record.overtime_wage) - (record.deduct_money + record.advance)

            if record.should_wage1 < tem_var:
                record.is_abnormal = True






    # 设置员工信息
    @api.depends('name')
    def _set_emp_message(self):
        for record in self:
            # 离职日期
            record.is_delete_date = record.name.is_delete_date
            # 部门
            record.first_level_department = record.name.department_id.id
            # 合同/工种
            record.contract = record.name.is_it_a_temporary_worker


    # 计算业绩工资
    @api.depends('month', 'name', 'basic_wage', 'overtime_wage', 'subsidy', 'performance', 'deduct_money', 'advance')
    def set_performance(self):
        for record in self:
            salary_obj = self.env["fsn_salary_sheet"].sudo().search([
                ("month", "=", record.month),
                ("employee_id", "=", record.name.id)
            ])

            # 增加 = 基本工资 + 加班工资 + 补贴
            increase = record.basic_wage + record.overtime_wage + record.subsidy
            # 减少 = 扣款 + 预支
            reduce = record.deduct_money + record.advance
            # 业绩工资 = 应发工资2(薪酬管理) - 增加 + 减少
            record.performance = salary_obj.salary_payable2 - increase + reduce


    # 计算应付工资1
    @api.depends('basic_wage', 'overtime_wage', 'subsidy', 'performance', 'deduct_money', 'advance', 'bonus')
    def set_should_wage1(self):
        for record in self:
            # 增加 = 基本工资 + 加班工资 + 补贴 + 业绩工资 + 奖金
            increase = record.basic_wage + record.overtime_wage + record.subsidy + record.performance + record.bonus
            # 减少 = 扣款 + 预支
            reduce = record.deduct_money + record.advance
            # 应付工资 = 增加 - 减少
            record.should_wage1 = increase - reduce


    # 计算应该付工资2
    @api.depends('should_wage1', 'tax')
    def set_should_wage2(self):
        for record in self:
            # 应付工资2 - 应付工资1 - 税
            record.should_wage2 = record.should_wage1 - record.tax




    # 发送异常通知
    def is_notice(self):
        # 获取上个月时间
        current_time = fields.datetime.now() - datetime.timedelta(days=30)
        # 查询上个月工资条
        fsn_true_salary_sheet_objs = self.env["fsn_true_salary_sheet"].sudo().search([
            ("month", "=", f'{current_time.year}-{current_time.month}')
        ])

        tem_var = False
        # 判断是否有异常
        for fsn_true_salary_sheet_obj in fsn_true_salary_sheet_objs:
            if fsn_true_salary_sheet_obj.is_abnormal:
                tem_var = True
                break

        return tem_var


    # 修改是否发放
    def set_is_grant(self):
        for record in self:

            if record.is_grant:
                record.is_grant = False
            else:
                record.is_grant = True







