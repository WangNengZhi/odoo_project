
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import re



class AttendanceRecord(models.Model):
    _name = 'attendance_record'
    _description = '考勤打卡'
    _order = 'date desc'

    date = fields.Date(string='日期')
    employee = fields.Many2one('hr.employee', string='员工')
    check_sign = fields.Char(string='出勤时间')
    show_time = fields.Char(string="出勤时间", compute="standardization_check_sign", store=True)



    # 设置上班打卡时间范围
    def set_up_time_scope(self, up_time):

        up_time = datetime.datetime.strptime(up_time, "%H:%M")
        # 上班开始时间
        up_start_time = up_time - datetime.timedelta(minutes=30)
        # 上班结束时间
        up_end_time = up_time + datetime.timedelta(minutes=30)

        return {
            "up_start_time": up_start_time,
            "up_end_time": up_end_time
        }


    # 设置下班打卡时间范围
    def set_down_time_scope(self, down_time):

        down_time = datetime.datetime.strptime(down_time, "%H:%M")
        # 下班开始时间
        down_start_time = down_time - datetime.timedelta(minutes=30)
        # 下班结束时间
        down_end_time = down_time + datetime.timedelta(minutes=30)

        return {
            "down_start_time": down_start_time,
            "down_end_time": down_end_time
        }


    @api.depends('date', 'employee', 'check_sign')
    def standardization_check_sign(self):
        for record in self:
            
            # 获取员工上下班时间
            time_plan = record.employee.time_plan
            commuter_time = re.findall(r'\d+:\d+', time_plan)
            print("-----------")
            print(commuter_time)

            real_time_list = record.check_sign.split(' ')

            # 真实上班打卡时间
            if real_time_list[0] == "--:--":
                up_start_time = "--:--"
            else:
                # 设置上班打卡时间范围
                up_time_scope = record.set_up_time_scope(commuter_time[0])
                # 真实的上班打卡时间
                real_up_time = datetime.datetime.strptime(real_time_list[0], "%H:%M")

                if real_up_time < up_time_scope["up_start_time"]:

                    # up_start_time = commuter_time[0].strftime("%H:%M") - datetime.timedelta(minutes=10)
                    up_start_time = datetime.datetime.strptime(commuter_time[0], "%H:%M") - datetime.timedelta(minutes=10)
                    up_start_time = up_start_time.strftime("%H:%M")
                else:
                    up_start_time = real_up_time.strftime("%H:%M")
            
            # 真实下班打卡时间
            if real_time_list[1] == "--:--":
                down_end_time = "--:--"
            else:
                # 设置下班打卡时间范围
                down_time_scope = record.set_down_time_scope(commuter_time[1])
                # 真实的下班打卡时间
                real_down_time = datetime.datetime.strptime(real_time_list[1], "%H:%M")

                if real_down_time > down_time_scope["down_end_time"]:

                    # down_end_time = commuter_time[1].strftime("%H:%M") + datetime.timedelta(minutes=10)
                    down_end_time = datetime.datetime.strptime(commuter_time[1], "%H:%M") + datetime.timedelta(minutes=10)
                    down_end_time = down_end_time.strftime("%H:%M")
                else:
                    down_end_time = real_down_time.strftime("%H:%M")


            record.show_time = up_start_time + " " + down_end_time