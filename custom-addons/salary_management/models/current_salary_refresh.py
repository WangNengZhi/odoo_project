
from itertools import permutations
from re import T
from odoo.exceptions import ValidationError
from odoo import models, fields, api

import datetime
import calendar

class salary(models.Model):
    _inherit = "salary"

    # 该次继承用于计算正常薪资刷新(按月计算)






    # 查询休息天数
    def set_rest_days(self, start_time, end_time):
        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]
        # 获取员工所在部门
        department_id = self.first_level_department.id
        rest_days = 0   # 休息天数

        # 查询>= 请假开始时间 和<= 请假结束时间的日历，获取请假中的休息天数
        custom_calendar_objs = self.env["custom.calendar"].sudo().search([
            ('date', '>=', start_time),
            ('date', '<=', end_time),
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

        return rest_days



    # 用于查询转正调岗时的应出勤天数
    def special_should_attendance(self, entry_date, dimission_date, start_time, end_time):
        """    用于查询转正调岗时的应出勤天数    """


        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]
        # 获取员工所在部门
        department_id = self.first_level_department.id

        year = int(self.date.split("-")[0])
        month = int(self.date.split("-")[1])
        # 这个月的天数
        the_month_days = calendar.monthrange(year, month)[1]

        # 如果入职时间大于当月第一天
        if entry_date > start_time:
            # 这个月的第一天
            the_month_first_day = entry_date
        else:
            # 这个月的第一天
            the_month_first_day = start_time

        # 如果离职时间小于当月最后一天
        if dimission_date and dimission_date < end_time:
            the_month_last_day = dimission_date
        else:
            # 这个月的最后一天
            the_month_last_day = end_time

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
        # self.should_attend = the_month_days - rest_days
        return the_month_days - rest_days



    # 无调岗计算
    def not_transfer_position(self, *args):


        start_time = args[1]
        end_time = args[2]
        calculation = args[3]
        full_time_deductions = args[4]

        # 判断是否是计件
        if self.name.is_it_a_temporary_worker == "正式工(计件工资)" \
            or self.name.is_it_a_temporary_worker == "临时工" \
                or self.name.is_it_a_temporary_worker == "实习生(计件)":
            if start_time and end_time:

                # 查询计件工资记录
                ji_jian_objs = self.env["ji.jian"].sudo().search([
                    ("employee", "=", self.name.id),
                    ("date1", ">=", start_time),
                    ("date1", "<=", end_time)
                ])

                tem_cost = 0
                for ji_jian_obj in ji_jian_objs:
                    tem_cost = tem_cost + ji_jian_obj.cost

                self.pay_now = tem_cost

            else:

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"]
                this_month_last_day = this_month["end"]

                # 查询计件工资记录
                ji_jian_objs = self.env["ji.jian"].sudo().search([
                    ("employee", "=", self.name.id),
                    ("date1", ">=", this_month_first_day),
                    ("date1", "<=", this_month_last_day)
                ])

                tem_cost = 0
                for ji_jian_obj in ji_jian_objs:
                    tem_cost = tem_cost + ji_jian_obj.cost

                self.pay_now = tem_cost

        else:
            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            this_month_first_day = this_month["begin"].date()
            this_month_last_day = this_month["end"].date()

            # 查询转正记录
            become_full_member_objs = self.env["become_full_member"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("turn_positive_date", ">=", this_month_first_day),
                ("turn_positive_date", "<=", this_month_last_day),
                ("state", "=", "确认")
            ])
            # 如果有转正记录
            if become_full_member_objs:

                # 转正之前薪资
                before_pay = become_full_member_objs.probation_period_treatment - full_time_deductions
                # 转正之后薪资
                after_pay = become_full_member_objs.after_pay - full_time_deductions
                # 转正日期
                become_date = become_full_member_objs.turn_positive_date

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"].date()   # 这个月第一天
                this_month_last_day = this_month["end"].date()  # 这个月最后一条
                entry_date = self.name.entry_time   # 入职日期
                dimission_date = self.name.is_delete_date   # 离职日期

                if calculation == "按月计算":
                    # 计算在职天数
                    before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                    # 这个月转正之前薪资
                    this_month_before_pay = (before_pay / 30.5) * before_job_days

                    # 计算在职天数
                    after_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                    # 这个月转正之前薪资
                    this_month_after_pay = (after_pay / 30.5) * after_job_days

                elif calculation == "按天计算":

                    before_job_days = self.special_should_attendance(entry_date, become_date, this_month_first_day, this_month_last_day)

                    this_month_before_pay = (before_pay / 26) * before_job_days

                    after_job_days = self.special_should_attendance(become_date, dimission_date, this_month_first_day, this_month_last_day)

                    this_month_after_pay = (after_pay / 26) * after_job_days


                # 这个月薪资 = 这个月转正之前薪资 + 这个月转正之后薪资
                self.pay_now = this_month_before_pay + this_month_after_pay

            # 如果没有转正记录
            else:

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"].date()   # 这个月第一天
                this_month_last_day = this_month["end"].date()  # 这个月最后一条
                entry_date = self.name.entry_time   # 入职日期
                dimission_date = self.name.is_delete_date   # 离职日期
                fixed_salary = self.name.fixed_salary - full_time_deductions    # 减去全勤扣款

                if calculation == "按月计算":

                    # 计算在职天数
                    job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day, this_month_last_day)
                    # 如果在职天数等于当月全部天数
                    if job_days == this_month_last_day.day:
                        self.pay_now = fixed_salary
                    else:
                        tem_pay_now = (fixed_salary / 30.5) * job_days
                        if tem_pay_now > fixed_salary:
                            self.pay_now = fixed_salary
                        else:
                            self.pay_now = tem_pay_now

                elif calculation == "按天计算":

                    # (薪酬 / 26) * 应出勤天数
                    self.pay_now = (fixed_salary / 26) * self.clock_in_time





    # 正常薪资刷新(开始时间，结束时间，计算方式)
    def current_salary_refresh(self, start_time, end_time, calculation):

        if self.name.attendance_bonus_type == "薪酬之内":
            # 计算全勤扣款
            full_time_deductions = self.set_internal_perfect_attendance()
        else:
            full_time_deductions = 0

        # 如果没有设置时间范围，则默认为当月的第一天和最后一天
        if start_time and end_time:
            # 查询内部调岗表
            internal_post_transfer_objs = self.env["internal.post.transfer"].sudo().search([
                ("name", "=", self.name.id),
                ("begin_start", ">=", start_time),
                ("begin_start", "<=", end_time),
                ("adjust_salary", "=", True),
                ("state", "=", "确认")
            ])
            # 查询转正记录
            become_full_member_objs = self.env["become_full_member"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("turn_positive_date", ">=", start_time),
                ("turn_positive_date", "<=", end_time),
                ("state", "=", "确认")
            ])
        else:
            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            this_month_first_day = this_month["begin"].date()
            this_month_last_day = this_month["end"].date()

            # 查询内部调岗表
            internal_post_transfer_objs = self.env["internal.post.transfer"].sudo().search([
                ("name", "=", self.name.id),
                ("begin_start", ">=", this_month_first_day),
                ("begin_start", "<=", this_month_last_day),
                ("adjust_salary", "=", True),
                ("state", "=", "确认")
            ])
            # 查询转正记录
            become_full_member_objs = self.env["become_full_member"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("turn_positive_date", ">=", this_month_first_day),
                ("turn_positive_date", "<=", this_month_last_day),
                ("state", "=", "确认")
            ])



        # 如果有转岗记录
        if internal_post_transfer_objs:

            if len(internal_post_transfer_objs) > 1:
                raise ValidationError(f"{self.name.name}暂不支持多次调岗的薪资计算！")
            elif  len(internal_post_transfer_objs) == 1:
                # 如果同时有转正记录
                if become_full_member_objs:
                    raise ValidationError(f"{self.name.name}暂不支持同时调岗和转正的薪资计算！")
                else:
                    # 调整之前薪资
                    before_pay = internal_post_transfer_objs.before_pay - full_time_deductions
                    # 调整之后薪资
                    after_pay = internal_post_transfer_objs.the_salary_adjustment_scheme - full_time_deductions
                    # 调整日期
                    become_date = internal_post_transfer_objs.begin_start

                    # 是否调整工种
                    if internal_post_transfer_objs.is_temporary_worker:
                        # 判断之前的工种
                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or self.name.is_it_a_temporary_worker == "实习生(计件)":
                            if start_time and end_time:
                            # 查询计件工资记录
                                ji_jian_objs = self.env["ji.jian"].sudo().search([
                                    ("employee", "=", self.name.id),
                                    ("date1", ">=", start_time),
                                    ("date1", "<=", become_date)
                                ])

                                tem_cost = 0
                                for ji_jian_obj in ji_jian_objs:
                                    tem_cost = tem_cost + ji_jian_obj.cost

                                this_month_before_pay = tem_cost
                            else:
                                # 获取当月第一天和最后一天
                                this_month = self.set_begin_and_end()
                                this_month_first_day = this_month["begin"]
                                this_month_last_day = this_month["end"]

                                # 查询计件工资记录
                                ji_jian_objs = self.env["ji.jian"].sudo().search([
                                    ("employee", "=", self.name.id),
                                    ("date1", ">=", this_month_first_day),
                                    ("date1", "<=", become_date)
                                ])

                                tem_cost = 0
                                for ji_jian_obj in ji_jian_objs:
                                    tem_cost = tem_cost + ji_jian_obj.cost

                                this_month_before_pay = tem_cost
                        else:

                            # 获取当月第一天和最后一天
                            this_month = self.set_begin_and_end()
                            this_month_first_day = this_month["begin"].date()   # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time   # 入职日期
                            dimission_date = self.name.is_delete_date   # 离职日期

                            if calculation == "按月计算":
                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_before_pay = (before_pay / 30.5) * job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                job_days = self.special_should_attendance(entry_date, become_date, this_month_first_day, this_month_last_day)

                                this_month_before_pay = (before_pay / 26) * job_days


                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                            if start_time and end_time:
                            # 查询计件工资记录
                                ji_jian_objs = self.env["ji.jian"].sudo().search([
                                    ("employee", "=", self.name.id),
                                    ("date1", ">=", become_date),
                                    ("date1", "<=", end_time)
                                ])

                                tem_cost = 0
                                for ji_jian_obj in ji_jian_objs:
                                    tem_cost = tem_cost + ji_jian_obj.cost

                                this_month_after_pay = tem_cost
                            else:
                                # 获取当月第一天和最后一天
                                this_month = self.set_begin_and_end()
                                this_month_first_day = this_month["begin"]
                                this_month_last_day = this_month["end"]

                                # 查询计件工资记录
                                ji_jian_objs = self.env["ji.jian"].sudo().search([
                                    ("employee", "=", self.name.id),
                                    ("date1", ">=", become_date),
                                    ("date1", "<=", this_month_last_day)
                                ])

                                tem_cost = 0
                                for ji_jian_obj in ji_jian_objs:
                                    tem_cost = tem_cost + ji_jian_obj.cost

                                this_month_after_pay = tem_cost

                        else:

                            # 获取当月第一天和最后一天
                            this_month = self.set_begin_and_end()
                            this_month_first_day = this_month["begin"].date()   # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time   # 入职日期
                            dimission_date = self.name.is_delete_date   # 离职日期


                            if calculation == "按月计算":
                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day, this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_after_pay = (after_pay / 30.5) * job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                job_days = self.special_should_attendance(entry_date, dimission_date, this_month_first_day, this_month_last_day)

                                this_month_after_pay = (after_pay / 26) * job_days


                        # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                        self.pay_now = this_month_before_pay + this_month_after_pay
                    else:

                        # 判断是否是计件
                        if self.name.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or self.name.is_it_a_temporary_worker == "临时工" \
                                or self.name.is_it_a_temporary_worker == "实习生(计件)":

                            raise ValidationError(f"{self.name.name}调岗情况发生意料之外的情况！")

                        else:

                            # 获取当月第一天和最后一天
                            this_month = self.set_begin_and_end()
                            this_month_first_day = this_month["begin"].date()   # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time   # 入职日期
                            dimission_date = self.name.is_delete_date   # 离职日期

                            if calculation == "按月计算":

                                # 计算在职天数
                                before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_before_pay = (before_pay / 30.5) * before_job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                before_job_days = self.special_should_attendance(entry_date, become_date, this_month_first_day, this_month_last_day)

                                this_month_before_pay = (before_pay / 26) * before_job_days


                            if calculation == "按月计算":

                                # 计算在职天数
                                after_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_after_pay = (after_pay / 30.5) * after_job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                after_job_days = self.special_should_attendance(become_date, dimission_date, this_month_first_day, this_month_last_day)

                                this_month_after_pay = (after_pay / 26) * after_job_days

                            if this_month_before_pay and this_month_after_pay:
                                # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                self.pay_now = this_month_before_pay + this_month_after_pay

                            else:

                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day, this_month_last_day)

                                # 如果在职天数等于当月全部天数
                                if job_days == this_month_last_day.day:

                                    self.pay_now = self.name.fixed_salary - full_time_deductions    # 减去全勤扣款

                                
                                else:
                                    # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                    self.pay_now = this_month_before_pay + this_month_after_pay


            else:
                raise ValidationError(f"{self.name.name}调岗薪资计算失败！")

        # 如果没有转岗记录
        else:

            self.not_transfer_position(self, start_time, end_time, calculation, full_time_deductions)


        # 有转岗组长薪资计算
        if internal_post_transfer_objs:
            if internal_post_transfer_objs.job_id.name == "流水组长" or internal_post_transfer_objs.raw_job_id.name == "流水组长":
                self.relieve_guard_group_leader_pay(internal_post_transfer_objs, full_time_deductions)
        # 无转岗薪资计算
        else:
            if self.job_id.name == "流水组长":
                self.not_relieve_guard_group_leader_pay()


    # 计算组长的考核薪资 = 组员薪资之和 * 0.12
    def calculate_group_members_pay_sum(self, start_time, end_time):

        # 查询薪资表中和组长相同部门的全部员工
        salary_objs = self.env["salary"].sudo().search([
            ("date", "=", self.date),
            ("first_level_department", "=", self.first_level_department.id),
            ("name", "!=", self.name.id),
        ])

        tem_pay_sum = 0
        for salary_obj in salary_objs:

            if salary_obj.job_id.name != "流水组长":

                # 如果离职的
                if salary_obj.name.is_delete:

                    # 离职时间大于当月最后一天的才算
                    if salary_obj.name.is_delete_date > self.set_begin_and_end()["end"].date():

                        # 查询计件工资记录
                        ji_jian_objs = self.env["ji.jian"].sudo().search([
                            ("employee", "=", salary_obj.name.id),
                            ("date1", ">=", start_time),
                            ("date1", "<=", end_time)
                        ])
                        for ji_jian_obj in ji_jian_objs:
                            tem_pay_sum = tem_pay_sum + ji_jian_obj.cost

                else:

                    # 查询计件工资记录
                    ji_jian_objs = self.env["ji.jian"].sudo().search([
                        ("employee", "=", salary_obj.name.id),
                        ("date1", ">=", start_time),
                        ("date1", "<=", end_time)
                    ])
                    for ji_jian_obj in ji_jian_objs:
                        tem_pay_sum = tem_pay_sum + ji_jian_obj.cost

        return tem_pay_sum * 0.12



    # 无转岗组长薪资计算
    def not_relieve_guard_group_leader_pay(self):

        # 获取当月第一天和最后一天
        this_month = self.set_begin_and_end()
        this_month_first_day = this_month["begin"].date()
        this_month_last_day = this_month["end"].date()
        # 入职时间
        entry_date = self.entry_time
        # 离职时间
        dimission_date = self.is_delete_date

        # 如果当月之前入职的
        if entry_date < this_month_first_day:
            # 如果离职了
            if dimission_date:
                # 离职日期大于当月最后一天
                if dimission_date > this_month_last_day:

                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, this_month_last_day)
                    if assess_apy > self.pay_now:
                        self.pay_now = assess_apy
                else:
                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, dimission_date)
                    if assess_apy > self.pay_now:
                        self.pay_now = assess_apy
            else:
                # 计算组长的考核薪资
                assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, this_month_last_day)
                if assess_apy > self.pay_now:
                    self.pay_now = assess_apy
        else:
            # 如果离职了
            if dimission_date:
                # 离职日期大于当月最后一天
                if dimission_date > this_month_last_day:
                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(entry_date, this_month_last_day)
                    if assess_apy > self.pay_now:
                        self.pay_now = assess_apy
                else:
                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(entry_date, dimission_date)
                    if assess_apy > self.pay_now:
                        self.pay_now = assess_apy
            else:
                # 计算组长的考核薪资
                assess_apy = self.calculate_group_members_pay_sum(entry_date, this_month_last_day)
                if assess_apy > self.pay_now:
                    self.pay_now = assess_apy


    # 有转岗组长薪资计算
    def relieve_guard_group_leader_pay(self, internal_post_transfer_objs, full_time_deductions):

        # 获取当月第一天和最后一天
        this_month = self.set_begin_and_end()
        this_month_first_day = this_month["begin"].date()
        this_month_last_day = this_month["end"].date()
        # 入职时间
        entry_date = self.entry_time
        # 离职时间
        dimission_date = self.is_delete_date

        # 调整之前薪资
        before_pay = internal_post_transfer_objs.before_pay
        # 调整之后薪资
        after_pay = internal_post_transfer_objs.the_salary_adjustment_scheme
        # 调整日期
        become_date = internal_post_transfer_objs.begin_start



        # 如果当月之前入职的
        if entry_date < this_month_first_day:
            # 如果离职了
            if dimission_date:
                # 当月之前入职的，离职日期大于当月最后一天----------------------1
                if dimission_date > this_month_last_day:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, become_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_before_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > before_pay:
                            adjust_before_pay = assess_apy

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", become_date),
                                ("date1", "<=", this_month_last_day)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_after_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days


                            if adjust_before_pay and adjust_after_pay:
                                # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                self.pay_now = adjust_before_pay + adjust_after_pay

                            else:

                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day, this_month_last_day)

                                # 如果在职天数等于当月全部天数
                                if job_days == this_month_last_day.day:

                                    self.pay_now = self.name.fixed_salary - full_time_deductions    # 减去全勤扣款

                                else:
                                    # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                    self.pay_now = adjust_before_pay + adjust_after_pay

                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", this_month_first_day),
                                ("date1", "<=", become_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_before_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(become_date, this_month_last_day)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_after_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > adjust_after_pay:
                            adjust_after_pay = assess_apy

                        self.pay_now = adjust_before_pay + adjust_after_pay

                # 当月之前入职的，离职日期小于等于当月最后一天----------------------2
                else:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":
                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, become_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_before_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > before_pay:
                            adjust_before_pay = assess_apy


                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", become_date),
                                ("date1", "<=", dimission_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_after_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days


                        self.pay_now = adjust_before_pay + adjust_after_pay

                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", this_month_first_day),
                                ("date1", "<=", become_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_before_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(become_date, dimission_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_after_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > adjust_after_pay:
                            adjust_after_pay = assess_apy

                        self.pay_now = adjust_before_pay + adjust_after_pay

            # 当月之前入职的，未离职----------------------3
            else:
                # 之前是组长
                if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(this_month_first_day, become_date)
                    # # 计算在职天数
                    before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                    # # 这个月调岗之前的正常薪资
                    adjust_before_pay = (before_pay / 30.5) * before_job_days

                    if assess_apy > before_pay:
                        adjust_before_pay = assess_apy

                    # 判断之后的工种
                    if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                        or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                        or internal_post_transfer_objs.after_temporary_worker == "临时工":
                        # 查询计件工资记录
                        ji_jian_objs = self.env["ji.jian"].sudo().search([
                            ("employee", "=", self.name.id),
                            ("date1", ">=", become_date),
                            ("date1", "<=", this_month_last_day)
                        ])
                        tem_cost = 0
                        for ji_jian_obj in ji_jian_objs:
                            tem_cost = tem_cost + ji_jian_obj.cost

                        adjust_after_pay = tem_cost
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_after_pay = (after_pay / 30.5) * job_days


                    self.pay_now = adjust_before_pay + adjust_after_pay
                # 之后是组长
                elif internal_post_transfer_objs.job_id.name == "流水组长":

                    if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                        or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                        # 查询计件工资记录
                        ji_jian_objs = self.env["ji.jian"].sudo().search([
                            ("employee", "=", self.name.id),
                            ("date1", ">=", this_month_first_day),
                            ("date1", "<=", become_date)
                        ])
                        tem_cost = 0
                        for ji_jian_obj in ji_jian_objs:
                            tem_cost = tem_cost + ji_jian_obj.cost

                        adjust_before_pay = tem_cost
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_before_pay = (before_pay / 30.5) * job_days

                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(become_date, this_month_last_day)
                    # # 计算在职天数
                    before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                    # # 这个月调岗之前的正常薪资
                    adjust_after_pay = (before_pay / 30.5) * before_job_days

                    if assess_apy > adjust_after_pay:
                        adjust_after_pay = assess_apy

                    self.pay_now = adjust_before_pay + adjust_after_pay
        else:

            if dimission_date:
                # 当月入职的，离职时间大于当月最后一天----------------------4
                if dimission_date > this_month_last_day:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(entry_date, become_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_before_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > before_pay:
                            adjust_before_pay = assess_apy

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", become_date),
                                ("date1", "<=", this_month_last_day)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_after_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days


                        self.pay_now = adjust_before_pay + adjust_after_pay

                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", entry_date),
                                ("date1", "<=", become_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_before_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(become_date, this_month_last_day)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_after_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > adjust_after_pay:
                            adjust_after_pay = assess_apy

                        self.pay_now = adjust_before_pay + adjust_after_pay
                # 当月入职的，离职时间小于等于当月最后一天----------------------5
                else:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(entry_date, become_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_before_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > before_pay:
                            adjust_before_pay = assess_apy

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", become_date),
                                ("date1", "<=", dimission_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_after_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days


                        self.pay_now = adjust_before_pay + adjust_after_pay

                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                            # 查询计件工资记录
                            ji_jian_objs = self.env["ji.jian"].sudo().search([
                                ("employee", "=", self.name.id),
                                ("date1", ">=", entry_date),
                                ("date1", "<=", become_date)
                            ])
                            tem_cost = 0
                            for ji_jian_obj in ji_jian_objs:
                                tem_cost = tem_cost + ji_jian_obj.cost

                            adjust_before_pay = tem_cost
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        # 计算组长的考核薪资
                        assess_apy = self.calculate_group_members_pay_sum(become_date, dimission_date)
                        # # 计算在职天数
                        before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # # 这个月调岗之前的正常薪资
                        adjust_after_pay = (before_pay / 30.5) * before_job_days

                        if assess_apy > adjust_after_pay:
                            adjust_after_pay = assess_apy

                        self.pay_now = adjust_before_pay + adjust_after_pay
            # 当月入职的，未离职----------------------6
            else:
                # 之前是组长
                if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(entry_date, become_date)
                    # # 计算在职天数
                    before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                    # # 这个月调岗之前的正常薪资
                    adjust_before_pay = (before_pay / 30.5) * before_job_days

                    if assess_apy > before_pay:
                        adjust_before_pay = assess_apy

                    # 判断之后的工种
                    if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                        or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":
                        # 查询计件工资记录
                        ji_jian_objs = self.env["ji.jian"].sudo().search([
                            ("employee", "=", self.name.id),
                            ("date1", ">=", become_date),
                            ("date1", "<=", this_month_last_day)
                        ])
                        tem_cost = 0
                        for ji_jian_obj in ji_jian_objs:
                            tem_cost = tem_cost + ji_jian_obj.cost

                        adjust_after_pay = tem_cost
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_after_pay = (after_pay / 30.5) * job_days


                    self.pay_now = adjust_before_pay + adjust_after_pay

                # 之后是组长
                elif internal_post_transfer_objs.job_id.name == "流水组长":

                    if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                        or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":
                        # 查询计件工资记录
                        ji_jian_objs = self.env["ji.jian"].sudo().search([
                            ("employee", "=", self.name.id),
                            ("date1", ">=", entry_date),
                            ("date1", "<=", become_date)
                        ])
                        tem_cost = 0
                        for ji_jian_obj in ji_jian_objs:
                            tem_cost = tem_cost + ji_jian_obj.cost

                        adjust_before_pay = tem_cost
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day, this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_before_pay = (before_pay / 30.5) * job_days

                    # 计算组长的考核薪资
                    assess_apy = self.calculate_group_members_pay_sum(become_date, this_month_last_day)
                    # # 计算在职天数
                    before_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day, this_month_last_day)
                    # # 这个月调岗之前的正常薪资
                    adjust_after_pay = (before_pay / 30.5) * before_job_days

                    if assess_apy > adjust_after_pay:
                        adjust_after_pay = assess_apy

                    self.pay_now = adjust_before_pay + adjust_after_pay











