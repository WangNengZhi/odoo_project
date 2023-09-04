from odoo import models, fields, api
import datetime
import calendar
from odoo.exceptions import ValidationError


class LockGardCheckAttendance(models.TransientModel):
    _name = 'lock_grade_check_attendance'
    _descriptions = '迟到早退向导'

    year_month = fields.Char(string="月份", required=True)

    def view_late_and_early_leave(self):
        """检查迟到早退"""
        last_list = self.env['reward_punish_record'].sudo().detection_of_late_arrival_and_early_departure(self.year_month)

        text = ""

        for i in last_list:
            text += f"员工：{i['name']}，日期：{i['date']}，迟到总时间：{i['minutes_late']}分钟， 早退总时间：{i['total_time_early']}分钟\n"

        raise ValidationError(f"{text}以上员工存在迟到早退异常！")

    def attendance_ticket_generation(self):
        """迟到早退生成罚单"""
        self.env['reward_punish_record'].sudo().generate_ticket(self.year_month)


class LackCardGenerateTicketWizard(models.TransientModel):
    _name = 'lack_card_generate_ticket_wizard'
    _description = '缺打卡向导'

    year_month = fields.Char(string="月份", required=True)




    def lack_card_generate_ticket(self):
        ''' 生成'''

        self.env['reward_punish_record'].sudo().monthly_number_one_auto_rpr(self.year_month, True)

    def view_lack_card_record(self):
        ''' 查看'''

        lack_card_list = self.env['reward_punish_record'].sudo().monthly_number_one_auto_rpr(self.year_month, False)
        
        text = ""
        for i in lack_card_list:
            text += f"员工：{i['name']}，日期: {i['day']}\n"

        raise ValidationError(f"{text}以上员工打卡记录存在异常！")

