from odoo import api, fields, models
from utils import weixin_utils

class FsnDaily(models.TransientModel):
    ''' 日报自定义时间'''
    _inherit = 'fsn_daily'


    def get_each_department_number(self, today):
        ''' 获取各部门人数'''

        department_list = ["缝纫一组", "缝纫二组", "缝纫三组", "缝纫四组", "缝纫五组", "缝纫六组", "缝纫七组", "缝纫八组", "缝纫九组", "缝纫十组"]

        dg_attendance_number_list = self.env['dg_attendance'].read_group(
            domain=[("date", "=", today)],
            fields=["department_id"],
            groupby="department_id"
        )

        totality = sum(i["department_id_count"] for i in dg_attendance_number_list)

        dg_attendance_number_list = map(lambda x: {"number": x["department_id_count"] + 1, "group": self.env['hr.department'].browse(x['department_id'][0]).name}, dg_attendance_number_list)
        dg_attendance_number_list = list(filter(lambda x: True if x['group'] in department_list else False, dg_attendance_number_list))

        dg_attendance_number_list.append({"number": totality - sum(i["number"] for i in dg_attendance_number_list), "group": "后道部"})
        # {'number': 16, 'group': '缝纫一组'}
        # {'number': 18, 'group': '缝纫二组'}
        # {'number': 15, 'group': '缝纫五组'}
        # {'number': 7, 'group': '后道部'}
        return dg_attendance_number_list





    def get_daily_dg_per_capita_gdp(self, today):
        ''' 获取吊挂人均产值'''
        parameter = {
            "车缝一组": "缝纫一组",
            "车缝二组": "缝纫二组",
            "车缝三组": "缝纫三组",
            "车缝四组": "缝纫四组",
            "车缝五组": "缝纫五组",
            "车缝六组": "缝纫六组",
            "车缝七组": "缝纫七组",
            "车缝八组": "缝纫八组",
            "车缝九组": "缝纫九组",
            "车缝十组": "缝纫十组",
            "后整": "后道部",
        }

        dg_total_gdp_list = self.env["suspension_system_summary"].read_group(
            domain=[("dDate", "=", today)],
            fields=["group", "production_value"],
            groupby="group"
        )
        for i in dg_total_gdp_list:
            print(i['production_value'], i['group'][-1])

        dg_attendance_number_list = self.get_each_department_number(today)

        for dg_attendance_number_record in dg_attendance_number_list:
            print(dg_attendance_number_record)


        # for dg_total_gdp_record in dg_total_gdp_list:

        #     for dg_attendance_number_record in dg_attendance_number_list:

        #         if parameter.get(dg_total_gdp_record['group'][-1]) and parameter.get(dg_total_gdp_record['group'][-1]) in dg_attendance_number_record["department_id"][-1]:

        #             dg_total_gdp_record["number"] = dg_attendance_number_record["department_id_count"]
        #             if dg_total_gdp_record['number']:
        #                 dg_total_gdp_record["avg_number"] = '{:.2f}'.format(dg_total_gdp_record["production_value"] / dg_total_gdp_record['number'])

        #             break
        
        # return dg_total_gdp_list


    def get_plan_total_gdp_difference(self, today):
        ''' 获取计划总产值差值'''
        # from datetime import timedelta, datetime
        # today = today - timedelta(days=4)

        parameter = {
            "车缝一组": "1组",
            "车缝二组": "2组",
            "车缝三组": "3组",
            "车缝四组": "4组",
            "车缝五组": "5组",
            "车缝六组": "6组",
            "车缝七组": "7组",
            "车缝八组": "8组",
            "车缝九组": "9组",
            "车缝十组": "10组",
            "后整": "后道"
        }
        dg_total_gdp_list = self.get_daily_dg_per_capita_gdp(today)

        plan_output_value_list = self.env['planning.slot'].read_group(
            domain=[("dDate", "=", today)],
            fields=["plan_output_value"],
            groupby="staff_group"
        )

        for dg_total_gdp_record in dg_total_gdp_list:
            
            for plan_output_value_record in plan_output_value_list:

                if parameter.get(dg_total_gdp_record['group'][-1]) and parameter.get(dg_total_gdp_record['group'][-1]) == plan_output_value_record["staff_group"]:

                    dg_total_gdp_record["plan_output_value"] = plan_output_value_record["plan_output_value"]
                    dg_total_gdp_record["difference"] = dg_total_gdp_record["plan_output_value"] - dg_total_gdp_record["production_value"]
                    break
        
        return dg_total_gdp_list


    def send_messages(self, today):

        message_list = self.get_plan_total_gdp_difference(today)

        self.send_enterprise_wechat_message(today, message_list)

        message_str = f"{today}人均产值以及计划产值差值：<br/>"
        
        for message in message_list:

            if "avg_number" in message and "difference" in message:
                message_str += f"组别:{message['group'][-1]}，人均产值:{message['avg_number']}，计划差值:{message['difference']}<br/>"
            elif "difference" in message:
                message_str += f"组别:{message['group'][-1]}，计划差值:{message['difference']}<br/>"
            elif "avg_number" in message:
                message_str += f"组别:{message['group'][-1]}，人均产值:{message['avg_number']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_workshop_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
    

    # 发送企业微信消息
    def send_enterprise_wechat_message(self, today, message_list):

        message_str = f"{today}人均产值以及计划产值差值：\n"

        for message in message_list:

            if "avg_number" in message and "difference" in message:
                message_str += f"组别:{message['group'][-1]}，人均产值:{message['avg_number']}，计划差值:{message['difference']}\n"
            elif "difference" in message:
                message_str += f"组别:{message['group'][-1]}，计划差值:{message['difference']}\n"
            elif "avg_number" in message:
                message_str += f"组别:{message['group'][-1]}，人均产值:{message['avg_number']}\n"

        weixin_utils.send_app_group_info_markdown_weixin(message_str, chatid=weixin_utils.WORK_SHOW)   # 管理群











