import datetime
import calendar
import re
import time
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class salary(models.Model):
    _name = 'payroll1'
    _inherit = ['mail.thread']
    _description = 'FSN薪酬明细'

    date = fields.Char(string='月份', required=True, track_visibility='onchange')
    serial_number = fields.Integer('序号')
    name = fields.Many2one('hr.employee', string='姓名', track_visibility='onchange')
    id_card = fields.Char(string="身份证号", compute="_set_emp_message", store=True, track_visibility='onchange')
    first_level_department = fields.Many2one("hr.department", string="部门", compute="_set_emp_message", store=True,
                                             track_visibility='onchange')

    secondary_department = fields.Char(string='二级部门', compute="_set_emp_message", store=True,
                                       track_visibility='onchange')
    department_position = fields.Char(string='岗位(旧)')
    job_id = fields.Many2one('hr.job', string='岗位', compute="_set_emp_message", store=True,
                             track_visibility='onchange')
    job_name = fields.Char(string="岗位名称", related="job_id.name", store=True)
    staff_level = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('实习', '实习'),
    ], string='员工等级', track_visibility='onchange')
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
    turn_positive_time = fields.Date(string='转正时间', compute="_set_emp_message", store=True,
                                     track_visibility='onchange')
    is_delete_date = fields.Date(string='离职日期', compute="_set_emp_message", store=True, track_visibility='onchange')
    is_handover = fields.Boolean(string="是否已交接", compute="_set_emp_message", store=True)
    is_grant = fields.Boolean(string="是否发放", default=True, compute="set_is_grant", store=True)

    @api.depends("is_delete_date", "is_handover", "clock_in_time")
    def set_is_grant(self):
        for record in self:
            if record.is_delete_date:
                if not record.is_handover or record.clock_in_time <= 3:
                    record.is_grant = False
                else:
                    record.is_grant = True
            else:
                record.is_grant = True

    def manual_set_is_grant(self):
        for record in self:
            if record.is_grant:
                record.is_grant = False
            else:
                record.is_grant = True

    attendance_bonus_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="全勤奖类型")

    meal_allowance_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="饭补类型")

    housing_subsidy_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="房补类型")

    transfer_number = fields.Integer(string="调岗次数", compute="set_transfer_number", store=True,
                                     track_visibility='onchange')

    # 设置员工信息
    @api.depends('name')
    def set_transfer_number(self):
        for record in self:
            if "internal.post.transfer" in self.env and record.name and record.date:
                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()

                record.transfer_number = self.env["internal.post.transfer"].sudo().search_count([
                    ("name", "=", record.name.id),
                    ("begin_start", ">=", this_month.get("begin")),
                    ("begin_start", "<=", this_month.get("end")),
                ])

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
            # 员工等级
            record.staff_level = record.name.staff_level
            # 是否已交接
            record.is_handover = record.name.is_handover

            record.attendance_bonus_type = record.name.attendance_bonus_type
            record.meal_allowance_type = record.name.meal_allowance_type
            record.housing_subsidy_type = record.name.housing_subsidy_type

    def set_emp_message(self):
        self._set_emp_message()

    should_attend = fields.Float(string='应出勤(天)', track_visibility='onchange')
    should_attend_hours = fields.Float(string="应出勤(时)", compute='set_should_attend_hours', store=True,
                                       track_visibility='onchange')

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
    whether_to_turn_positive = fields.Boolean(string='是否转正', compute='_dormitory_depends', store=True,
                                              track_visibility='onchange')
    salary_type = fields.Char('工资类型', track_visibility='onchange')

    efficiency_wages = fields.Float(string="效率薪资", track_visibility='onchange')

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

    rental_allowance = fields.Float(string='租房津贴', track_visibility='onchange')
    seniority_award = fields.Float('工龄奖', track_visibility='onchange')

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
    other_deductions = fields.Float('绩效扣除', track_visibility='onchange')
    blue_collar_apartment_dormitory_deposit_deduction = fields.Float('宿舍押金扣款', track_visibility='onchange')
    rent_deduction = fields.Float('房租扣款', track_visibility='onchange')
    advanced = fields.Float('已预支', track_visibility='onchange')

    pension_individual = fields.Float('养老（个人)', track_visibility='onchange')
    medical_personal = fields.Float('医疗（个人）', track_visibility='onchange')
    unemployed_individual = fields.Float('失业（个人）', track_visibility='onchange')
    provident_fund_deduction = fields.Float('公积金扣款', track_visibility='onchange')
    social_security_allowance = fields.Float(string='社保津贴', track_visibility='onchange')

    # 社保刷新
    def set_social_security(self):

        socail_base_obj = self.env["socail.base"].sudo().search([])

        for record in self:
            # if record.contract in ["正式工(计件工资)", "实习生(计件)", "正式工(B级管理)", "正式工(A级管理)", "实习生(非计件)"]:

            if record.name.is_social_security == "交":

                now_year, now_month, _ = map(int, str(fields.Date.today()).split('-'))
                year, month = map(int, record.name.start_paying_social_security_month.split('-'))

                if ((now_year > year) or (now_month >= month)) and (now_year >= year):

                    # 获取当月第一天和最后一天
                    this_month = self.set_begin_and_end()

                    if record.is_delete_date == False or record.is_delete_date > this_month.get("end").date():

                        # 养老
                        record.pension_individual = socail_base_obj.base * socail_base_obj.pension
                        # 医疗
                        record.medical_personal = socail_base_obj.base * socail_base_obj.medical_treatment
                        # 事业
                        record.unemployed_individual = socail_base_obj.base * socail_base_obj.unemployment
                        # 社保津贴
                        record.social_security_allowance = record.pension_individual + record.medical_personal + record.unemployed_individual
                        # 社保扣款
                        record.social_security_deductions = record.pension_individual + record.medical_personal + record.unemployed_individual

                    else:
                        # 养老
                        record.pension_individual = 0
                        # 医疗
                        record.medical_personal = 0
                        # 事业
                        record.unemployed_individual = 0
                        # 社保津贴
                        record.social_security_allowance = 0
                        # 社保扣款
                        record.social_security_deductions = 0

                else:
                    # 养老
                    record.pension_individual = 0
                    # 医疗
                    record.medical_personal = 0
                    # 事业
                    record.unemployed_individual = 0
                    # 社保津贴
                    record.social_security_allowance = 0
                    # 社保扣款
                    record.social_security_deductions = 0
            else:
                # 养老
                record.pension_individual = 0
                # 医疗
                record.medical_personal = 0
                # 事业
                record.unemployed_individual = 0
                # 社保津贴
                record.social_security_allowance = 0
                # 社保扣款
                record.social_security_deductions = 0

    salary_payable1 = fields.Float(string='应发工资1', compute='set_salary_payable1', store=True, digits=[12, 2],
                                   track_visibility='onchange')

    dimission_subsidy = fields.Float(string="离职补贴", track_visibility='onchange')
    month_workpiece_ratio = fields.Float(string="自动月平均效率(%)", track_visibility='onchange')
    manual_month_workpiece_ratio = fields.Float(string="手工月平均效率(%)", track_visibility='onchange')
    last_month_month_workpiece_ratio = fields.Float(string="上月自动月平均效率(%)",
                                                    compute='set_last_month_month_workpiece_ratio', store=True)

    # 设置上月应发工资2
    @api.depends('month_workpiece_ratio', 'date', 'name')
    def set_last_month_month_workpiece_ratio(self):
        for record in self:
            if record.date and record.name:
                year, month = tuple(record.date.split("-"))

                if int(month) == 1:

                    date = "{year-1}-12"
                else:
                    month = int(month) - 1
                    date = f"{year}-{'%02d' % month}"

                obj = record.sudo().search([("date", "=", date), ("name", "=", record.name.id)])
                if obj:
                    record.last_month_month_workpiece_ratio = obj.month_workpiece_ratio
                else:
                    record.last_month_month_workpiece_ratio = 0

    customer_subsidy = fields.Float('客户补贴', groups='salary_management.kehubutie', track_visibility='onchange')

    compensation = fields.Float(string="赔偿", compute='set_salary_payable2', store=True, track_visibility='onchange')

    performance_bonus = fields.Float(string="绩效奖金", track_visibility='onchange')

    commission_bonus = fields.Float(string="提成", track_visibility='onchange')

    salary_payable2 = fields.Float(string='应发工资2', compute='set_salary_payable2', store=True, digits=[12, 2],
                                   track_visibility='onchange')

    day_average_salary = fields.Float(string="日均工资", compute='set_day_average_salary', store=True)

    # 计算日平均工资（实出勤天数，应发工资2）
    @api.depends('clock_in_time', 'salary_payable2')
    def set_day_average_salary(self):
        for record in self:
            if record.clock_in_time:
                record.day_average_salary = record.salary_payable2 / record.clock_in_time

    last_month_salary_payable2 = fields.Float(string="上月应发工资2", compute='set_last_month_salary_payable2',
                                              store=True)

    # 设置上月应发工资2
    @api.depends('salary_payable2', 'date', 'name')
    def set_last_month_salary_payable2(self):
        for record in self:
            if record.date and record.name:

                year, month = tuple(record.date.split("-"))

                if int(month) == 1:

                    date = "{year-1}-12"
                else:
                    month = int(month) - 1
                    date = f"{year}-{'%02d' % month}"

                obj = record.sudo().search([("date", "=", date), ("name", "=", record.name.id)])
                if obj:
                    record.last_month_salary_payable2 = obj.salary_payable2
                else:
                    record.last_month_salary_payable2 = 0

    salary_payable3 = fields.Float(string='实发', compute='set_salary_payable3', store=True, digits=[12, 2],
                                   track_visibility='onchange')
    social_security_deductions = fields.Float('社保扣款', track_visibility='onchange')
    tax = fields.Float('个税', track_visibility='onchange', compute='set_tax', store=True)

    @api.depends('salary_payable3', 'social_security_allowance')
    def set_tax(self):
        for record in self:
            if record.salary_payable3 > (record.social_security_allowance + 5000):
                record.tax = (record.salary_payable3 - (record.social_security_allowance + 5000)) * 0.03
            else:
                record.tax = 0

    paid_wages = fields.Float(string='实发2', compute='set_paid_wages', store=True, digits=[12, 2],
                              track_visibility='onchange')

    # 计算实发工资 = 应发工资3 - （社保扣款 + 个税）
    @api.depends('salary_payable3', 'social_security_deductions', 'provident_fund_deduction', 'tax')
    def set_paid_wages(self):
        for record in self:
            record.paid_wages = record.salary_payable3 - (
                        record.social_security_deductions + record.provident_fund_deduction + record.tax)

    state = fields.Selection([('已确认', '已确认'), ('未确认', '未确认'), ('有更改', '有更改')], string='状态',
                             default="未确认", track_visibility='onchange')
    confirm_date = fields.Datetime(string="确认日期", track_visibility='onchange')

    last_month_salary_payable3 = fields.Float(string="上月应发工资3（作废）", compute='set_last_month_salary_payable3',
                                              store=True)

    calculation = fields.Selection([('按月计算', '按月计算'), ('按天计算', '按天计算')], string='计算方式')

    # 设置上月应发工资3
    @api.depends('salary_payable3', 'date', 'name')
    def set_last_month_salary_payable3(self):
        for record in self:
            if record.date and record.name:

                year, month = tuple(record.date.split("-"))

                if int(month) == 1:

                    date = "{year-1}-12"
                else:
                    month = int(month) - 1
                    date = f"{year}-{'%02d' % month}"

                obj = record.sudo().search([("date", "=", date), ("name", "=", record.name.id)])
                if obj:
                    record.last_month_salary_payable3 = obj.salary_payable3
                else:
                    record.last_month_salary_payable3 = 0

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
            # pass
            self.judge_change()

        return res

    # 设置预支工资
    def set_advanced(self):
        for record in self:
            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()

            # 查询预支工资
            advance_of_wages_objs = self.env["advance_of_wages"].sudo().search_read([
                ("employee_id", "=", record.name.id),
                ("dDate", ">=", this_month["begin"]),
                ("dDate", "<=", this_month["end"]),
                ("approve_state", "=", "已审批"),
                ("wages_type", "in", ["薪酬", "借款"]),
            ], ["money"])
            tem_advanced = sum(i["money"] for i in advance_of_wages_objs)

            this_month = record.set_begin_and_end()
            last_day = this_month["end"]  # 当月最后一天
            first_day = this_month["begin"]  # 当月第一天

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
                print(this_month_last_day, entry_date)
                print((this_month_last_day - entry_date).days)
                tem_work_time = (this_month_last_day - entry_date).days + 1

        self.work_time = tem_work_time

        return tem_work_time

    # 计算应发工资1 = 正常薪资 + 租房津贴 + 春节补贴 + 全勤奖 + 饭补 + 招聘奖金 - （事假扣款 + 病假扣款 + 其他扣款 + 迟到早退扣款 + 宿舍水电物业费 + 宿舍房租扣款 + 旷工扣款) - 已预支 + 社保津贴 + 绩效工资
    @api.depends('pay_now', 'rental_allowance', 'perfect_attendance_award', 'meal_allowance', 'job_allowance',
                 'rice_tonic', 'leave_deduction', 'sick_leave_deduction', 'other_deductions',
                 'late_arrival_and_early_refund_deduction', 'dormitory_water_and_electricity_deduction',
                 'rent_deduction', 'advanced', 'social_security_allowance', 'performance_pay')
    def set_salary_payable1(self):
        for record in self:
            # 房补类型
            if record.name.housing_subsidy_type == "薪酬之内":
                # 津贴 = 全勤奖 + 春节补贴 + 招聘奖金
                allowance = record.perfect_attendance_award + record.job_allowance + record.recruitment_reward
            else:
                # 津贴 = 租房津贴 + 全勤奖 + 春节补贴 + 招聘奖金
                allowance = record.rental_allowance + record.perfect_attendance_award + record.job_allowance + record.recruitment_reward

            # 这些岗位的饭补参与计算
            if record.job_id.name in ['保洁', '司机', '流水组长', '整件', '实习生', '流水车位', '小烫', '分料员']:
                allowance = allowance + record.meal_allowance

            # 扣款 =  事假扣款 + 病假扣款 + 其他扣款 + 迟到早退扣款 + 旷工扣款
            deduct_money = record.leave_deduction + record.sick_leave_deduction + record.other_deductions + record.late_arrival_and_early_refund_deduction + record.absenteeism_deduction

            # if record.contract in ["正式工(计件工资)", "实习生(计件)"]:
            #     # 应发工资1 = 正常薪资 + 津贴 + 绩效工资 - 扣款 + 社保津贴
            #     record.salary_payable1 = record.pay_now + allowance + record.performance_pay - deduct_money + record.social_security_allowance
            # else:
            #     # 应发工资1 = 正常薪资 + 津贴 + 绩效工资 - 扣款
            #     record.salary_payable1 = record.pay_now + allowance + record.performance_pay - deduct_money
            # 应发工资1 = 正常薪资 + 补贴 + 绩效工资 - 扣款
            if record.efficiency_wages and record.contract not in ["正式工(B级管理)", "正式工(A级管理)"]:

                if record.first_level_department.parent_id.name == "车间" and record.first_level_department.name != "整件组":
                    record.salary_payable1 = record.efficiency_wages + allowance + record.performance_pay - deduct_money
                else:
                    record.salary_payable1 = record.pay_now + allowance + record.performance_pay - deduct_money
            else:
                record.salary_payable1 = record.pay_now + allowance + record.performance_pay - deduct_money

    # 计算赔偿
    def set_compensation(self) -> float:
        ''' 计算赔偿 罚单'''

        if "reward_punish_record" in self.env and self.date:

            this_month = self.set_begin_and_end()

            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                ("emp_id", "=", self.name.id),
                ("declare_time", ">=", this_month["begin"]),
                ("declare_time", "<=", this_month["end"]),
                ("state", "=", "审批通过"),
                ("record_type", "=", "compensation")
            ])
            if reward_punish_record_objs:

                return sum(reward_punish_record_objs.mapped('money_amount'))

            else:
                return 0
        else:
            return 0

    def current_month_in_service_days(self, this_month_start, this_month_end):
        ''' 计算当月在职日期范围'''

        if self.entry_time < this_month_start:
            if not self.name.is_delete or self.is_delete_date > this_month_end:
                return this_month_start, this_month_end
            else:
                return this_month_start, self.is_delete_date
        else:
            if not self.is_delete_date or self.is_delete_date > this_month_end:
                return self.entry_time, this_month_end
            else:
                return self.entry_time, self.is_delete_date

    def set_compensatio2(self):
        ''' 计算赔偿 生成进度表 报次库存和工厂交付差值'''

        this_month = self.set_begin_and_end()

        start_date, end_date = self.current_month_in_service_days(this_month.get("begin").date(),
                                                                  this_month.get("end").date())

        schedule_production_objs = self.env['schedule_production'].sudo().search(
            [("date_contract", ">=", start_date), ("date_contract", "<=", end_date), ("processing_type", "!=", "返修")])

        return sum(i.defective_number + i.factory_delivery_variance for i in schedule_production_objs) * 8

    # 计算应发工资2 = 应该发工资1 + 客户补贴 - 赔偿 + 绩效奖金 + 提成
    @api.depends('salary_payable1', 'customer_subsidy', 'performance_bonus', 'is_grant_performance_bonus',
                 'commission_bonus', 'is_grant_commission_bonus')
    def set_salary_payable2(self):
        for record in self:

            max_compensation = (record.salary_payable1 + record.customer_subsidy) * 0.3

            if record.job_id.name in ["厂长", "品控主管", "生产总监"]:
                temp_compensation = record.set_compensation() + record.set_compensatio2()
            else:
                temp_compensation = record.set_compensation()

            if temp_compensation == 0:
                record.compensation = 0
            elif temp_compensation > max_compensation:
                record.compensation = max_compensation
            else:
                record.compensation = temp_compensation

            if record.is_grant_commission_bonus:
                if record.is_grant_performance_bonus:
                    # 应发工资2 = 应发工资1 + 客户补贴 - 赔偿 + 绩效奖金 + 提成
                    record.salary_payable2 = record.salary_payable1 + record.customer_subsidy - record.compensation + record.performance_bonus + record.commission_bonus
                else:
                    record.salary_payable2 = record.salary_payable1 + record.customer_subsidy - record.compensation + record.commission_bonus
            else:
                if record.is_grant_performance_bonus:
                    # 应发工资2 = 应发工资1 + 客户补贴 - 赔偿 + 绩效奖金
                    record.salary_payable2 = record.salary_payable1 + record.customer_subsidy - record.compensation + record.performance_bonus
                else:
                    record.salary_payable2 = record.salary_payable1 + record.customer_subsidy - record.compensation

    # 应发工资3 = 应发工资2 - （房补扣款 + 饭补扣款 + 宿舍水电物业费 + 已预支 + 离职补贴）
    @api.depends('salary_payable2', 'rice_tonic', 'dormitory_water_and_electricity_deduction', 'rent_deduction',
                 'dimission_subsidy')
    def set_salary_payable3(self):
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
            # 饭补扣款 宿舍水电物业费 房补扣款 预支
            deductions = record.rice_tonic + record.dormitory_water_and_electricity_deduction + record.rent_deduction + record.advanced

            record.salary_payable3 = record.salary_payable2 - deductions + record.dimission_subsidy

    def set_dimission_subsidy(self):
        for record in self:

            # 如果离职了
            if record.name.is_delete:

                # 查询扣款设置里面的离职补贴设置
                deduct_money_setting_obj = self.env["deduct_money_setting"].sudo().search([("month", "=", record.date)])
                # 如果扣款设置里面设置了离职补贴
                if deduct_money_setting_obj.is_dimission_subsidy:
                        # 并且离职性质为“急辞”
                    if record.name.dimission_nature == "急辞":

                        if (record.salary_payable1 * 0.3) > 0:
                                # 离职补贴
                            record.dimission_subsidy = -(record.salary_payable1 * 0.3)
                        else:
                                # 离职补贴
                            record.dimission_subsidy = (record.salary_payable1 * 0.3)
            # 饭补扣款 宿舍水电物业费 房补扣款 预支
            deductions = record.rice_tonic + record.dormitory_water_and_electricity_deduction + record.rent_deduction + record.advanced

            record.salary_payable3 = record.salary_payable2 - deductions + record.dimission_subsidy

    # 获取当月第一天和最后一天
    def set_begin_and_end(self):
        ''' 获取当月第一天和最后一天'''

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
            date_end_of_the_month6 = datetime.datetime.strptime(date_end_of_the_month5,
                                                                '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59,
                                                                                                 seconds=59)  # 当月最后一天

            date_end = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')  # 当月第一天

            return {"begin": date_end, "end": date_end_of_the_month6}

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

            matter_days = 0  # 事假
            disease_days = 0  # 病假

            for every_detail_obj in every_detail_objs:

                tem_matter_days = 0  # 事假临时变量
                tem_disease_days = 0  # 病假临时变量
                rest_days = 0  # 休息天数

                # 查询>= 请假开始时间 和<= 请假结束时间的日历，获取请假中的休息天数
                custom_calendar_objs = self.env["custom.calendar"].sudo().search([
                    ('date', '>=', every_detail_obj.date + datetime.timedelta(hours=8)),
                    ('date', '<=', every_detail_obj.end_date + datetime.timedelta(hours=8)),
                ])
                if custom_calendar_objs:
                    # 休息天数
                    for custom_calendar_obj in custom_calendar_objs:
                        custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                            ("custom_calendar_id", "=", custom_calendar_obj.id),  # 日历id
                            ("department", "=", department_id)  # 部门id
                        ])
                        if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                            rest_days = rest_days + 1
                        elif rest_type == "大小休" and (
                                custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                            rest_days = rest_days + 1
                        elif rest_type == "双休" and (
                                custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
                            rest_days = rest_days + 1

                # 如果没有请假条
                if every_detail_obj.are_there_any_leave_slips == False:

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


                    elif every_detail_obj.reason_for_leave2 == "病假":

                        tem_disease_days = (every_detail_obj.end_date - every_detail_obj.date).days
                        if tem_disease_days == 0:
                            if every_detail_obj.days > 2:
                                tem_disease_days = 1
                        else:
                            tem_disease_days = tem_disease_days + 1

                        # 减去休息天数
                        tem_disease_days = tem_disease_days - rest_days

                matter_days = matter_days + tem_matter_days
                disease_days = disease_days + tem_disease_days

            self.matter_days = matter_days  # 事假(天)
            self.disease_days = disease_days  # 病假(天)

    # 获取本月全部的天
    def get_this_month_days(self):

        date = str(self.date)
        date2 = date.split('-')
        year = int(date2[0])
        month = int(date2[1])

        num_days = calendar.monthrange(year, month)[1]  ## 最后一天
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_days)

        entry_date = self.name.entry_time  # 入职日期
        dimission_date = self.name.is_delete_date  # 离职日期

        scope_1 = 0
        scope_2 = 0

        if entry_date < start_date:
            if dimission_date:
                if dimission_date > end_date:
                    days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
                elif dimission_date == end_date:
                    days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
                    days = days[0: -1]
                else:
                    days = [datetime.date(year, month, day) for day in range(1, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        else:
            if dimission_date:
                if dimission_date > end_date:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days + 1)]
                elif dimission_date == end_date:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days + 1)]
                    days = days[0: -1]
                else:
                    days = [datetime.date(year, month, day) for day in range(entry_date.day, dimission_date.day)]
            else:
                days = [datetime.date(year, month, day) for day in range(entry_date.day, num_days + 1)]

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
                    every_detail_objs = self.env["every.detail"].sudo().search([
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
                    every_detail_objs = self.env["every.detail"].sudo().search([
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
                every_detail_objs = self.env["every.detail"].sudo().search([
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

    def is_workshop(self):
        for record in self:
            # 获取部门id
            department_obj = record.first_level_department

            while True:
                if department_obj.name == "车间" or department_obj.name == "后道部":
                    return True
                else:
                    if department_obj.parent_id:
                        if department_obj.parent_id.name == "车间":
                            return True
                        else:
                            department_obj = department_obj.parent_id
                            continue
                    else:
                        return False

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

        #if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)':
        if self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            # 循环当月的全部天
            for day in self.get_this_month_days():
                # 先查询日历
                custom_calendar_obj = self.env["custom.calendar"].sudo().search([
                    ("date", "=", day)
                ])
                # 如果日历有记录
                if custom_calendar_obj:
                    custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                        ("custom_calendar_id", "=", custom_calendar_obj.id),  # 日历id
                        ("department", "=", department_id)  # 部门id
                    ])
                    if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                        pass
                    elif rest_type == "大小休" and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                        pass
                    elif rest_type == "双休" and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
                        pass
                    # 如果不休息
                    else:

                        if self.is_workshop():
                            group_attendance_objs = self.env["auto_employee_information"].sudo().search([
                                ("employee_id", "=", self.name.id),
                                ("date", "=", day),
                            ])
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
                            every_detail_objs = self.env["every.detail"].sudo().search([
                                ("leave_officer", "=", self.name.id),
                                ("date", "<=", day),
                                ("end_date", ">=", day)
                            ])
                            # 如果查到了
                            if every_detail_objs:
                                pass
                            # 如果没查到
                            else:
                                exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                                    ("start_date", "<=", day),
                                    ("end_date", ">=", day),
                                    ("employee_id", "=", self.name.id)
                                ])
                                if exchange_rest_use_line_obj:
                                    pass

                                else:
                                    tem_absenteeism_days = tem_absenteeism_days + 1
                else:
                    if self.is_workshop():
                        group_attendance_objs = self.env["auto_employee_information"].sudo().search([
                            ("employee_id", "=", self.name.id),
                            ("date", "=", day),
                        ])
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
                        every_detail_objs = self.env["every.detail"].sudo().search([
                            ("leave_officer", "=", self.name.id),
                            ("date", "<=", day),
                            ("end_date", ">=", day)
                        ])
                        # 如果查到了
                        if every_detail_objs:
                            pass
                        # 如果没查到
                        else:
                            exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                                ("start_date", "<=", day),
                                ("end_date", ">=", day),
                                ("employee_id", "=", self.name.id)
                            ])
                            if exchange_rest_use_line_obj:
                                pass

                            else:
                                tem_absenteeism_days = tem_absenteeism_days + 1


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
                        ("custom_calendar_id", "=", custom_calendar_obj.id),  # 日历id
                        ("department", "=", department_id)  # 部门id
                    ])
                    print(custom_calendar_obj.date, department_id)
                    if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                        pass
                    elif rest_type == "大小休" and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                        pass
                    elif rest_type == "双休" and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
                        pass
                    # 如果不休息
                    else:
                        tem_absenteeism_days = tem_absenteeism_days + self.set_absenteeism_punch_card(day)


                else:
                    tem_absenteeism_days = tem_absenteeism_days + self.set_absenteeism_punch_card(day)

        self.absenteeism_days = tem_absenteeism_days  # 旷工(天)

    # 房补计算（薪酬之外）
    def set_rental_allowance(self):

        if self.name.is_dormitory == "入住":
            pass
        else:
            if self.should_attend:
                # （房补基数/应出勤天数) * 实出勤天数

                return (self.name.housing_subsidy_limit / self.should_attend) * self.clock_in_time
            else:
                return 0

    # 房补计算（薪酬之内）
    def set_rental_allowance_interior(self):

        if self.should_attend:
            # （房补基数/应出勤天数) * 实出勤天数
            return (self.name.housing_subsidy_limit / self.should_attend) * self.clock_in_time
        else:
            return 0

    # 房补扣款（薪酬之外）
    def set_rent_deduction(self):

        if self.name.is_dormitory == "入住":

            # 如果不是全勤
            if self.should_attend != self.clock_in_time:
                # 如果有请假或矿工
                if self.matter_days or self.disease_days or self.absenteeism_days:

                    tem_rent_deduction = (self.name.housing_subsidy_limit / self.should_attend) * (
                                self.matter_days + self.disease_days + self.absenteeism_days)
                    return tem_rent_deduction

                else:
                    return 0

            else:
                return 0
        else:
            return 0

    # 房补扣款（薪酬之内）
    def set_rent_deduction_interior(self):
        if self.name.is_dormitory == "入住":
            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            this_month_first_day = this_month["begin"].date()  # 这个月第一天
            this_month_last_day = this_month["end"].date()  # 这个月最后一条
            entry_date = self.name.entry_time  # 入职日期
            dimission_date = self.name.is_delete_date  # 离职日期

            before_job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day,
                                                      this_month_last_day)

            tem_rent_deduction = (self.name.housing_subsidy_limit / 30.5) * before_job_days

            if tem_rent_deduction > self.name.housing_subsidy_limit:
                return self.name.housing_subsidy_limit
            else:
                return tem_rent_deduction

    # 饭补计算
    def set_rice_tonic(self, entry_time, departure_date, first_day, last_day):

        # 查询有没有退卡记录
        refill_card_return_obj = self.env["refill_card_return"].sudo().search([
            ("employee_id", "=", self.name.id),
            ("month", "=", self.date)
        ])
        if refill_card_return_obj:
            # 饭补，饭补扣款
            return refill_card_return_obj.recharge_amount, refill_card_return_obj.refund_amount
        else:
            # 查询饭补基数set_up_base_objs.rice_tonic
            this_month = self.set_begin_and_end()
            last_day = this_month["end"]  # 当月最后一天
            first_day = this_month["begin"]  # 当月第一天

            meal_subsidy_top_up_obj = self.env["meal_subsidy_top_up"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("name", "=", self.name.id)
            ])

            if meal_subsidy_top_up_obj:

                # 饭补，饭补扣款 = 饭补额度 * （1-（实际出勤/饭卡充值里面的出勤天数）)
                return meal_subsidy_top_up_obj.amount, meal_subsidy_top_up_obj.amount * (
                            1 - (self.clock_in_time / meal_subsidy_top_up_obj.attendance_day))
            else:
                return 0, 0

    # 设置全勤奖  入职时间 当月第一天 当月最后一天
    def set_perfect_attendance(self, entry_time, first_day, last_day):

        attendance_bonus_limit = self.name.attendance_bonus_limit

        # 本月之前入职
        if entry_time <= first_day:

            # 未离职或离职时间在本月之后
            if not self.name.is_delete_date:

                # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                if self.should_attend == self.clock_in_time:

                    return attendance_bonus_limit
                else:
                    return 0

            else:

                if self.name.is_delete_date >= last_day.date():

                    # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                    if self.should_attend == self.clock_in_time:

                        return attendance_bonus_limit
                    else:
                        return 0

                else:

                    return 0

        else:
            return 0

    # 设置工资之内的全勤奖计算
    def set_internal_perfect_attendance(self, entry_time, first_day, last_day):

        attendance_bonus_limit = self.name.attendance_bonus_limit
        # 本月之前入职
        if entry_time <= first_day:

            # 未离职或离职时间在本月之后
            if not self.name.is_delete_date:

                # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                if self.should_attend == self.clock_in_time:

                    return 0
                else:
                    return attendance_bonus_limit

            else:

                if self.name.is_delete_date >= last_day.date():

                    # 如果应出勤天数 等于 实出勤天数则有全勤奖，否则没有全勤奖
                    if self.should_attend == self.clock_in_time:

                        return 0
                    else:
                        return attendance_bonus_limit

                else:

                    return attendance_bonus_limit
        #如果是本月入职扣除 attendance_bonus_limit*（实出勤/应出勤）
        elif entry_time > first_day:
            attendance_bonus_limit_no_month = attendance_bonus_limit*(self.clock_in_time/self.should_attend)
            return attendance_bonus_limit_no_month

    # # 设置工资之内的全勤奖计算
    # def set_internal_perfect_attendance(self):

    #     attendance_bonus_limit = self.name.attendance_bonus_limit

    #     if self.should_attend == self.clock_in_time:

    #         return 0
    #     else:

    #         return attendance_bonus_limit

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
                elif rest_type == "大小休" and (
                        custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息"):

                    date_end = date_end + datetime.timedelta(days=1)
                    continue
                elif rest_type == "双休" and (
                        custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息" or custom_calendar_line_obj.state == "仅双休休息"):

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

            date_end_of_the_month6 = this_month["end"]  # 当月最后一天
            date_end = this_month["begin"]  # 当月第一天
            date_fanbu = datetime.datetime.strptime(str(record.entry_time), '%Y-%m-%d')  # 入职时间
            if record.is_delete_date:
                departure_date = datetime.datetime.strptime(str(record.is_delete_date), '%Y-%m-%d')  # 离职时间
            else:
                departure_date = False

            if record.name.attendance_bonus_type == "薪酬之外":

                # 全勤奖查询日历
                first_day = record.attendance_bonus_calendar(date_end)

                record.perfect_attendance_award = record.set_perfect_attendance(date_fanbu, first_day,
                                                                                date_end_of_the_month6)
            elif record.name.attendance_bonus_type == "薪酬之内":
                #未全勤扣款  本月入职 未全勤扣款 = 300*实出勤天数/应出勤； 不在本月入职  未全勤扣款 = 300
                #全勤：应出勤>=实出勤  未全勤：应出勤<实出勤
                # 全勤奖查询日历
                first_day = record.attendance_bonus_calendar(date_end)

                record.perfect_attendance_award = -record.set_internal_perfect_attendance(date_fanbu, first_day,
                                                                                          date_end_of_the_month6)
            else:
                pass

            # 房补和房补扣款
            if record.name.housing_subsidy_type == "薪酬之外":
                record.rental_allowance = record.set_rental_allowance()
                record.rent_deduction = record.set_rent_deduction()
            elif record.name.housing_subsidy_type == "薪酬之内":
                record.rental_allowance = record.set_rental_allowance_interior()
                record.rent_deduction = record.set_rent_deduction_interior()

            # 饭补和饭补扣款
            if record.name.meal_allowance_type == "薪酬之外":
                # 饭补扣款(入职时间, 当月第一天, 当月最后一天)
                record.meal_allowance, record.rice_tonic = record.set_rice_tonic(date_fanbu, departure_date, date_end,
                                                                                 date_end_of_the_month6)
            else:
                if record.name.is_it_a_temporary_worker == '正式工(计件工资)' or record.name.is_it_a_temporary_worker == '临时工' or record.name.is_it_a_temporary_worker == '实习生(计件)':
                    record.meal_allowance = 0
                    record.rice_tonic = record.name.meal_allowance_limit - (
                                (record.name.meal_allowance_limit / record.should_attend) * record.clock_in_time)
                else:
                    record.meal_allowance = 0
                    record.rice_tonic = 0

            # 招聘奖金
            record.recruitment_reward = record.set_recruitment_reward(date_end, date_end_of_the_month6)

    # 设置招聘奖金
    def set_recruitment_reward(self, first_day, last_day):

        if self.name.department_id.name == "人事行政部":

            pass
        else:
            personnel_award_objs = self.env["personnel_award"].sudo().search([
                ("introducer", "=", self.name.id),  # 员工id
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

            if self.is_workshop():
                group_attendance_objs = self.env["auto_employee_information"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("date", "=", dDate),
                ])
            else:

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
                every_detail_objs = self.env["every.detail"].sudo().search([
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
        every_detail_objs = self.env["every.detail"].sudo().search([
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
                    elif rest_type == "大小休" and (
                            custom_calendar_line_objs.state == "休息" or custom_calendar_line_objs.state == "大小休休息"):
                        pass
                    elif rest_type == "双休" and (
                            custom_calendar_line_objs.state == "休息" or custom_calendar_line_objs.state == "大小休休息" or custom_calendar_line_objs.state == "仅双休休息"):
                        pass
                    else:
                        # 判断是否旷工或请假
                        if self.query_absenteeism(come_to_work_obj.date) or self.query_leave(
                                come_to_work_obj.date) or self.query_reissue_a_card(come_to_work_obj.date):
                            pass
                        else:
                            tem_total_time = tem_total_time + (
                                        come_to_work_obj.minutes_late + come_to_work_obj.total_time_early)

                else:
                    # 判断是否旷工或请假
                    if self.query_absenteeism(come_to_work_obj.date) or self.query_leave(
                            come_to_work_obj.date) or self.query_reissue_a_card(come_to_work_obj.date):
                        pass
                    else:
                        tem_total_time = tem_total_time + (
                                    come_to_work_obj.minutes_late + come_to_work_obj.total_time_early)

        # 迟到早退分钟数
        self.be_late_time = tem_total_time

        # 如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工":
                self.late_arrival_and_early_refund_deduction = (self.pay_now * (
                            tem_total_time / (21.75 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio
        if self.name.is_it_a_temporary_worker == '临时工':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":
                self.late_arrival_and_early_refund_deduction = (self.pay_now * (
                            tem_total_time / (21.75 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio

        else:
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":
                self.late_arrival_and_early_refund_deduction = (self.name.fixed_salary * (
                            tem_total_time / (26 * 8 * 60))) * deduct_money_setting_obj.be_late_deduct_money_ratio

    # 请假扣款
    def set_ask_for_leave_deduct_money(self, deduct_money_setting_obj):
        if self.name.time_plan == "8:00 - 21:00, 单休":
            leave_house_day = 11.5
        elif self.name.time_plan == "9:00 - 18:00, 单休" or self.name.time_plan == "9:00 - 18:00, 大小休" or self.name.time_plan == "9:00 - 18:00, 双休":
            leave_house_day = 8
        elif self.name.time_plan == "8:00 - 18:00, 单休":
            leave_house_day = 9
        elif self.name.time_plan == "7:30 - 17:00, 单休":
            leave_house_day = 7.5
        elif self.name.time_plan == "8:00 - 19:00, 单休":
            leave_house_day = 10
        #如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':
            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工":
                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (
                            self.pay_now / (21.75 * leave_house_day))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "仅计件工种" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "非临时工":
                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (
                            self.pay_now / (21.75 * leave_house_day))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio

        # 如果是临时工
        elif self.name.is_it_a_temporary_worker == '临时工':

            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":
                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (
                            self.pay_now / (21.75 * leave_house_day))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "仅临时工" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "非计件工种":
                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (
                            self.pay_now / (21.75 * leave_house_day))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio


        else:

            if deduct_money_setting_obj.matter_vacation_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件和临时工" or \
                    deduct_money_setting_obj.matter_vacation_deduct_money == "非计件工种":
                # (事假（小时）*(正常工资/(21.75 * 8))) * 事假扣款比例
                self.leave_deduction = (self.leave_days * (self.name.fixed_salary / (
                            26 * leave_house_day))) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

            if deduct_money_setting_obj.sick_leave_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "非临时工" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "非计件和临时工" or \
                    deduct_money_setting_obj.sick_leave_deduct_money == "非计件工种":
                # (病假（小时）*(正常工资/(21.75 * 8))) * 病假扣款比例
                self.sick_leave_deduction = (self.sick_leave_days * (
                            self.name.fixed_salary / (26 * leave_house_day))) * deduct_money_setting_obj.sick_leave_deduct_money_ratio

    # 旷工扣款
    def set_absenteeism_deduct_money(self, deduct_money_setting_obj):

        if self.name.time_plan.startswith('8:00 - 21:00'):
            temp_hous = 11.5
        elif self.name.time_plan.startswith('9:00 - 18:00'):
            temp_hous = 8
        else:
            temp_hous = 9

        # 如果是计件工种
        if self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '实习生(计件)':

            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "仅计件工种" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "非临时工":
                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.pay_now / (
                            21.75 * temp_hous))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio

        elif self.name.is_it_a_temporary_worker == '临时工':

            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "仅临时工" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "仅计件和临时工" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "非计件工种":
                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.pay_now / (
                            21.75 * temp_hous))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio

        else:
            if deduct_money_setting_obj.absenteeism_deduct_money == "全部工种" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "非临时工" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "非计件和临时工" or \
                    deduct_money_setting_obj.absenteeism_deduct_money == "非计件工种":
                # 旷工（小时）* (正常工资/(21.75 * 8))) * 旷工扣款比例
                self.absenteeism_deduction = (self.absenteeism_time * (self.name.fixed_salary / (
                            26 * temp_hous))) * deduct_money_setting_obj.absenteeism_deduct_money_ratio

    def get_reward_punish_record_money_amount(self, is_day, first_day, last_day):

        reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
            ("emp_id", "=", self.name.id),
            ("declare_time", ">=", first_day),
            ("declare_time", "<=", last_day),
            ("state", "=", "审批通过"),
            ("record_type", "=", "punish")
        ])

        money_amount = sum(reward_punish_record_objs.mapped('money_amount'))#获取金额

        if is_day:
            performance_money = (self.name.performance_money / 26) * self.clock_in_time
        else:
            performance_money = self.name.performance_money

        if performance_money:
            if performance_money < money_amount:
                return performance_money
            else:
                return money_amount
        else:
            return money_amount

    # 设置绩效扣除或绩效奖金(奖罚记录单)
    def set_performance_data(self, first_day, last_day):

        if self.transfer_number:#是否有调岗信息
            transfer_number_objs = self.env["internal.post.transfer"].sudo().search([
                ("name", "=", self.name.id),
                ("begin_start", ">=", first_day),
                ("begin_start", "<=", last_day),
            ], order='begin_start')

            num = 0

            for i, transfer_number_obj in enumerate(transfer_number_objs):

                if i == 0 and i == len(transfer_number_objs) - 1:#如果本月只有一个转岗信息

                    before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                        ("job_id", "=", transfer_number_obj.raw_job_id.id),
                        ("frequency_distribution", ">", 1)#frequency_distribution = fields.Integer(string="发放频率（每几个月一次发放一次）")
                    ])
                    if not before_post_performance_setting_obj:
                        reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                            ("emp_id", "=", self.name.id),
                            ("declare_time", ">=", first_day),
                            ("declare_time", "<", transfer_number_obj.begin_start),
                            ("state", "=", "审批通过"),
                            ("record_type", "=", "punish")
                        ])
                        num += sum(reward_punish_record_objs.mapped('money_amount'))

                    after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                        ("job_id", "=", transfer_number_obj.job_id.id),
                        ("frequency_distribution", ">", 1)
                    ])

                    if not after_post_performance_setting_obj:
                        reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                            ("emp_id", "=", self.name.id),
                            ("declare_time", ">=", transfer_number_obj.begin_start),
                            ("declare_time", "<", last_day + datetime.timedelta(days=1)),
                            ("state", "=", "审批通过"),
                            ("record_type", "=", "punish")
                        ])
                        num += sum(reward_punish_record_objs.mapped('money_amount'))

                else:

                    if i == 0:

                        before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                            ("job_id", "=", transfer_number_obj.raw_job_id.id),
                            ("frequency_distribution", ">", 1)
                        ])
                        if not before_post_performance_setting_obj:
                            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                                ("emp_id", "=", self.name.id),
                                ("declare_time", ">=", first_day),
                                ("declare_time", "<", transfer_number_obj.begin_start),
                                ("state", "=", "审批通过"),
                                ("record_type", "=", "punish")
                            ])
                            num += sum(reward_punish_record_objs.mapped('money_amount'))

                    elif i == len(transfer_number_objs) - 1:

                        after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                            ("job_id", "=", transfer_number_obj.job_id.id),
                            ("frequency_distribution", ">", 1)
                        ])

                        if not after_post_performance_setting_obj:
                            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                                ("emp_id", "=", self.name.id),
                                ("declare_time", ">=", transfer_number_obj[i - 1].begin_start),
                                ("declare_time", "<", transfer_number_obj.begin_start),
                                ("state", "=", "审批通过"),
                                ("record_type", "=", "punish")
                            ])
                            num += sum(reward_punish_record_objs.mapped('money_amount'))

                        after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                            ("job_id", "=", transfer_number_obj.job_id.id),
                            ("frequency_distribution", ">", 1)
                        ])

                        if not after_post_performance_setting_obj:
                            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                                ("emp_id", "=", self.name.id),
                                ("declare_time", ">=", transfer_number_obj.begin_start),
                                ("declare_time", "<", last_day + datetime.timedelta(days=1)),
                                ("state", "=", "审批通过"),
                                ("record_type", "=", "punish")
                            ])
                            num += sum(reward_punish_record_objs.mapped('money_amount'))

                    else:

                        after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                            ("job_id", "=", transfer_number_obj.job_id.id),
                            ("frequency_distribution", ">", 1)
                        ])

                        if not after_post_performance_setting_obj:
                            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                                ("emp_id", "=", self.name.id),
                                ("declare_time", ">=", transfer_number_obj[i - 1].begin_start),
                                ("declare_time", "<", transfer_number_obj.begin_start),
                                ("state", "=", "审批通过"),
                                ("record_type", "=", "punish")
                            ])
                            num += sum(reward_punish_record_objs.mapped('money_amount'))

            self.performance_bonus = 0
            self.other_deductions = num

        else:

            if not self.env['post_performance_setting'].sudo().search(
                    [("job_id", "=", self.job_id.id), ("frequency_distribution", ">", 1)]):
                self.performance_bonus = 0

                # if self.job_id.name == "人事招聘专员":
                #     if self.counting_number_recruits(first_day, last_day) < 10:

                #         self.other_deductions = self.get_reward_punish_record_money_amount(False, first_day, last_day) + 1000
                #     else:
                #         self.other_deductions = self.get_reward_punish_record_money_amount(False, first_day, last_day)
                # else:

                #     self.other_deductions = self.get_reward_punish_record_money_amount(False, first_day, last_day)
                self.other_deductions = self.get_reward_punish_record_money_amount(False, first_day, last_day)

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
                # 设置绩效扣除或绩效奖金
                record.set_performance_data(this_month_first_day, this_month_last_day)
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

            # 水电费
            demo = self.env['dormitory.property'].sudo().search([
                ('month', '=', record.date),
                ('name', '=', record.name.id)
            ])
            if demo:
                # 水电物业费扣款
                record.dormitory_water_and_electricity_deduction = demo.water_and_electricity_property_fee_deduction

    @api.constrains('date', 'name')
    def check_date(self):
        def is_valid_date(strdate):
            '''判断是否是一个有效的日期字符串'''
            try:
                if "-" in strdate:
                    if strdate.split('-')[1] in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                                                 '12']:
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
        demo = self.sudo().search([
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
                        if department_id == custom_calendar_line_id.department.id and (
                                custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                            rest_days = rest_days + 1
                elif rest_type == "双休":
                    for custom_calendar_line_id in custom_calendar_obj.custom_calendar_line_ids:
                        if department_id == custom_calendar_line_id.department.id and (
                                custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
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
        punch_in_record_obj = self.env["punch.in.record"].sudo().search(
            [("date", "=", day), ("employee", "=", self.name.id)])

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
            if  (record.name.is_it_a_temporary_worker == '正式工(计件工资)'):
                this_month = record.set_begin_and_end()
                name_list_data = []
                punch_in_objs = self.env["punch.in.record"].sudo().search([
                        ("employee.name", "=", record.name.name),
                        ("date", ">=", this_month["begin"]),
                        ("date", "<=", this_month["end"])
                    ])
                for punch_in_obj in punch_in_objs:
                    name_list_data.append(punch_in_obj.date)
                name_list_data = list(set(name_list_data))
                clock_in_time = len(name_list_data)
                print(clock_in_time)
                if clock_in_time > record.should_attend:

                    record.clock_in_time = record.should_attend
                else:
                    record.clock_in_time = clock_in_time
                    




            #if (record.name.is_it_a_temporary_worker == '正式工(计件工资)' or record.name.is_it_a_temporary_worker == '临时工' or record.name.is_it_a_temporary_worker == '实习生(计件)') and record.name.job_id.name != "整件":
            if (record.name.is_it_a_temporary_worker == '临时工' or record.name.is_it_a_temporary_worker == '实习生(计件)') and record.name.job_id.name != "整件":
                this_month = record.set_begin_and_end()

                name_list = []

                if record.is_workshop():
                   
                    memp_memp_objs = self.env["auto_employee_information"].sudo().search([
                        ("employee_id", "=", record.name.id),
                        ("date", ">=", this_month["begin"]),
                        ("date", "<=", this_month["end"])
                    ])
                else:
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

                # temp_days = 0
                # for i in name_list:
                #     custom_calendar_obj = self.env['custom.calendar'].sudo().search([("date", "=", i)])
                #     for j in custom_calendar_obj.custom_calendar_line_ids:
                #         if j.department.id == record.name.department_id.id:
                #             if j.state == "休息":
                #                 temp_days += 1
                # print(temp_days)
                # clock_in_time -= temp_days
                print(record.name.name,clock_in_time, record.name.id, record.name)
                # 如果实际出勤天数大于应出勤天数，则实际出勤天数=应出勤天数
                if clock_in_time > record.should_attend:
                    record.clock_in_time = record.should_attend
                else:
                    record.clock_in_time = clock_in_time

            else:

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
                        custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search(
                            [("custom_calendar_id", "=", custom_calendar_obj.id),
                             ("department", "=", record.first_level_department.id)])

                        if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                            is_rest = True
                        elif rest_type == "大小休" and (
                                custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息"):
                            is_rest = True
                        elif rest_type == "双休" and (
                                custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息" or custom_calendar_line_obj.state == "仅双休休息"):
                            is_rest = True
                    # 如果休息则跳过，如果不休息则查询考勤机 计算实出勤天数
                    if is_rest:
                        pass
                    else:
                        print(day, record.punch_card_and_fill_card(day))
                        clock_in_time = clock_in_time + record.punch_card_and_fill_card(day)

                record.clock_in_time = clock_in_time

    # 获取实际出勤日期列表
    def get_actual_attendance_days(self):

        #if (self.name.is_it_a_temporary_worker == '正式工(计件工资)' or self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)'):
        if self.name.is_it_a_temporary_worker == '临时工' or self.name.is_it_a_temporary_worker == '实习生(计件)':

            this_month = self.set_begin_and_end()

            if self.is_workshop():
                memp_memp_objs = self.env["auto_employee_information"].sudo().search([
                    ("employee_id", "=", self.name.id),
                    ("date", ">=", this_month["begin"]),
                    ("date", "<=", this_month["end"])
                ])
            else:
                # 查询统计中的员工信息表
                memp_memp_objs = self.env["memp.memp"].sudo().search([
                    ("employee", "=", self.name.id),
                    ("date", ">=", this_month["begin"]),
                    ("date", "<=", this_month["end"])
                ])

            return list(set(memp_memp_objs.mapped('date')))
        else:

            # 获取员工的休息类型(单休还是双休或者大小休息)
            rest_type = self.time_plan.split(' ')[-1]
            date_list = []
            # 循环当月全部天
            for day in self.get_this_month_days():

                # 默认为不休息
                is_rest = False
                # 先查询日历，这天是否是休息，如果查询到是休息，则将is_rest = True
                custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", day)])
                if custom_calendar_obj:
                    custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search(
                        [("custom_calendar_id", "=", custom_calendar_obj.id),
                         ("department", "=", self.first_level_department.id)])

                    if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                        is_rest = True
                    elif rest_type == "大小休" and (
                            custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息"):
                        is_rest = True
                    elif rest_type == "双休" and (
                            custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息" or custom_calendar_line_obj.state == "仅双休休息"):
                        is_rest = True
                # 如果休息则跳过，如果不休息则查询考勤机 计算实出勤天数
                if is_rest:
                    pass
                else:
                    if self.punch_card_and_fill_card(day):
                        date_list.append(day)
            return date_list

    # 计算月平均效率,效率薪资
    def set_month_workpiece_ratio(self):

        for record in self:
            # 判断是否是计件
            if record.name.is_it_a_temporary_worker == "正式工(计件工资)" \
                    or record.name.is_it_a_temporary_worker == "临时工" \
                    or record.name.is_it_a_temporary_worker == "实习生(计件)":
                # 获取当月第一天和最后一天
                this_month = record.set_begin_and_end()

                # 自动效率
                automatic_efficiency_table_objs = self.env["automatic_efficiency_table"].sudo().search([
                    ("date", ">=", this_month.get("begin")),
                    ("date", "<=", this_month.get("end")),
                    ("employee_id", "=", record.name.id)
                ])

                if automatic_efficiency_table_objs:

                    record.month_workpiece_ratio = sum(automatic_efficiency_table_objs.mapped('efficiency')) / len(
                        automatic_efficiency_table_objs)

                else:

                    record.month_workpiece_ratio = 0

                # 人工效率
                eff_eff_objs = self.env["eff.eff"].sudo().search([
                    ("date", ">=", this_month.get("begin")),
                    ("date", "<=", this_month.get("end")),
                    ("employee", "=", record.name.id)
                ])

                if eff_eff_objs:

                    record.manual_month_workpiece_ratio = sum(eff_eff_objs.mapped('totle_eff')) / len(eff_eff_objs)

                else:

                    record.manual_month_workpiece_ratio = 0

                if record.is_workshop():
                    # 设置自动效率薪资
                    record.set_efficiency_wages(record.month_workpiece_ratio)
                else:
                    # 设置手动效率薪资
                    record.set_efficiency_wages(record.manual_month_workpiece_ratio)

            else:
                record.efficiency_wages = self.calculate_the_performance_of_sample_workers(record)



                # continue
                # if record.job_id.name == "流水组长":
                #     record.efficiency_wages = record.set_group_leader_efficiency_wages(record.clock_in_time, record.first_level_department.id)
                #
                # if record.transfer_number > 1:
                #     raise ValidationError(f"{record.name.name}暂不支持多次调岗的薪资计算！")
                # elif record.transfer_number == 1:
                #     record.efficiency_wages = record.management_efficiency_pay_calculation()
                # else:
                #     if record.job_id.name == "流水组长":
                #         record.efficiency_wages = record.set_group_leader_efficiency_wages(record.clock_in_time, record.first_level_department.id)
                #     elif record.job_id.name == "品控主管":
                #         record.efficiency_wages = record.set_qc_supervisor_efficiency_wages(record.name.fixed_salary, record.clock_in_time, record.get_actual_attendance_days())
                #     elif record.job_id.name == "后道主管":
                #         record.efficiency_wages = record.set_following_process_director_efficiency_wages(record.name.fixed_salary, record.clock_in_time, record.get_actual_attendance_days())
                #     elif record.job_id.name == "车间主任":
                #         record.efficiency_wages = record.set_workshop_director_efficiency_wages(record.name.fixed_salary, record.clock_in_time, record.get_actual_attendance_days())
                #     elif record.job_id.name == "裁床主管":
                #         record.efficiency_wages = record.set_cutting_bed_head_efficiency_wages(record.name.fixed_salary, record.clock_in_time, record.get_actual_attendance_days())
                #     elif record.job_id.name == "厂长":
                #         record.efficiency_wages = record.set_factory_director_efficiency_wages(record.name.fixed_salary, record.clock_in_time, record.get_actual_attendance_days())

    def calculate_the_performance_of_sample_workers(self, record):
        """样衣工薪资"""
        # 将字符串日期转换为datetime对象（假设为该月的第一天）
        date_obj = datetime.datetime.strptime(record.date + "-01", "%Y-%m-%d")
        # 获取当月的第一天和最后一天
        first_day = date_obj.replace(day=1)
        last_day = date_obj.replace(day=calendar.monthrange(date_obj.year, date_obj.month)[1])
        # 将日期转换为字符串格式
        first_day_str = first_day.strftime("%Y-%m-%d")
        last_day_str = last_day.strftime("%Y-%m-%d")

        if record.job_id.name == "样衣工":
            ret = self.env['th_per_management'].search([('employee_id', '=', record.name.id),
                                                        ('date', '>=', first_day_str), ('date', '<=', last_day_str)])
            total = 0.0
            for i in ret:
                s = self.env['mhp.mhp'].search([('order_number', '=', i.style_number.id)])
                for j in s:
                    total += (i.actual_production * j.totle_price)  # 累加计算结果
            return total


    # 管理效率薪资计算
    def management_efficiency_pay_calculation(self):
        # 获取当月第一天和最后一天
        this_month = self.set_begin_and_end()
        transfer_number_obj = self.env["internal.post.transfer"].sudo().search([
            ("name", "=", self.name.id),
            ("begin_start", ">=", this_month.get("begin")),
            ("begin_start", "<=", this_month.get("end")),
        ])
        if transfer_number_obj.adjust_salary:
            before_fixed_salary = transfer_number_obj.before_pay
            after_fixed_salary = transfer_number_obj.the_salary_adjustment_scheme
        else:
            before_fixed_salary = self.name.fixed_salary
            after_fixed_salary = self.name.fixed_salary

        if transfer_number_obj.raw_job_id.name == "流水组长":

            clock_in_time = len([i for i in self.get_actual_attendance_days() if i < transfer_number_obj.begin_start])

            before_pay = self.set_group_leader_efficiency_wages(clock_in_time, transfer_number_obj.department_id.id)
        elif transfer_number_obj.raw_job_id.name == "品控主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i < transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            before_pay = self.set_qc_supervisor_efficiency_wages(before_fixed_salary, clock_in_time,
                                                                 actual_attendance_days)
        elif transfer_number_obj.raw_job_id.name == "后道主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i < transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            before_pay = self.set_following_process_director_efficiency_wages(before_fixed_salary, clock_in_time,
                                                                              actual_attendance_days)
        elif transfer_number_obj.raw_job_id.name == "车间主任":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i < transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            before_pay = self.set_workshop_director_efficiency_wages(before_fixed_salary, clock_in_time,
                                                                     actual_attendance_days)
        elif transfer_number_obj.raw_job_id.name == "裁床主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i < transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            before_pay = self.set_cutting_bed_head_efficiency_wages(before_fixed_salary, clock_in_time,
                                                                    actual_attendance_days)
        elif transfer_number_obj.raw_job_id.name == "厂长":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i < transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            before_pay = self.set_factory_director_efficiency_wages(before_fixed_salary, clock_in_time,
                                                                    actual_attendance_days)
        else:
            before_pay = 0
        #     actual_attendance_days = [i for i in self.get_actual_attendance_days() if i < transfer_number_obj.begin_start]
        #     clock_in_time = len(actual_attendance_days)
        #     before_pay = (before_fixed_salary / self.should_attend) * clock_in_time

        if transfer_number_obj.job_id.name == "流水组长":

            clock_in_time = len([i for i in self.get_actual_attendance_days() if i >= transfer_number_obj.begin_start])

            after_pay = self.set_group_leader_efficiency_wages(clock_in_time,
                                                               transfer_number_obj.proposed_department.id)
        elif transfer_number_obj.job_id.name == "品控主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i >= transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            after_pay = self.set_qc_supervisor_efficiency_wages(after_fixed_salary, clock_in_time,
                                                                actual_attendance_days)
        elif transfer_number_obj.job_id.name == "后道主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i >= transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            after_pay = self.set_following_process_director_efficiency_wages(after_fixed_salary, clock_in_time,
                                                                             actual_attendance_days)
        elif transfer_number_obj.job_id.name == "车间主任":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i >= transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            after_pay = self.set_workshop_director_efficiency_wages(after_fixed_salary, clock_in_time,
                                                                    actual_attendance_days)
        elif transfer_number_obj.job_id.name == "裁床主管":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i >= transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            after_pay = self.set_cutting_bed_head_efficiency_wages(after_fixed_salary, clock_in_time,
                                                                   actual_attendance_days)
        elif transfer_number_obj.job_id.name == "厂长":
            actual_attendance_days = [i for i in self.get_actual_attendance_days() if
                                      i >= transfer_number_obj.begin_start]
            clock_in_time = len(actual_attendance_days)

            after_pay = self.set_factory_director_efficiency_wages(after_fixed_salary, clock_in_time,
                                                                   actual_attendance_days)

        else:
            after_pay = 0

        return before_pay + after_pay

    # 获取当月产值增量
    def get_warehouse_finished_product_stock_data(self, actual_attendance_days_list, process_type_list) -> float:

        warehouse_finished_product_stock_objs = self.env['warehouse_finished_product_stock'].sudo().search([
            ("date", "in", actual_attendance_days_list), ("processing_type", "in", process_type_list)
        ])

        return sum(i.change_stock_production_value for i in warehouse_finished_product_stock_objs)

        # 获取当月退货产值

    def get_return_good_output_value(self, actual_attendance_days) -> float:

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        return sum(float(i.order_number.order_price) * i.number for i in return_good_objs)

    # 厂长效率薪资
    def set_factory_director_efficiency_wages(self, fixed_salary, clock_in_time, actual_attendance_days) -> float:

        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂", "外发"])

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        total_price = stock_output_increase - sum(
            float(i.order_number.order_price) * i.number for i in return_good_objs)

        if self.calculation == "按天计算":
            return ((fixed_salary / 26) * clock_in_time) + total_price * 0.003
        else:
            return ((fixed_salary / self.should_attend) * clock_in_time) + total_price * 0.003

    # 裁床主管效率薪资
    def set_cutting_bed_head_efficiency_wages(self, fixed_salary, clock_in_time, actual_attendance_days) -> float:

        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂"])

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        total_price = stock_output_increase - sum(
            float(i.order_number.order_price) * i.number for i in return_good_objs)

        if self.calculation == "按天计算":
            return ((fixed_salary / 26) * clock_in_time) + total_price * 0.003
        else:
            return ((fixed_salary / self.should_attend) * clock_in_time) + total_price * 0.003

    # 车间主任效率薪资
    def set_workshop_director_efficiency_wages(self, fixed_salary, clock_in_time, actual_attendance_days) -> float:

        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂"])

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        total_price = stock_output_increase - sum(
            float(i.order_number.order_price) * i.number for i in return_good_objs)

        if self.calculation == "按天计算":
            return ((fixed_salary / 26) * clock_in_time) + total_price * 0.003
        else:
            return ((fixed_salary / self.should_attend) * clock_in_time) + total_price * 0.003

    # 后道主管效率薪资
    def set_following_process_director_efficiency_wages(self, fixed_salary, clock_in_time,
                                                        actual_attendance_days) -> float:

        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂"])

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        total_price = stock_output_increase - sum(
            float(i.order_number.order_price) * i.number for i in return_good_objs)

        if self.calculation == "按天计算":
            return ((fixed_salary / 26) * clock_in_time) + total_price * 0.003
        else:
            return ((fixed_salary / self.should_attend) * clock_in_time) + total_price * 0.003

    # 品控主管效率薪资
    def set_qc_supervisor_efficiency_wages(self, fixed_salary, clock_in_time, actual_attendance_days) -> float:

        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂", "外发"])

        return_good_objs = self.env['finished_product_ware_line'].sudo().search([
            ('date', "in", actual_attendance_days),
            ("type", "=", "入库"),
            ("character", "=", "退货"),
        ])

        total_price = stock_output_increase - sum(
            float(i.order_number.order_price) * i.number for i in return_good_objs)

        if self.calculation == "按天计算":
            return ((fixed_salary / 26) * clock_in_time) + total_price * 0.003
        else:
            return ((fixed_salary / self.should_attend) * clock_in_time) + total_price * 0.003

    # 流水组长效率薪资
    def set_group_leader_efficiency_wages(self, clock_in_time, department_id) -> float:

        if self.calculation == "按天计算":
            algorithm_one_wages = (self.set_group_leader_efficiency_wages_algorithm_one(
                department_id) / 26) * clock_in_time
        else:
            algorithm_one_wages = (self.set_group_leader_efficiency_wages_algorithm_one(
                department_id) / self.should_attend) * clock_in_time

        return algorithm_one_wages

    # 流水组长效率薪资 算法1（效率薪资）
    def set_group_leader_efficiency_wages_algorithm_one(self, department_id) -> float:

        pay_now_list = self.sudo().search_read(
            [("date", "=", self.date), ("first_level_department", "=", department_id), ("id", "!=", self.id)],
            ["pay_now"]
        )

        return sum(i['pay_now'] for i in pay_now_list) * 0.12

    # 流水组长效率薪资 算法2（正常薪资）
    def set_group_leader_efficiency_wages_algorithm_two(self, department_id=None) -> float:

        if not department_id:
            department_id = self.first_level_department.id

        on_job_list = []

        # 循环当月的全部天
        for day in self.get_this_month_days():
            on_job_number = self.env["hr.employee"].sudo().search_count([
                ("department_id", "=", department_id),
                ("entry_time", "<=", day),
                ("job_id.name", "in", ["流水车位", "小烫"]),
                "|", ("is_delete", "=", False), ("is_delete_date", ">", day)
            ])
            on_job_list.append(on_job_number)

        return self.env["group_leader_wages_setting"].sudo().search(
            [("employees_number", "=", min(on_job_list, default=0))]).salary_quota

    # 计件工人设置效率薪资
    def set_efficiency_wages(self, workpiece_ratio):

        if self.job_id.name == "后道大烫":

            config_obj = self.env["efficiency_wages_setting"].sudo().search([
                ("date", "=", self.date),
                ("type", "=", "大烫"),
            ])

        elif self.job_id.name == "裁床主刀":

            config_obj = self.env["efficiency_wages_setting"].sudo().search([
                ("date", "=", self.date),
                ("type", "=", "裁床主刀"),
            ])
        else:

            config_obj = self.env["efficiency_wages_setting"].sudo().search([
                ("date", "=", self.date),
                ("type", "=", "通用"),
            ])

        self.type_set_efficiency_wages(config_obj, workpiece_ratio)

    def type_set_efficiency_wages(self, config_obj, workpiece_ratio):

        if self.first_level_department.name == "裁床部":

            if self.job_id.name == "裁床主刀":

                total_efficiency_wages = config_obj.lowest_efficiency_wages + (
                            workpiece_ratio * config_obj.growth_numerical)
                # self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time
                self.efficiency_wages = (total_efficiency_wages / 26) * self.clock_in_time
            else:
                # (约定薪资 - (三项补贴 + 社保)) * 效率
                total_efficiency_wages = (self.name.fixed_salary - (
                            self.name.attendance_bonus_limit + self.name.meal_allowance_limit + self.name.housing_subsidy_limit + self.social_security_allowance)) * (
                                                     workpiece_ratio / 100)

                # self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time
                self.efficiency_wages = (total_efficiency_wages / 26) * self.clock_in_time

        elif self.job_id.name == "后道大烫":
            #基础效率工资 = 最低效率工资+（效率*增长数值）
            total_efficiency_wages = config_obj.lowest_efficiency_wages + (
                        workpiece_ratio * config_obj.growth_numerical)
            # self.efficiency_wages = (total_efficiency_wages / 26) * self.clock_in_time
            self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time

        else:
            if workpiece_ratio < 50:  # 效率小于50

                entry_time_year, entry_time_month, _ = str(self.name.entry_time).split("-")

                if self.name.is_it_a_temporary_worker == "正式工(计件工资)" and self.date == f"{entry_time_year}-{entry_time_month}":

                    # total_efficiency_wages = ((workpiece_ratio / 100) / 0.5) * config_obj.first_month_min_wages
                    # self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time

                    self.efficiency_wages = (config_obj.first_month_min_wages / 26) * self.clock_in_time



                # if self.clock_in_time < 7:  # 实出勤大于7天效率按50计算,即为（最低效率工资 / 应出勤） * 实出勤

                #     # self.efficiency_wages = (config_obj.lowest_efficiency_wages / self.should_attend) * self.clock_in_time
                #     self.efficiency_wages = (config_obj.lowest_efficiency_wages / 26) * self.clock_in_time

                else:
                    # # （（（效率 / 0.5） * 4000）/ 应出勤）* 实出勤
                    # total_efficiency_wages = ((workpiece_ratio / 100) / 0.5) * config_obj.lowest_efficiency_following_wages
                    # # self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time
                    # self.efficiency_wages = (total_efficiency_wages / 26) * self.clock_in_time

                    self.efficiency_wages = (config_obj.lowest_efficiency_following_wages / 26) * self.clock_in_time

            else:
                # （（最低效率工资 + (效率 - 最低效率（50）) * 增长数值） / 应出勤） * 实出勤
                total_efficiency_wages = config_obj.lowest_efficiency_wages + (
                            workpiece_ratio - config_obj.lowest_efficiency) * config_obj.growth_numerical
                # self.efficiency_wages = (total_efficiency_wages / self.should_attend) * self.clock_in_time
                self.efficiency_wages = (total_efficiency_wages / 26) * self.clock_in_time

    # 设置客户补贴
    def set_customer_subsidy(self):
        for record in self:
            if record.efficiency_wages:

                if record.first_level_department.name != "整件组":

                    if record.job_id.name == "流水组长":
                        if record.efficiency_wages > record.pay_now:
                            record.pay_now = record.efficiency_wages
                    else:
                        if record.name.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or record.name.is_it_a_temporary_worker == "临时工" \
                                or record.name.is_it_a_temporary_worker == "实习生(计件)":

                            if record.first_level_department.parent_id.name == "车间":

                                # 客户补贴 = （效率奖金额度 / 应出勤天数） * 实出勤天数
                                efficiency_bonus_setting_obj = self.env['efficiency_bonus_setting'].sudo().search([
                                    ("month", "=", record.date),
                                    ("workpiece_ratio_lower_limit", "<=", record.month_workpiece_ratio / 100),
                                    ("workpiece_ratio_upper_limit", ">", record.month_workpiece_ratio / 100)
                                ])
                                if efficiency_bonus_setting_obj:
                                    record.customer_subsidy = (
                                                                          efficiency_bonus_setting_obj.bonus_quota / record.should_attend) * record.clock_in_time
                                else:
                                    record.customer_subsidy = 0

                            else:
                                # 客户补贴 = 效率薪资 - 正常薪资
                                record.customer_subsidy = record.efficiency_wages - record.pay_now

                        else:

                            if self.env['post_commission_setting'].sudo().search([("job_id", "=", record.job_id.id)]):
                                pass
                            else:
                                record.performance_pay = record.efficiency_wages - record.pay_now
                                record.commission_bonus = 0

    # 计算计件工资
    def get_piece_rate(self, start_time, end_time):

        if self.is_workshop():
            ji_jian_objs = self.env["dg_piece_rate"].sudo().search([
                ("employee_id", "=", self.name.id),
                ("date", ">=", start_time),
                ("date", "<=", end_time)
            ])
        else:
            ji_jian_objs = self.env["ji.jian"].sudo().search([
                ("employee", "=", self.name.id),
                ("date1", ">=", start_time),
                ("date1", "<=", end_time)
            ])

        return sum(ji_jian_objs.mapped('cost'))

    # 查询休息天数
    def set_rest_days(self, start_time, end_time):
        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.name.time_plan.split(' ')[-1]
        # 获取员工所在部门
        department_id = self.first_level_department.id
        rest_days = 0  # 休息天数

        # 查询>= 请假开始时间 和<= 请假结束时间的日历，获取请假中的休息天数
        custom_calendar_objs = self.env["custom.calendar"].sudo().search([
            ('date', '>=', start_time),
            ('date', '<=', end_time),
        ])

        if custom_calendar_objs:
            # 休息天数
            for custom_calendar_obj in custom_calendar_objs:
                custom_calendar_line_id = self.env["custom_calendar_line"].sudo().search([
                    ("custom_calendar_id", "=", custom_calendar_obj.id),  # 日历id
                    ("department", "=", department_id)  # 部门id
                ])
                if rest_type == "单休" and custom_calendar_line_id.state == "休息":
                    rest_days = rest_days + 1
                elif rest_type == "大小休" and (
                        custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                    rest_days = rest_days + 1
                elif rest_type == "双休" and (
                        custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
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
                    if department_id == custom_calendar_line_id.department.id and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息"):
                        rest_days = rest_days + 1
            elif rest_type == "双休":
                for custom_calendar_line_id in custom_calendar_obj.custom_calendar_line_ids:
                    if department_id == custom_calendar_line_id.department.id and (
                            custom_calendar_line_id.state == "休息" or custom_calendar_line_id.state == "大小休休息" or custom_calendar_line_id.state == "仅双休休息"):
                        rest_days = rest_days + 1

        # 应出勤天数 = the_month_days - 休息的天数
        # self.should_attend = the_month_days - rest_days
        return the_month_days - rest_days

    # 无调岗计算
    def not_transfer_position(self, *args):

        start_time = args[1]
        end_time = args[2]
        calculation = args[3]

        # 判断是否是计件
        if self.name.is_it_a_temporary_worker == "正式工(计件工资)" \
                or self.name.is_it_a_temporary_worker == "临时工" \
                or self.name.is_it_a_temporary_worker == "实习生(计件)":
            if start_time and end_time:

                self.pay_now = self.get_piece_rate(start_time, end_time)

            else:

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"]
                this_month_last_day = this_month["end"]

                self.pay_now = self.get_piece_rate(this_month_first_day, this_month_last_day)

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
                before_pay = become_full_member_objs.probation_period_treatment
                # 转正之后薪资
                after_pay = become_full_member_objs.after_pay
                # 转正日期
                become_date = become_full_member_objs.turn_positive_date

                post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                    ("job_id", "=", self.job_id.id),
                    ("frequency_distribution", ">", 1)
                ])
                if not post_performance_setting_obj:
                    before_pay += become_full_member_objs.before_performance
                    after_pay += become_full_member_objs.after_performance

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"].date()  # 这个月第一天
                this_month_last_day = this_month["end"].date()  # 这个月最后一条
                entry_date = self.name.entry_time  # 入职日期
                dimission_date = self.name.is_delete_date  # 离职日期

                if calculation == "按月计算":
                    # 计算在职天数
                    before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                              this_month_last_day)
                    # 这个月转正之前薪资
                    this_month_before_pay = (before_pay / 30.5) * before_job_days

                    # 计算在职天数
                    after_job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                             this_month_last_day)
                    # 这个月转正之前薪资
                    this_month_after_pay = (after_pay / 30.5) * after_job_days

                elif calculation == "按天计算":

                    before_job_days = self.special_should_attendance(entry_date, become_date, this_month_first_day,
                                                                     this_month_last_day)

                    this_month_before_pay = (before_pay / 26) * before_job_days

                    after_job_days = self.special_should_attendance(become_date, dimission_date, this_month_first_day,
                                                                    this_month_last_day)

                    this_month_after_pay = (after_pay / 26) * after_job_days

                # 这个月薪资 = 这个月转正之前薪资 + 这个月转正之后薪资
                self.pay_now = this_month_before_pay + this_month_after_pay

            # 如果没有转正记录
            else:

                # 获取当月第一天和最后一天
                this_month = self.set_begin_and_end()
                this_month_first_day = this_month["begin"].date()  # 这个月第一天
                this_month_last_day = this_month["end"].date()  # 这个月最后一条
                entry_date = self.name.entry_time  # 入职日期
                dimission_date = self.name.is_delete_date  # 离职日期

                fixed_salary = self.name.fixed_salary

                post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                    ("job_id", "=", self.job_id.id),
                    ("frequency_distribution", ">", 1)
                ])

                if not post_performance_setting_obj:

                    if self.job_id.name == "人事招聘专员" or self.job_id.name == "流水组长":
                        pass
                    else:
                        fixed_salary += self.name.performance_money

                if calculation == "按月计算":

                    # 计算在职天数
                    job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day,
                                                       this_month_last_day)
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

                    # 查询扣款设置
                    deduct_money_setting_obj = self.env["deduct_money_setting"].sudo().search(
                        [("month", "=", self.date)])

                    # 获取当月第一天和最后一天
                    this_month = self.set_begin_and_end()

                    # 查询请假记录
                    every_detail_objs = self.env["every.detail"].sudo().search([
                        ("leave_officer", "=", self.name.id),
                        ("date", ">=", this_month["begin"]),
                        ("end_date", "<=", this_month["end"])
                    ])
                    # 事假天数
                    leave_days = sum([int(i.days / 8) for i in every_detail_objs if
                                      i.days >= 8 and i.reason_for_leave2 == "事假"]) * 8

                    tem_leave_deduction = (leave_days * fixed_salary / (
                                26 * 8)) * deduct_money_setting_obj.matter_vacation_deduct_money_ratio

                    # 病假天数
                    sick_leave_days = sum([int(i.days / 8) for i in every_detail_objs if
                                           i.days >= 8 and i.reason_for_leave2 == "病假"]) * 8

                    tem_sick_leave_days = (sick_leave_days * fixed_salary / (
                                26 * 8)) * deduct_money_setting_obj.sick_leave_deduct_money_ratio

                    # (薪酬 / 26) * 实出勤天数
                    # self.pay_now = (fixed_salary / 26) * self.clock_in_time + tem_leave_deduction + tem_sick_leave_days
                    #self.pay_now = (fixed_salary / 26) * self.clock_in_time - tem_leave_deduction - tem_sick_leave_days
                    self.pay_now = (fixed_salary / 26) * self.clock_in_time 
                    print(self.pay_now,fixed_salary,self.clock_in_time,tem_leave_deduction,tem_sick_leave_days)

    # 正常薪资刷新(开始时间，结束时间，计算方式)
    def current_salary_refresh(self, start_time, end_time, calculation):

        self.calculation = calculation

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
        print(internal_post_transfer_objs, "---------------")
        if internal_post_transfer_objs:

            if len(internal_post_transfer_objs) > 1:
                raise ValidationError(f"{self.name.name}暂不支持多次调岗的薪资计算！")
            elif len(internal_post_transfer_objs) == 1:
                # 如果同时有转正记录
                if become_full_member_objs:
                    raise ValidationError(f"{self.name.name}暂不支持同时调岗和转正的薪资计算！")
                else:
                    # 调整之前薪资
                    before_pay = internal_post_transfer_objs.before_pay
                    # 调整之后薪资
                    after_pay = internal_post_transfer_objs.the_salary_adjustment_scheme
                    # 调整日期
                    become_date = internal_post_transfer_objs.begin_start

                    before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                        ("job_id", "=", internal_post_transfer_objs.raw_job_id.id),
                        ("frequency_distribution", ">", 1)
                    ])
                    if not before_post_performance_setting_obj:
                        if internal_post_transfer_objs.raw_job_id.name in ["人事招聘专员", "流水组长"]:
                            pass
                        else:
                            before_pay += internal_post_transfer_objs.before_post_commission

                    after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([
                        ("job_id", "=", internal_post_transfer_objs.job_id.id),
                        ("frequency_distribution", ">", 1)
                    ])
                    if not after_post_performance_setting_obj:
                        if internal_post_transfer_objs.job_id.name in ["人事招聘专员", "流水组长"]:
                            pass
                        else:
                            after_pay += internal_post_transfer_objs.after_post_commission

                    # 是否调整工种
                    if internal_post_transfer_objs.is_temporary_worker:
                        # 判断之前的工种
                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or self.name.is_it_a_temporary_worker == "实习生(计件)":
                            if start_time and end_time:

                                this_month_before_pay = self.get_piece_rate(start_time, become_date)
                            else:
                                # 获取当月第一天和最后一天
                                this_month = self.set_begin_and_end()
                                this_month_first_day = this_month["begin"]
                                this_month_last_day = this_month["end"]

                                this_month_before_pay = self.get_piece_rate(this_month_first_day, become_date)
                        else:

                            # 获取当月第一天和最后一天
                            this_month = self.set_begin_and_end()
                            this_month_first_day = this_month["begin"].date()  # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time  # 入职日期
                            dimission_date = self.name.is_delete_date  # 离职日期

                            if calculation == "按月计算":
                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                                   this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_before_pay = (before_pay / 30.5) * job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                job_days = self.special_should_attendance(entry_date, become_date, this_month_first_day,
                                                                          this_month_last_day)

                                this_month_before_pay = (before_pay / 26) * job_days

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                            if start_time and end_time:

                                this_month_after_pay = self.get_piece_rate(become_date, end_time)
                            else:
                                # 获取当月第一天和最后一天
                                this_month = self.set_begin_and_end()
                                this_month_first_day = this_month["begin"]
                                this_month_last_day = this_month["end"]

                                this_month_after_pay = self.get_piece_rate(become_date, this_month_last_day)

                        else:

                            # 获取当月第一天和最后一天
                            this_month = self.set_begin_and_end()
                            this_month_first_day = this_month["begin"].date()  # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time  # 入职日期
                            dimission_date = self.name.is_delete_date  # 离职日期

                            if calculation == "按月计算":
                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day,
                                                                   this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_after_pay = (after_pay / 30.5) * job_days

                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                job_days = self.special_should_attendance(entry_date, dimission_date,
                                                                          this_month_first_day, this_month_last_day)

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
                            this_month_first_day = this_month["begin"].date()  # 这个月第一天
                            this_month_last_day = this_month["end"].date()  # 这个月最后一条
                            entry_date = self.name.entry_time  # 入职日期
                            dimission_date = self.name.is_delete_date  # 离职日期

                            if calculation == "按月计算":

                                # 计算在职天数
                                before_job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                                          this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_before_pay = (before_pay / 30.5) * before_job_days
                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                before_job_days = self.special_should_attendance(entry_date, become_date,
                                                                                 this_month_first_day,
                                                                                 this_month_last_day)

                                this_month_before_pay = (before_pay / 26) * before_job_days

                            if calculation == "按月计算":

                                # 计算在职天数
                                after_job_days = self.be_on_the_job_days(become_date, dimission_date,
                                                                         this_month_first_day, this_month_last_day)
                                # 这个月转正之前薪资
                                this_month_after_pay = (after_pay / 30.5) * after_job_days
                            elif calculation == "按天计算":
                                # 计算应出勤天数
                                after_job_days = self.special_should_attendance(become_date, dimission_date,
                                                                                this_month_first_day,
                                                                                this_month_last_day)

                                this_month_after_pay = (after_pay / 26) * after_job_days

                            if this_month_before_pay and this_month_after_pay:
                                # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                self.pay_now = this_month_before_pay + this_month_after_pay

                            else:

                                # 计算在职天数
                                job_days = self.be_on_the_job_days(entry_date, dimission_date, this_month_first_day,
                                                                   this_month_last_day)

                                # 如果在职天数等于当月全部天数
                                if job_days == this_month_last_day.day:

                                    if self.job_id.name == "人事招聘专员" or self.job_id.name == "流水组长":
                                        self.pay_now = self.name.fixed_salary
                                    else:
                                        self.pay_now = self.name.fixed_salary + self.name.performance_money


                                else:
                                    # 这个月薪资 = 这个月调整之前薪资 + 这个月调整之后薪资
                                    print(this_month_before_pay, this_month_after_pay)
                                    self.pay_now = this_month_before_pay + this_month_after_pay



            else:
                raise ValidationError(f"{self.name.name}调岗薪资计算失败！")


        # 如果没有转岗记录
        else:

            self.not_transfer_position(self, start_time, end_time, calculation)

        # # 有转岗组长薪资计算
        # if internal_post_transfer_objs:

        #     if internal_post_transfer_objs.raw_job_id.name == "流水组长" or internal_post_transfer_objs.job_id.name == "流水组长":

        #         self.pay_now = self.relieve_guard_group_leader_pay(internal_post_transfer_objs)
        # # 无转岗薪资计算
        # else:
        #     if self.job_id.name == "流水组长":
        #         if self.calculation == "按天计算":
        #             self.pay_now = ((self.set_group_leader_efficiency_wages_algorithm_two()) / 26) * self.clock_in_time
        #         else:
        #             self.pay_now = ((self.set_group_leader_efficiency_wages_algorithm_two()) / self.should_attend) * self.clock_in_time

    # 获取两个日期间的所有日期
    def getEveryDay(self, begin_date, end_date):
        date_list = []
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list

    # 特殊情况实出勤天数计算
    def special_actual_attendance_calculation(self, date_list) -> int:
        clock_in_time = 0
        for day in date_list:
            # 获取员工的休息类型(单休还是双休或者大小休息)
            rest_type = self.name.time_plan.split(' ')[-1]

            # 默认为不休息
            is_rest = False
            # 先查询日历，这天是否是休息，如果查询到是休息，则将is_rest = True
            custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", day)])
            if custom_calendar_obj:
                custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search(
                    [("custom_calendar_id", "=", custom_calendar_obj.id),
                     ("department", "=", self.first_level_department.id)])

                if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                    is_rest = True
                elif rest_type == "大小休" and (
                        custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息"):
                    is_rest = True
                elif rest_type == "双休" and (
                        custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state == "大小休休息" or custom_calendar_line_obj.state == "仅双休休息"):
                    is_rest = True
            # 如果休息则跳过，如果不休息则查询考勤机 计算实出勤天数
            if is_rest:
                pass
            else:

                clock_in_time = clock_in_time + self.punch_card_and_fill_card(day)

        return clock_in_time

    # 有转岗组长薪资计算
    def relieve_guard_group_leader_pay(self, internal_post_transfer_objs):

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

                        date_list = self.getEveryDay(this_month_first_day, become_date)[0:-1]
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                            adjust_after_pay = self.get_piece_rate(become_date, this_month_last_day)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days



                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                            adjust_before_pay = self.get_piece_rate(this_month_first_day, become_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        date_list = self.getEveryDay(become_date, this_month_last_day)
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time



                # 当月之前入职的，离职日期小于等于当月最后一天----------------------2
                else:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        date_list = self.getEveryDay(this_month_first_day, become_date)[0:-1]
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工":

                            adjust_after_pay = self.get_piece_rate(become_date, dimission_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days



                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                            adjust_before_pay = self.get_piece_rate(this_month_first_day, become_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        date_list = self.getEveryDay(become_date, dimission_date)
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time


            # 当月之前入职的，未离职----------------------3
            else:
                # 之前是组长
                if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                    date_list = self.getEveryDay(this_month_first_day, become_date)[0:-1]
                    clock_in_time = self.special_actual_attendance_calculation(date_list)
                    # 计算组长薪资
                    adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                        internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time
                    # 判断之后的工种
                    if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工":

                        adjust_after_pay = self.get_piece_rate(become_date, this_month_last_day)
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                           this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_after_pay = (after_pay / 30.5) * job_days


                # 之后是组长
                elif internal_post_transfer_objs.job_id.name == "流水组长":

                    if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                        adjust_before_pay = self.get_piece_rate(this_month_first_day, become_date)
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                           this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_before_pay = (before_pay / 30.5) * job_days

                    date_list = self.getEveryDay(become_date, this_month_last_day)
                    clock_in_time = self.special_actual_attendance_calculation(date_list)
                    # 计算组长薪资
                    adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                        internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time

        else:

            if dimission_date:
                # 当月入职的，离职时间大于当月最后一天----------------------4
                if dimission_date > this_month_last_day:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        date_list = self.getEveryDay(entry_date, become_date)[0:-1]
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                            adjust_after_pay = self.get_piece_rate(become_date, this_month_last_day)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days


                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                            adjust_before_pay = self.get_piece_rate(entry_date, become_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        date_list = self.getEveryDay(become_date, this_month_last_day)
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time

                # 当月入职的，离职时间小于等于当月最后一天----------------------5
                else:
                    # 之前是组长
                    if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                        date_list = self.getEveryDay(entry_date, become_date)[0:-1]
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time

                        # 判断之后的工种
                        if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                            adjust_after_pay = self.get_piece_rate(become_date, dimission_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_after_pay = (after_pay / 30.5) * job_days



                    # 之后是组长
                    elif internal_post_transfer_objs.job_id.name == "流水组长":

                        if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                                or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                            adjust_before_pay = self.get_piece_rate(entry_date, become_date)
                        else:
                            # 计算在职天数
                            job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                               this_month_last_day)
                            # 这个月转正之前薪资
                            adjust_before_pay = (before_pay / 30.5) * job_days

                        date_list = self.getEveryDay(become_date, dimission_date)
                        clock_in_time = self.special_actual_attendance_calculation(date_list)
                        # 计算组长薪资
                        adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                            internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time

            # 当月入职的，未离职----------------------6
            else:
                # 之前是组长
                if internal_post_transfer_objs.raw_job_id.name == "流水组长":

                    date_list = self.getEveryDay(entry_date, become_date)[0:-1]
                    clock_in_time = self.special_actual_attendance_calculation(date_list)
                    # 计算组长薪资
                    adjust_before_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                        internal_post_transfer_objs.department_id.id)) / self.should_attend) * clock_in_time

                    # 判断之后的工种
                    if internal_post_transfer_objs.after_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.after_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.after_temporary_worker == "实习生(计件)":

                        adjust_after_pay = self.get_piece_rate(become_date, this_month_last_day)
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(become_date, dimission_date, this_month_first_day,
                                                           this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_after_pay = (after_pay / 30.5) * job_days


                # 之后是组长
                elif internal_post_transfer_objs.job_id.name == "流水组长":

                    if internal_post_transfer_objs.is_it_a_temporary_worker == "正式工(计件工资)" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "临时工" \
                            or internal_post_transfer_objs.is_it_a_temporary_worker == "实习生(计件)":

                        adjust_before_pay = self.get_piece_rate(entry_date, become_date)
                    else:
                        # 计算在职天数
                        job_days = self.be_on_the_job_days(entry_date, become_date, this_month_first_day,
                                                           this_month_last_day)
                        # 这个月转正之前薪资
                        adjust_before_pay = (before_pay / 30.5) * job_days

                    date_list = self.getEveryDay(become_date, this_month_last_day)
                    clock_in_time = self.special_actual_attendance_calculation(date_list)
                    # 计算组长薪资
                    adjust_after_pay = ((self.set_group_leader_efficiency_wages_algorithm_two(
                        internal_post_transfer_objs.proposed_department.id)) / self.should_attend) * clock_in_time

        return adjust_before_pay + adjust_after_pay

    # 计算绩效工资
    def set_performance_pay(self):

        for record in self:

            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            first_day = this_month["begin"]
            last_day = this_month["end"]

            if record.job_id.name == "流水组长":
                target_output_value_obj = self.env['target_output_value'].sudo().search([
                    ("year_month", "=", record.date),
                    ("employee_id", "=", record.name.id),
                ], limit=1)
                if target_output_value_obj:
                    record.performance_pay = record.name.performance_money * (target_output_value_obj.progress / 100)
                else:
                    raise ValidationError(f"没有查询到流水组长{self.name.name}的目标产值记录！")

            if record.name.department_id.name == "人事行政部":
                personnel_award_count = record.counting_number_recruits(first_day, last_day)
                record.performance_pay = personnel_award_count * 100

    # 计算中查绩效 中查漏查表(日：按中查)
    def calculate_middle_check_performance(self, first_day, last_day):

        middle_check_day_leak_objs = self.env["middle_check_day_leak"].sudo().search([
            ("middle_check_principal", "like", self.name.name),  # 匹配员工姓名
            ("date", ">=", first_day),
            ("date", "<=", last_day)
        ])

        tem_middle_check_performance_pay = 0

        for middle_check_day_leak_obj in middle_check_day_leak_objs:
            tem_middle_check_performance_pay = tem_middle_check_performance_pay + middle_check_day_leak_obj.assess_index

        return tem_middle_check_performance_pay

    # 计算总检绩效 总检漏查(日)
    def calculate_always_check_performance(self, first_day, last_day):

        always_check_day_leak_objs = self.env["always_check_omission"].sudo().search([
            ("always_check_principal", "like", self.name.name),  # 匹配员工姓名
            ("dDate", ">=", first_day),
            ("dDate", "<=", last_day)
        ])

        tem_always_check_performance_pay = 0

        for always_check_day_leak_obj in always_check_day_leak_objs:
            tem_always_check_performance_pay = tem_always_check_performance_pay + always_check_day_leak_obj.assess_index

        return tem_always_check_performance_pay

    # 计算招聘人数
    def counting_number_recruits(self, first_day, last_day):
        personnel_award_count = self.env["personnel_award"].sudo().search_count([
            ("introducer", "=", self.name.id),  # 员工id
            ("working_time", ">=", 30),  # 在职时长大于30天
            ("satisfy_date", ">=", first_day),  # 满足30天日期大于等于当月第一天
            ("satisfy_date", "<=", last_day),  # 满足30天日期小于等于当月第一天
        ])
        return personnel_award_count