class RewardPunishRecord(models.Model):
    _inherit = "reward_punish_record"


    def get_this_month_days(self, year, month, entry_date, dimission_date):
        ''' 获取本月全部的天'''

        num_days = calendar.monthrange(year, month)[1]## 最后一天
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_days)


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



    def query_punch_in_record(self, on_work_day, emp_obj):
        ''' 查询打卡记录'''
        tem_absenteeism_days = 0

        # 查询打卡记录
        punch_in_record_obj = self.env["punch.in.record"].sudo().search([("employee", "=", emp_obj.id), ("date", "=", on_work_day)])

        # 如果打卡记录
        if punch_in_record_obj:

            if "--:--" in punch_in_record_obj.check_sign:
                # 查询请假表
                every_detail_objs  = self.env["every.detail"].sudo().search([
                    ("leave_officer", "=", emp_obj.id),
                    ("date", "<=", on_work_day),
                    ("end_date", ">=", on_work_day)
                ])
                # 如果查到了
                if every_detail_objs:
                    pass
                else:
                    exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                        ("start_date", "<=", on_work_day),
                        ("end_date", ">=", on_work_day),
                        ("employee_id", "=", emp_obj.id)
                    ])
                    if exchange_rest_use_line_obj:
                        pass
                    else:
                        tem_absenteeism_days = 1

        else:

            # 查询请假表
            every_detail_objs  = self.env["every.detail"].sudo().search([
                ("leave_officer", "=", emp_obj.id),
                ("date", "<=", on_work_day),
                ("end_date", ">=", on_work_day)
            ])
            # 如果查到了
            if every_detail_objs:
                pass

            else:
                exchange_rest_use_line_obj = self.env["exchange_rest_use_line"].sudo().search([
                    ("start_date", "<=", on_work_day),
                    ("end_date", ">=", on_work_day),
                    ("employee_id", "=", emp_obj.id)
                ])
                if exchange_rest_use_line_obj:
                    pass
                else:
                    tem_absenteeism_days = 2

        return tem_absenteeism_days


    def monthly_number_one_auto_rpr(self, generate_month, is_create):
        ''' 缺卡生成'''
        last_year, last_month = map(int, generate_month.split("-"))

        last_month_start = datetime.date(last_year, last_month, 1)
        last_month_start, last_month_end = self.set_begin_and_end(last_month_start)

        work_type_list = ["正式工(A级管理)", "正式工(B级管理)", "正式工(计时工资)", "实习生(非计件)"]

        emp_objs = self.env['hr.employee'].sudo().search([
            ("is_it_a_temporary_worker", "in", work_type_list),
            "|", ("is_delete", "=", False), ("is_delete_date", ">=", last_month_end), ("entry_time", "<=", last_month_start)
        ])

        lack_card_list = []

        for emp_obj in emp_objs:

            lack_punch_frequency = 0

            rest_type = emp_obj.time_plan.split(' ')[-1]

            department_id = emp_obj.department_id.id

            on_work_days_list = self.get_this_month_days(last_year, last_month, emp_obj.entry_time, emp_obj.is_delete_date)
                
            for on_work_day in on_work_days_list:

                custom_calendar_obj = self.env["custom.calendar"].sudo().search([("date", "=", on_work_day)])
                
                if custom_calendar_obj:

                    custom_calendar_line_obj = custom_calendar_obj.custom_calendar_line_ids.filtered(lambda x: x.department.id == department_id)


                    if custom_calendar_line_obj:

                        if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                            pass
                        elif rest_type == "大小休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息"):
                            pass
                        elif rest_type == "双休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息" or custom_calendar_line_obj.state== "仅双休休息"):
                            pass
                        else:
                            if is_create:
                                lack_punch_frequency += self.query_punch_in_record(on_work_day, emp_obj)
                            else:
                                if self.query_punch_in_record(on_work_day, emp_obj) != 0:
                                    lack_card_list.append({"name": emp_obj.name, "day": on_work_day})
                    
                    else:
                        if is_create:
                            lack_punch_frequency += self.query_punch_in_record(on_work_day, emp_obj)
                        else:
                            if self.query_punch_in_record(on_work_day, emp_obj) != 0:
                                lack_card_list.append({"name": emp_obj.name, "day": on_work_day})
                
                else:
                    if is_create:
                        lack_punch_frequency += self.query_punch_in_record(on_work_day, emp_obj)
                    else:
                        if self.query_punch_in_record(on_work_day, emp_obj) != 0:
                            lack_card_list.append({"name": emp_obj.name, "day": on_work_day})

                
            if lack_punch_frequency >= 3:
                
                
                reward_punish_record_obj = self.env['reward_punish_record'].sudo().search([
                    ("emp_id", "=", emp_obj.id),
                    ("declare_time", "=", last_month_end),
                    ("event_type", "=", "auto_lack_card")
                ])
                if not reward_punish_record_obj:
                    self.env['reward_punish_record'].sudo().create({
                        "is_automatic": True,
                        "declare_time": last_month_end,
                        "emp_id": emp_obj.id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": int(lack_punch_frequency / 3) * 50,
                        "record_matter": f"{last_year}年{last_month}月，缺卡{lack_punch_frequency}次。"
                    })
        
        if lack_card_list:
            return lack_card_list

    def detection_of_late_arrival_and_early_departure(self, generate_month):
        """查询迟到早退"""
        last_year, last_month = map(int, generate_month.split("-"))
        last_month_start = datetime.date(last_year, last_month, 1)
        last_month_start, last_month_end = self.set_begin_and_end(last_month_start)
        # 去除时间部分并格式化日期
        last_month_start_date = last_month_start.strftime('%Y-%m-%d')
        last_month_end_date = last_month_end.strftime('%Y-%m-%d')

        records = self.env['come.to.work'].sudo().search([('minutes_late', '>', 0), ('total_time_early', '>', 0),
                                                          ('date', '>=', last_month_start_date),
                                                          ('date', '<=', last_month_end_date)])
        result_list = []

        for record in records:
            date = record.date
            name = record.name.name
            minutes_late = record.minutes_late
            total_time_early = record.total_time_early

            result_dict = {
                'id': record.name.id,
                'date': date,
                'name': name,
                'minutes_late': minutes_late,
                'total_time_early': total_time_early
            }
            result_list.append(result_dict)
        return result_list

    def obtain_late_and_early_leave(self, generate_month):
        """查询迟到早退"""
        last_year, last_month = map(int, generate_month.split("-"))
        last_month_start = datetime.date(last_year, last_month, 1)

        last_month_start, last_month_end = self.set_begin_and_end(last_month_start)
        # 去除时间部分并格式化日期
        last_month_start_date = last_month_start.strftime('%Y-%m-%d')
        last_month_end_date = last_month_end.strftime('%Y-%m-%d')

        records = self.env['come.to.work'].sudo().search([('minutes_late', '>', 0), ('total_time_early', '>', 0),
                                                          ('date', '>=', last_month_start_date),
                                                          ('date', '<=', last_month_end_date)])
        result_list = []
        late_count_dict = {}
        early_count_dict = {}

        for record in records:
            employee_id = record.name.id
            date = record.date
            name = record.name.name
            minutes_late = record.minutes_late
            total_time_early = record.total_time_early

            if employee_id in late_count_dict:
                late_count_dict[employee_id] += 1
            else:
                late_count_dict[employee_id] = 1

            if employee_id in early_count_dict:
                early_count_dict[employee_id] += 1
            else:
                early_count_dict[employee_id] = 1

            result_dict = {
                'id': employee_id,
                'date': date,
                'name': name,
                'minutes_late': minutes_late,
                'total_time_early': total_time_early
            }
            result_list.append(result_dict)

        result_list_filtered = [record for record in result_list if
                                late_count_dict.get(record['id'], 0) >= 3 or early_count_dict.get(record['id'], 0) >= 3]

        return result_list_filtered

    def generate_ticket(self, generate_month):
        """生成罚单"""
        last_year, last_month = map(int, generate_month.split("-"))
        last_month_start = datetime.date(last_year, last_month, 1)
        last_month_start, last_month_end = self.set_begin_and_end(last_month_start)
        # 去除时间部分并格式化日期
        last_month_end_date = last_month_end.strftime('%Y-%m-%d')

        result_list = self.obtain_late_and_early_leave(generate_month)

        processed_employees = {}  # 跟踪已处理的员工

        for result in result_list:
            emp_id = result['id']
            if emp_id not in processed_employees:  # 检查员工是否已处理过
                emp_objs = self.env['hr.employee'].sudo().search([('id', '=', result['id'])])

                data = {
                    "is_automatic": True,
                    'declare_time': last_month_end_date,
                    "emp_id": emp_objs.id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": int(len(result) / 3) * 50,
                    "record_matter": f"{last_year}年{last_month}月，迟到或者早退{len(result)}次。"
                }

                self.env['reward_punish_record'].sudo().create(data)
                processed_employees[emp_id] = True  # 将员工标记为已处理

        processed_employees.clear() # 清空已处理员工的记录，以便下个月重新跟踪
