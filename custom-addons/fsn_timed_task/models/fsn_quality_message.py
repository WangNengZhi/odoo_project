from datetime import datetime, timedelta
from collections import Counter

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class Quality(models.TransientModel):
    _inherit = "fsn_daily"

    def get_quality_data(self, today):
        qualities = self.get_general_inspection_abnormal_info(today)
        return qualities

    def get_return_within(self):
        """获取30天内退货件数"""
        # 计算30天前的日期
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)

        domain = [
            ('create_date', '>=', thirty_days_ago),
            ('create_date', '<=', today),
            ('check_type', '=', '客户'),
            ('repair_number', '!=', 0)
        ]

        return_orders = self.env['client_ware'].search(domain)
        total_repair_number = sum(return_order.repair_number for return_order in return_orders)
        return {'total_repair_number': total_repair_number}

    def get_return_of_the_month(self):
        """
        客户货期是当月的退货件数
        获取当月退货件数
        """
        current_date = datetime.now().date()
        start_of_month = current_date.replace(day=1)
        end_of_month = start_of_month + relativedelta(months=1, days=-1)

        domain = [
            ('check_type', '=', '客户'),
            ("order_number.customer_delivery_time", ">=", start_of_month),
            ("order_number.customer_delivery_time", "<=", end_of_month),
            ('repair_number', '!=', 0)
        ]

        orders = self.env['client_ware'].search(domain)
        total = sum(order.repair_number for order in orders)
        return {'total': total}


    def get_return_last_month(self):
        """
         客户货期是上月的退货件数
         获取上月退货件数
        """
        current_date = datetime.now().date()
        start_of_last_month = (current_date - relativedelta(months=1)).replace(day=1)
        end_of_last_month = current_date.replace(day=1) - relativedelta(days=1)

        domain = [
            ('order_number.customer_delivery_time', '>=', start_of_last_month),
            ('order_number.customer_delivery_time', '<=', end_of_last_month),
            ('repair_number', '!=', 0),
            ('check_type', '=', '客户'),
        ]

        orders = self.env['client_ware'].search(domain)
        total = sum(order.repair_number for order in orders)
        return {'total': total}

    def order_completed(self, today):
        """
        获取订单完成时（客户货期后一天）
        """
        # tmp_date = datetime.strptime('2023-02-9', '%Y-%m-%d').date()
        # time_desired = tmp_date - timedelta(days=1)
        #
        # # desired_date = today - timedelta(days=1)
        # records = self.env['schedule_production'].search([
        #     ('date_contract', '=', time_desired),
        #     ('difference_delivery', '!=', 0),
        #     ('lock_state', '=', '未审批')
        # ])
        #
        # abnormal_list = []
        # for record in records:
        #
        #     if record.style_number.style_number.split("-")[1] == "0":
        #         suspension_system_station_summary_obj = self.env['suspension_system_station_summary'].sudo().search([
        #             ("order_number", "=", record.order_number.id),
        #             ("style_number", "=", record.style_number.id),
        #             ("job_id.name", "=", "中查")
        #         ], limit=1)
        #
        #         if suspension_system_station_summary_obj:
        #             invest = suspension_system_station_summary_obj.employee_id.name
        #         else:
        #             invest = "无"
        #     elif record.style_number.style_number.split("-")[1] == "1":
        #
        #         emp_obj = self.env['hr.employee'].sudo().search([("job_id.name", "=", "生产总监"), ("is_delete", "=", False)], limit=1)
        #         if not emp_obj:
        #             emp_obj = self.env['hr.employee'].sudo().search([("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1)
        #         if emp_obj:
        #             invest = emp_obj.name
        #
        #         else:
        #             invest = "无"
        #
        #     else:
        #         invest = "无"
        #
        #     production_group_ids = record.order_number.production_group_ids.mapped('name')
        #     group_ids_string = ', '.join(production_group_ids)
        #
        #     abnormal_list.append({
        #         "invest": invest,
        #         "order_number": record.order_number.order_number,
        #         "date_order": record.date_order,
        #         'date_contract': record.date_contract,
        #         "production_group_ids": group_ids_string,
        #         "difference_delivery": record.difference_delivery,
        #         "style_number": record.style_number.style_number,
        #         "size": record.size.name
        #     })
        # return abnormal_list

        # tmp_date = datetime.strptime('2023-02-9', '%Y-%m-%d').date()
        # time_desired = tmp_date - timedelta(days=1)

        desired_date = today - timedelta(days=1)
        records = self.env['schedule_production'].search([
            ('date_contract', '=', desired_date),
            ('difference_delivery', '!=', 0),
            ('lock_state', '=', '未审批')
        ])

        abnormal_list = []
        invest = "无"  # 初始化 invest 变量

        for record in records:
            if record.style_number.style_number.split("-")[1] == "0":

                suspension_system_station_summary_obj = self.env['suspension_system_station_summary'].sudo().search(
                    [
                        ("order_number", "=", record.order_number.id),
                        ("style_number", "=", record.style_number.id),
                        ("job_id.name", "=", "中查")
                    ], limit=1)

                if suspension_system_station_summary_obj:
                    invest = suspension_system_station_summary_obj.employee_id.name

            elif record.style_number.style_number.split("-")[1] == "1":
                emp_obj = self.env['hr.employee'].sudo().search(
                    [("job_id.name", "=", "生产总监"), ("is_delete", "=", False)], limit=1)
                if not emp_obj:
                    emp_obj = self.env['hr.employee'].sudo().search(
                        [("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1)
                if emp_obj:
                    invest = emp_obj.name

            # 无需 else 分支，因为 invest 已经初始化为 "无"

            production_group_ids = record.order_number.production_group_ids.mapped('name')
            group_ids_string = ', '.join(production_group_ids)

            abnormal_list.append({
                "invest": invest,
                "order_number": record.order_number.order_number,
                "date_order": record.date_order,
                'date_contract': record.date_contract,
                "production_group_ids": group_ids_string,
                "difference_delivery": record.difference_delivery,
                "style_number": record.style_number.style_number,
                "size": record.size.name
            })
        return abnormal_list


class Channel(models.Model):
    _inherit = 'mail.channel'

    # 品控
    def send_fsn_quality_daily(self, today):
        """发送品控日报"""
        message_content = {}
        message_content['get_quality_data']= self.env['fsn_daily'].get_quality_data(today)
        # 获取30天内退货件数
        message_content['get_return_within'] = self.env['fsn_daily'].get_return_within()
        # 获取当月退货件数
        message_content['get_return_of_the_month'] = self.env['fsn_daily'].get_return_of_the_month()
        # 获取上月退货件数
        message_content['get_return_last_month'] = self.env['fsn_daily'].get_return_last_month()
        # 获取订单完成时（客户货期后一天）
        abnormal_list = self.env['fsn_daily'].order_completed(today)

        message_str = f"{message_content['get_quality_data']['date']}_{len(message_content['get_quality_data']['message_content'])}总检异常信息:<br/>"
        for message in message_content["get_quality_data"]["message_content"]:
            message_str += f"员工：{message['general1']}，查货数：{message['general_number']}，吊挂查货数:{message['dg_general_number']}，返修数:{message['repair_number']}，吊挂返修数:{message['dg_repair_number']}<br/>"


        message_str += f"<br/>{today}客仓退货信息：<br/>"
        message_str += f"30天内客户退货件数：{message_content['get_return_within']['total_repair_number']}件<br/>"
        message_str += f"客户货期在当月的退货件数：{message_content['get_return_of_the_month']['total']}件<br/>"
        message_str += f"客户货期在上月的退货件数：{message_content['get_return_last_month']['total']}件<br/>"


        message_str += f"<br/>{today}订单完成后,车间交货差异异常信息：<br/>"
        for message in abnormal_list:
            message_str += f"订单编号:{message['order_number']}，下单日期:{message['date_order']}， " \
                           f"合同日期:{message['date_contract']}，组别:{str(message['production_group_ids'])}，检组:{message['invest']}，" \
                           f"车间交货差异:{message['difference_delivery']}，款号:{message['style_number']}，" \
                           f"尺码:{message['size']}<br/>"



        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_quality_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
