
from odoo import api, fields, models
from datetime import timedelta, datetime

from utils import weixin_utils

import logging

_logger = logging.getLogger(__name__)


class SuspensionSystemStationSummary(models.Model):
    _inherit = "suspension_system_station_summary"

    last_number = fields.Integer(string="上次件数")


    def set_last_number(self, today):
        ''' 设置上一次件数'''

        suspension_system_station_summary_objs = self.env["suspension_system_station_summary"].sudo().search([("dDate", "=", today)])
        for suspension_system_station_summary_obj in suspension_system_station_summary_objs:
            suspension_system_station_summary_obj.last_number = suspension_system_station_summary_obj.total_quantity


    def get_dg_personal_data_timing(self, today):
        ''' 定时获取吊挂个人数据'''

        # 提交事务
        self.env.cr.commit()

        message_list = []

        read_group_list = self.env["suspension_system_station_summary"].sudo().read_group([("dDate", "=", today)],
            fields=['group:array_agg', "last_number", "total_quantity"],
            groupby=['employee_id']
        )

        for record in read_group_list:


            if record["last_number"] == record["total_quantity"] and record["employee_id"]:

                message_list.append({
                    "date": today,
                    "name": record["employee_id"][1],
                    "job_name": self.env["hr.employee"].sudo().browse(record["employee_id"][0]).job_id.name,
                    "group": "_".join(self.env["check_position_settings"].sudo().browse(i).group for i in list(set(record["group"]))),
                    "last_number": record["last_number"],
                    "this_number": record["total_quantity"]
                })


        self.set_last_number(today)

        return message_list
    

    def add_dg_abnormal_record(self, message):
        ''' 增加中层管理，吊挂异常记录明细'''
        if "dg_abnormal_record" in self.env:

            self.env['dg_abnormal_record'].sudo().create({"name": message['name'], "group": message['group']})

    # 发送消息
    def send_workshop_message(self, today):

        # 当前时间
        current_time = fields.Datetime.now() + timedelta(hours=8)
        # 凌晨时间
        morning_time = current_time - timedelta(hours=current_time.hour, minutes=current_time.minute, seconds=current_time.second)
        # 开始时间
        start_time = morning_time + timedelta(hours=8)
        # 结束时间
        end_time = morning_time + timedelta(hours=23)
        # 设置时间范围
        if start_time < current_time and current_time < end_time:

            message_list = self.get_dg_personal_data_timing(today)

            self.send_enterprise_wechat_message(message_list)

            message_str = f"{current_time}吊挂异常记录:{len(message_list)}条<br/>"
            for message in message_list:

                message_str += f"{message['date']}，{message['name']}，{message['job_name']}，上次件数:{message['last_number']}，本次件数:{message['this_number']}，{message['group']}<br/>"
                try:    
                    self.add_dg_abnormal_record(message)
                except Exception as e:
                    _logger.warning(e)

            # 发送人
            odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
            # 发送频道
            channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_workshop_inspect_channel").id)

            channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
            return channel


    # 发送企业微信消息
    def send_enterprise_wechat_message(self, message_list):
        ''' 发送企业微信消息'''

        message_str = f"{fields.Datetime.now() + timedelta(hours=8)}吊挂异常记录:{len(message_list)}条\n"

        for message in message_list:
            message_str += f"{message['date']}，{message['name']}，{message['job_name']}，上次件数:{message['last_number']}，本次件数:{message['this_number']}，{message['group']}。\n"

        weixin_utils.send_app_group_info_markdown_weixin(message_str, chatid=weixin_utils.WORK_SHOW)   # 管理群




