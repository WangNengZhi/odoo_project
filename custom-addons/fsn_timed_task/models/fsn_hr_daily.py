from odoo import models, fields, api
from datetime import timedelta, datetime, date
import itertools

import logging
_logger = logging.getLogger(__name__)

class FsnDaily(models.TransientModel):
    _inherit = "fsn_daily"


    def set_recruitment_info(self, today):
        ''' 获取招聘信息'''

        today = today - timedelta(days=1)

        abnormal_list = []

        appointment_objs = self.env['appointment.recritment'].sudo().search([("date", "=", today)], order="recruiter")

        for appointment_obj in appointment_objs:
            abnormal_list.append({
                "recruiter": appointment_obj.recruiter,
                "interviewer": appointment_obj.name,
                "job_name": appointment_obj.apply_to_position,
                "eligibility": appointment_obj.eligibility,
            })

        return {"date": today, "message_content": abnormal_list}
    

    def get_time_limit_not_recruitment_record(self, today):
        ''' 获取期限无招聘信息的招聘专员'''
        emp_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("job_id.name", "=", "人事招聘专员")])

        # abnormal_list = []
        # for emp_obj in emp_objs:
        #     def get_emp_recruitment_record_list(n):
        #         for i in range(1, n + 1):
        #             temp_date = today - timedelta(days=i)
        #             if self.env['appointment.recritment'].sudo().search(
        #                     [("date", "=", temp_date), ("recruiter", "=", emp_obj.name)]):
        #                 yield False
        #                 return  # 停止迭代并退出函数
        #         yield True
        #
        #     if all(get_emp_recruitment_record_list(3)):
        #
        #         abnormal_list.append({"name": emp_obj.name})
        #
        # # print(abnormal_list)
        # return {"date": today, "message_content": abnormal_list}
        abnormal_list = []
        for emp_obj in emp_objs:

            def has_no_recruitment_record_in_last_n_days(emp_name, n):
                for i in range(1, n + 1):
                    temp_date = today - timedelta(days=i)
                    if self.env['appointment.recritment'].sudo().search(
                            [("date", "=", temp_date), ("recruiter", "=", emp_name)]):
                        return False  # 有招聘记录，返回 False
                return True

            if has_no_recruitment_record_in_last_n_days(emp_obj.name, 3):
                abnormal_list.append({"name": emp_obj.name})
        return {"date": today, "message_content": abnormal_list}


    def get_the_number_of_each_department(self, today):
        """获取各个部门人数"""
        employee_data = self.env['hr.employee'].read_group(
            domain=[('create_date', '<=', str(today)), ('is_delete', '=', False)],
            fields=['department_id'],
            groupby=['department_id'],
            lazy=False
        )
        total = 0
        department_employee_count = {}
        data_list = employee_data[:-1]
        for data in data_list:
            department_id = data['department_id']
            department_id_name = department_id[1].split('/')[-1].strip()
            employee_count = data['__count']
            department_employee_count[department_id_name] = employee_count
            total += employee_count

        result = {
            'date': today,
            'total': total,
            'message_content': [{'department': dept, 'number': str(count)} for dept, count in department_employee_count.items()]
        }
        return result

    def hr_has_no_onboarding_information(self):
        """获取三天入职少于一人招聘专员"""
        # three_days_ago = datetime.now().date() - timedelta(days=3)
        # recruiter_data = []
        # recruiters = self.env['hr.employee'].sudo().search(
        #     [("is_delete", "=", False), ("job_id.name", "=", "人事招聘专员")])
        #
        # for recruiter in recruiters:
        #     staffs = self.env['hr.employee'].sudo().search([('is_delete', '=', False),
        #                                                       ('introducer', '=', recruiter.name),
        #                                                       ('entry_time', '>=', three_days_ago)])
        #     if len(staffs) < 1:
        #         recruiter_data.append({
        #             'name': recruiter.id,
        #             'staffs': len(staffs)
        #         })
        #
        # return recruiter_data
        three_days_ago = datetime.now().date() - timedelta(days=3)
        recruiter_data = []

        recruiters = self.env['hr.employee'].sudo().search(
            [("is_delete", "=", False), ("job_id.name", "=", "人事招聘专员")])

        for recruiter in recruiters:
            # 查询过去3天内由当前招聘专员引荐的员工
            staffs = self.env['hr.employee'].sudo().search([
                ('is_delete', '=', False),
                ('introducer', '=', recruiter.name),
                ('entry_time', '>=', three_days_ago)
            ])
            # 如果没有招聘到员工，将招聘专员添加到列表中
            if len(staffs) < 1:
                recruiter_data.append({
                    'name': recruiter.id,
                    'staffs': len(staffs)
                })
        print(recruiter_data)
        return recruiter_data


class Channel(models.Model):
    _inherit = 'mail.channel'



    # 人事部频道
    def fsn_hr_inspect_channel_messages(self, message_list):

        _logger.info('开始发送人事频道信息01')
        message_str = f"{message_list['yesterday_employee_situation_messages_content']['date']}<br/>"
        message_str += f"入职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['induction_list'])}<br/>"
        for induction in message_list['yesterday_employee_situation_messages_content']['message_content']['induction_list']:
            message_str += f"{induction['name']}，{induction['job_name']}<br/>"
        message_str += f"离职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['departure_list'])}<br/>"
        for departure in message_list['yesterday_employee_situation_messages_content']['message_content']['departure_list']:
            message_str += f"{departure['name']}，{departure['job_name']}<br/>"
        message_str += f"在职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['yesterday_list'])}<br/>"


        message_str += "<br/>"
        _logger.info('开始发送人事频道信息02')
        message_str += f"<b>{message_list['recruitment_info']['date']}_{len(message_list['recruitment_info']['message_content'])}个人事招聘信息:</b><br/>"
        for message in message_list["recruitment_info"]["message_content"]:
            message_str += f"招聘者：{message['recruiter']}，面试人:{message['interviewer']}，面试岗位:{message['job_name']}，是否合格:{message['eligibility']}<br/>"


        message_str += "<br/>"
        _logger.info('开始发送人事频道信息03')
        message_str += f"<b>{message_list['time_limit_not_recruitment_record']['date']}_{len(message_list['time_limit_not_recruitment_record']['message_content'])}连续三天无招聘记录！:</b><br/>"
        for message in message_list["time_limit_not_recruitment_record"]["message_content"]:
            message_str += f"员工姓名：{message['name']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送人事频道信息04')
        message_str += f"<b>{message_list['the_number_of_each_department']['date']}_{len(message_list['the_number_of_each_department']['message_content'])}所有部门人数:{message_list['the_number_of_each_department']['total']}人</b><br/>"
        for message in message_list["the_number_of_each_department"]["message_content"]:
            department = message['department']
            number = message['number']
            message_str += f"{department:<12}：部门人数{number}人<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_hr_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
