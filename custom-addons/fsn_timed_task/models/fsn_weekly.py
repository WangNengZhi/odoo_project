from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
import itertools

from utils import weixin_utils

import logging
_logger = logging.getLogger(__name__)

class FsnWeekly(models.TransientModel):
    _name = 'fsn_weekly'
    _description = 'FSN周报'

    # 获取上周日期范围
    def get_last_week_date_range(self, today):
        last_week_start = today - timedelta(days=today.weekday()+7)
        last_week_end = today - timedelta(days=today.weekday()+1)
        return last_week_start, last_week_end

    # 获取两个日期间的所有日期 
    def getEveryDay(self, begin_date, end_date): 
        date_list = [] 
        while begin_date <= end_date: 
            date_str = begin_date.strftime("%Y-%m-%d") 
            date_list.append(date_str) 
            begin_date += timedelta(days=1) 
        return date_list

    # 获取周效率信息
    def get_week_efficiency_info(self, today):

        last_week_start, last_week_end = self.get_last_week_date_range(today)
        
        automatic_efficiency_table_objs = self.env["automatic_efficiency_table"].sudo().search([("date", ">=", last_week_start),("date", "<=", last_week_end)], order="group")

        abnormal_list = []

        for group_obj, group_content_objs in itertools.groupby(automatic_efficiency_table_objs, key=lambda x:x.group.id):     # 按组别分组

            group_content_objs = list(group_content_objs)

            group_content_objs.sort(key=lambda x: x.employee_id.id, reverse=False)     # 按员工排序

            for employee_obj, employee_content_objs in itertools.groupby(group_content_objs, key=lambda x:x.employee_id.id):     # 再按员工分组

                employee_content_objs = list(employee_content_objs)

                average_efficiency = round(sum(i.efficiency for i in employee_content_objs) / len(employee_content_objs), 2)   # 平均效率

                if average_efficiency < 50:
                    abnormal_list.append({"group": group_content_objs[0].group.group, "name": employee_content_objs[0].employee_id.name, "average_efficiency": average_efficiency})


        eff_eff_objs_list = self.env["eff.eff"].sudo().read_group(
            [("group", "=", "裁床"), ("date", ">=", last_week_start), ("date", "<=", last_week_end)],
            ["employee", "totle_eff"],
            groupby=['employee']
        )

        abnormal_list.extend([{"group": "裁床", "name": i["employee"][1], "average_efficiency": round(i["totle_eff"], 2)} for i in eff_eff_objs_list if i["totle_eff"] < 200])



        return {"date": today, "message_content": abnormal_list}

    # 获取周员工入职离职信息
    def get_week_employee_come_out_info(self, today):

        last_week_start, last_week_end = self.get_last_week_date_range(today)
        # 离职员工列表
        departure_list = self.env["hr.employee"].sudo().search_read([('is_delete_date', '>=', last_week_start), ('is_delete_date', '<=', last_week_end)], ["name", "job_id", "is_delete_date"], order="is_delete_date")
        # 入职员工列表
        induction_list = self.env["hr.employee"].sudo().search_read([('entry_time', '>=', last_week_start), ('entry_time', '<=', last_week_end)], ["name", "job_id", "entry_time"], order="entry_time")

        return {"date": today, "message_content": {"departure_list": departure_list, "induction_list": induction_list}}

    # 发送周报
    def send_fsn_weekly(self, today=fields.Date.today(), message_group=False):

        message_content = {}

        # 获取周效率信息
        message_content["week_efficiency_info_content"] = self.get_week_efficiency_info(today)
        _logger.info("获取获取周效率信息成功！")
        # 获取周员工入职离职信息
        message_content["week_employee_come_out_info_content"] = self.get_week_employee_come_out_info(today)
        _logger.info("获取周员工入职离职信息！")


        self.send_to_system_internal(message_content)

        if message_group:
            # 发送企业微信消息
            self.send_to_enterprise_wechat(message_content, message_group)


    # 发送系统内部消息
    def send_to_system_internal(self, message_content):

        message_str = ""
        message_str += f"{message_content['week_efficiency_info_content']['date']}_上周_{len(message_content['week_efficiency_info_content']['message_content'])}个周平均效率异常记录！:<br/>"
        for message in message_content['week_efficiency_info_content']["message_content"]:
            message_str += f"{message['group']}，{message['name']}，周平均效率:{message['average_efficiency']}<br/>"

        message_str += f"{message_content['week_employee_come_out_info_content']['date']}_上周员工入离职信息:<br/>"
        message_str += f"入职{len(message_content['week_employee_come_out_info_content']['message_content']['induction_list'])}人:<br/>"
        for message in message_content['week_employee_come_out_info_content']['message_content']['induction_list']:
            message_str += f"{message['name']}，{message['job_id'][-1]}，入职日期:{message['entry_time']}<br/>"
        message_str += f"离职{len(message_content['week_employee_come_out_info_content']['message_content']['departure_list'])}人:<br/>"
        for message in message_content['week_employee_come_out_info_content']['message_content']['departure_list']:
            message_str += f"{message['name']}，{message['job_id'][-1]}，离职日期:{message['is_delete_date']}<br/>"


        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_weekly_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel

    # 发送企业微信消息
    def send_to_enterprise_wechat(self, message_content, message_group):

        messages_list = []

        week_efficiency_info_content = f"{message_content['week_efficiency_info_content']['date']}:\n上周{len(message_content['week_efficiency_info_content']['message_content'])}个周平均效率异常记录！\n"
        for message in message_content["week_efficiency_info_content"]["message_content"]:
            week_efficiency_info_content += f"{message['group']}，{message['name']}，周平均效率:{message['average_efficiency']}\n"
        messages_list.append(week_efficiency_info_content)


        week_employee_come_out_info_content = f"{message_content['week_employee_come_out_info_content']['date']}_上周员工入离职信息:\n"
        week_employee_come_out_info_content += f"入职{len(message_content['week_employee_come_out_info_content']['message_content']['induction_list'])}人:\n"
        for message in message_content['week_employee_come_out_info_content']['message_content']['induction_list']:
            week_employee_come_out_info_content += f"{message['name']}，{message['job_id'][-1]}，入职日期:{message['entry_time']}\n"
        week_employee_come_out_info_content += f"离职{len(message_content['week_employee_come_out_info_content']['message_content']['departure_list'])}人:\n"
        for message in message_content['week_employee_come_out_info_content']['message_content']['departure_list']:
            week_employee_come_out_info_content += f"{message['name']}，{message['job_id'][-1]}，离职日期:{message['is_delete_date']}\n"
        messages_list.append(week_employee_come_out_info_content)


        def send_weixin_messages(messages):
            if message_group == "管理群":
                weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.ADMIN_GROUP)   # 管理群

            elif message_group == "测试群":
                weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.DEVELOPMENT_AND_TEST)   # 开发测试群

        for messages in messages_list:
            send_weixin_messages(messages)
