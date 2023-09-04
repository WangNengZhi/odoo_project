from odoo.exceptions import ValidationError
from odoo import models, fields, api
import datetime
import calendar

class RefillCardReturn(models.Model):
    _name = 'refill_card_return'
    _description = '饭卡归还'
    _order = "departure_date desc"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    departure_date = fields.Date(string='离职日期')
    month = fields.Char(string="退卡月份")
    recharge_amount = fields.Float(string="当月充值金额", compute="set_employee_message", store=True)
    working_days = fields.Float(string="离职月在职天数", compute="set_employee_message", store=True)
    should_allowance = fields.Float(string="应补金额", compute="set_employee_message", store=True)
    actual_cost = fields.Float(string="实际花费金额")
    refund_amount = fields.Float(string="退款金额", compute="set_refund_amount", store=True)

    clock_in_time = fields.Float(string="实际出勤天数", compute="set_employee_message", store=True)
    attendance_day = fields.Integer(string="应出勤天数", compute="set_employee_message", store=True)


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

        scope_1 = 0
        scope_2 = 0

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


        return days


    # 实出勤天数计算:打卡和补卡查询
    def punch_card_and_fill_card(self, day):
        tem_clock_in_time = 0

        # 查询打卡机记录,如果有则+1,如果没有则查询补卡记录
        punch_in_record_obj = self.env["punch.in.record"].sudo().search([("date", "=", day), ("employee", "=", self.employee_id.id)])

        # 如果有打卡记录
        if punch_in_record_obj:

            if punch_in_record_obj.check_sign[0: 5] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.employee_id.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "上班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", self.employee_id.id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1

            elif punch_in_record_obj.check_sign[6: 11] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", self.employee_id.id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "下班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", self.employee_id.id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1
            else:
                tem_clock_in_time = 1

        # # 如果没有打卡记录
        else:
            up_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.employee_id.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "上班卡")
            ])
            below_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", self.employee_id.id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "下班卡")
            ])
            if up_repair_clock_in_line_obj and below_repair_clock_in_line_obj:
                tem_clock_in_time = 1
            else:
                exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                    ("start_date", "<=", day),
                    ("end_date", ">=", day),
                    ("employee_id", "=", self.employee_id.id)
                ])
                if exchange_rest_use_line_obj:
                    tem_clock_in_time = 1

        return tem_clock_in_time


    def is_workshop(self):
        for record in self:
            # 获取部门id
            department_obj = record.employee_id.department_id

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


    # 计算实际出勤天数
    def set_clock_in_time(self):

        for record in self:

            if record.employee_id.is_it_a_temporary_worker == '正式工(计件工资)' or record.employee_id.is_it_a_temporary_worker == '临时工':

                this_month_year = int(record.month.split('-')[0])
                this_month_month = int(record.month.split('-')[1])
                this_month = record.set_begin_and_end(this_month_year, this_month_month)
                # return {"first_day": first_day, "last_day": last_day}
                name_list = []
                # 查询统计中的员工信息表
                if self.is_workshop():
                    group_attendance_objs = self.env["auto_employee_information"].sudo().search([
                        ("employee_id", "=", record.employee_id.id),
                        ("date", ">=", this_month["first_day"]),
                        ("date", "<=", this_month["last_day"])
                    ])
                else:
 
                    group_attendance_objs = self.env["memp.memp"].sudo().search([
                        ("employee", "=", record.employee_id.id),
                        ("date", ">=", this_month["first_day"]),
                        ("date", "<=", this_month["last_day"])
                    ])

                for memp_memp_obj in group_attendance_objs:
                    name_list.append(memp_memp_obj.date)
                # 按日期去重后存放到列表中
                name_list = list(set(name_list))

                temp_days = 0
                for i in name_list:
                    custom_calendar_obj = self.env['custom.calendar'].sudo().search([("date", "=", i)])
                    for j in custom_calendar_obj.custom_calendar_line_ids:
                        if j.department.id == record.employee_id.department_id.id:
                            if j.state == "休息":
                                temp_days += 1

                record.clock_in_time = len(name_list) - temp_days
            
            else:

                # 获取员工的休息类型(单休还是双休或者大小休息)
                rest_type = record.employee_id.time_plan.split(' ')[-1]
                # 出勤天数
                clock_in_time = 0

                # 循环当月全部天
                for day in record.get_this_month_days():

                    # 默认为不休息
                    is_rest = False
                    # 先查询日历，这天是否是休息，如果查询到是休息，则将is_rest = True
                    custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", day)])
                    if custom_calendar_obj:
                        custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([("custom_calendar_id", "=", custom_calendar_obj.id), ("department", "=", record.employee_id.department_id.id)])

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



    # 设置离职日期
    # @api.depends('employee_id')
    @api.onchange('employee_id')
    def set_departure_date(self):
        for record in self:
            if record.employee_id:

                if record.employee_id.is_delete_date:
                    record.departure_date = record.employee_id.is_delete_date
                
                else:

                    if record.month:
                        year, month = map(int, record.month.split("-"))
                        record.departure_date = record.set_begin_and_end(year, month)["last_day"]

                    else:

                        raise ValidationError(f"请先设置退卡月份！")


    @api.constrains('employee_id', 'departure_date')
    def _check_unique(self):

        for record in self:

            demo = self.env[record._name].sudo().search([
                ("employee_id", "=", record.employee_id.id),
            ])
            if len(demo) > 1:
                raise ValidationError(f"同一个员工只能有一条饭卡归还记录！")

                


    # 获取当前月份
    def get_nowaday_month(self):
        
        # 当前年
        year = datetime.datetime.now().year
        # 当前月
        month = datetime.datetime.now().month

        return {"year": year, "month": month}


    # 获取当月第一天和最后一天
    def set_begin_and_end(self, this_month_year, this_month_month):
        
        this_month_year = str(this_month_year)
        this_month_month = str(this_month_month)

        day = 1
        date_pinjie = this_month_year + '-' + this_month_month + '-' + str(day)
        #    这就是年月的算法，返回本月天数
        month_math = calendar.monthrange(int(this_month_year), int(this_month_month))[1]

        date_end_of_the_month5 = this_month_year + '-' + this_month_month + '-' + str(month_math)
        last_day = datetime.datetime.strptime(date_end_of_the_month5, '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

        first_day = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')      # 当月第一天

        return {"first_day": first_day, "last_day": last_day}


    # 获取当月饭补金额
    def get_rice_tonic(self, this_month_year, this_month_month):


        tem_dict = self.set_begin_and_end(this_month_year, this_month_month)
        first_day = tem_dict["first_day"]
        last_day = tem_dict["last_day"]

        meal_subsidy_top_up_obj = self.env["meal_subsidy_top_up"].sudo().search([
            ("date", ">=", first_day),
            ("date", "<=", last_day),
            ("name", "=", self.employee_id.id)
        ])

        return meal_subsidy_top_up_obj


    # 设置员工信息
    @api.depends('employee_id', 'month', 'departure_date')
    def set_employee_message(self):
        for record in self:

            if record.employee_id and record.month:

                if record.departure_date:
                    # 计算实际出勤天数
                    record.set_clock_in_time()
                    # 入职日期年份
                    entry_year = record.employee_id.entry_time.year
                    # 入职日期月份
                    entry_month = record.employee_id.entry_time.month

                    this_month_year = int(record.month.split('-')[0])
                    this_month_month = int(record.month.split('-')[1])

                    # 获取当月饭补
                    rice_tonic_obj = record.get_rice_tonic(this_month_year, this_month_month)
                    if not rice_tonic_obj:
                        raise ValidationError(f"未查询到该员工的饭卡充值记录信息。")

                    # 当月充值金额 = 当月饭补
                    record.recharge_amount = rice_tonic_obj.amount

                    # 如果入职年份月份 = 当前年份月份
                    if entry_year == this_month_year and entry_month == this_month_month:
                        # 离职月在职天数 = 离职日期 - 入职日期
                        record.working_days = (record.departure_date - record.employee_id.entry_time).days

                    else:
                        # 获取当月第一天
                        this_month_first_day = datetime.date(this_month_year, this_month_month, 1)
                        # 离职月在职天数 = 离职日期 - 当月第一天
                        record.working_days = (record.departure_date - this_month_first_day).days
                    
                    if record.clock_in_time > rice_tonic_obj.attendance_day:
                        record.clock_in_time = rice_tonic_obj.attendance_day
                        
                    record.attendance_day = rice_tonic_obj.attendance_day
                    # 应补餐费 = 离职月在职天数 * (当月饭补 / 出勤天数)
                    record.should_allowance = record.clock_in_time * (rice_tonic_obj.amount / record.attendance_day)
                    # record.should_allowance = record.working_days * 10

                else:

                    raise ValidationError(f"该员工未设置离职日期！")

    # 设置退款金额
    @api.depends('should_allowance', 'actual_cost')
    def set_refund_amount(self):
        for record in self:


            if record.employee_id:

                if record.departure_date:
                    # # 入职日期年份
                    # entry_year = record.employee_id.entry_time.year
                    # # 入职日期月份
                    # entry_month = record.employee_id.entry_time.month
                    # # 获取当前年和月
                    # this_month = record.get_nowaday_month()
                    # this_month_year = this_month["year"]
                    # this_month_month = this_month["month"]
                    # # 获取当月饭补
                    # rice_tonic = record.get_rice_tonic(this_month_year, this_month_month)
                    # # 如果入职年份月份 = 当前年份月份
                    # if entry_year == this_month_year and entry_month == this_month_month:

                    #     # 退款金额 = 当月充值金额 - 实际花费金额
                    #     record.refund_amount = record.recharge_amount - record.actual_cost

                    # else:
                    #     # 退款金额 = 当月饭补 - 实际花费金额
                    #     record.refund_amount = rice_tonic - record.actual_cost
                    # 退款金额 = 实际花费金额 - 应补金额
                    record.refund_amount = record.actual_cost - record.should_allowance
                    # 退款金额 = 应补金额 - 实际花费金额
                    # record.refund_amount = record.should_allowance - record.actual_cost

                else:

                    raise ValidationError(f"该员工未设置离职日期！")




            




