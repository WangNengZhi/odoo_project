from odoo import api, fields, models
import datetime
import calendar

class FsnKpiLine(models.Model):
    _inherit = 'fsn_kpi_line'

    ''' 自动考核常用方法'''


    # 获取当月第一天和最后一天
    def set_begin_and_end(self, year, month):

        this_month_start = datetime.datetime(year, month, 1)
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]) + datetime.timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

        return this_month_start, this_month_end


    # 获取本月全部的天
    def get_this_month_days(self, year, month, entry_date, dimission_date):

        num_days = calendar.monthrange(year,month)[1] ## 最后一天
        start_date = datetime.date(year,month,1)
        end_date = datetime.date(year,month,num_days)

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

        return days


    # 实出勤天数计算:打卡和补卡查询,调休记录
    def punch_card_and_fill_card(self, day):
        tem_clock_in_time = 0

        employee_id = self.fsn_kpi_id.employee_id.id

        # 查询打卡机记录,如果有则+1,如果没有则查询补卡记录
        punch_in_record_obj = self.env["punch.in.record"].sudo().search([("date", "=", day), ("employee", "=", employee_id)])

        # 如果有打卡记录
        if punch_in_record_obj:

            if punch_in_record_obj.check_sign[0: 5] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", employee_id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "上班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", employee_id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1

            elif punch_in_record_obj.check_sign[6: 11] == "--:--":
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                    ("employee_id", "=", employee_id),
                    ("line_date", "=", day),
                    ("repair_clock_type", "=", "下班卡")
                ])
                if repair_clock_in_line_obj:
                    tem_clock_in_time = 1
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", day),
                        ("end_date", ">=", day),
                        ("employee_id", "=", employee_id)
                    ])
                    if exchange_rest_use_line_obj:
                        tem_clock_in_time = 1
            else:
                tem_clock_in_time = 1

        # # 如果没有打卡记录
        else:
            up_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", employee_id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "上班卡")
            ])
            below_repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", employee_id),
                ("line_date", "=", day),
                ("repair_clock_type", "=", "下班卡")
            ])
            if up_repair_clock_in_line_obj and below_repair_clock_in_line_obj:
                tem_clock_in_time = 1
            else:
                exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                    ("start_date", "<=", day),
                    ("end_date", ">=", day),
                    ("employee_id", "=", employee_id)
                ])
                if exchange_rest_use_line_obj:
                    tem_clock_in_time = 1

        return tem_clock_in_time


    # 计算在职天数
    def get_actual_attendance_days(self, days_list):

        # 获取员工的休息类型(单休还是双休或者大小休息)
        rest_type = self.fsn_kpi_id.employee_id.time_plan.split(' ')[-1]
        date_list = []
        # 循环当月全部天
        for day in days_list:

            # 默认为不休息
            is_rest = False
            # 先查询日历，这天是否是休息，如果查询到是休息，则将is_rest = True
            custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", day)])
            if custom_calendar_obj:
                custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([("custom_calendar_id", "=", custom_calendar_obj.id), ("department", "=", self.fsn_kpi_id.employee_id.department_id.id)])

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
                if self.punch_card_and_fill_card(day):
                    date_list.append(day)
        
        return date_list
