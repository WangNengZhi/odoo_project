import calendar
from datetime import datetime, timedelta

from odoo import models, fields, api

from utils import weixin_utils


class FinancialDailyReport(models.TransientModel):
    """财务对账"""
    _inherit = "fsn_daily"

    def obtain_sale_reconciliation(self):
        today = fields.Date.today()
        current_month = today.month
        _, last_day_of_month = calendar.monthrange(today.year, current_month)

        # 获取数据库中实际存在订单的月份
        months_with_orders = self.env['fsn_sales_order'].search([]).mapped('date')
        months_with_orders = {month.strftime('%Y-%m') for month in months_with_orders}

        result_list = []

        for i in range(12):
            # 计算月份的开始和结束日期
            month_year = today.year
            month_number = current_month - i
            if month_number <= 0:
                month_number += 12
                month_year -= 1
            start_date = datetime(month_year, month_number, 1)
            _, last_day_of_month = calendar.monthrange(month_year, month_number)
            end_date = datetime(month_year, month_number, last_day_of_month)

            month_str = start_date.strftime('%Y-%m')

            if month_str in months_with_orders:
                # 获取该月份的订单记录
                orders_in_month = self.env['fsn_sales_order'].search([
                    ('date', '>=', start_date),
                    ('date', '<=', end_date),
                ])

                # 获取销售明细同月份中的销售价格
                order_lines_in_month = self.env['fsn_sales_order_line'].search([
                    ('fsn_sales_order_id.date', '>=', start_date),
                    ('fsn_sales_order_id.date', '<=', end_date),
                ])

                # 对字段求和
                total_order_sum = sum(order_lines_in_month.mapped('amount'))

                after_tax_total_sum = sum(orders_in_month.mapped('after_tax_total'))
                actual_collection_sum = sum(orders_in_month.mapped('actual_collection'))

                cost_sales_record = self.env['cost_sales'].search([('month', '=', month_str)])
                if cost_sales_record:
                    for cost in cost_sales_record:
                        if cost.order_amount != total_order_sum or cost.completed_amount != after_tax_total_sum or cost.amount_paid != actual_collection_sum:
                            result_dict = {
                                'month': month_str,
                                'total_sales_order': total_order_sum,
                                'total_count': cost.order_amount,
                                'sales_accounts_receivable': after_tax_total_sum,
                                'inventory_completed_amount': cost.completed_amount,
                                'actual_sales_receipts': actual_collection_sum,
                                'inventory_received_amount': cost.amount_paid
                            }
                            result_list.append(result_dict)
        print({'today': today, 'result': result_list})
        return {'today': today, 'result': result_list}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_sales_reconciliation_daily_report(self):
        """销售财务对账"""
        message_content = {}

        message_content['obtain_sale'] = self.env['fsn_daily'].sudo().obtain_sale_reconciliation()

        self.finance_sends_enterprise_wechat(message_content['obtain_sale']['today'], message_content)

        message_str = f"<b>{message_content['obtain_sale']['today']}共有{len(message_content['obtain_sale']['result'])}条销售账款与盘点销售收入不符</b><br/>"
        for message in message_content['obtain_sale']['result']:
            message_str += f"月份：{message['month']}, 销售订单总数价格：{message['total_sales_order']}，盘点已签订单金额：{message['total_count']}" \
                           f"销售应收款：{message['sales_accounts_receivable']}，盘点已完成金额：{message['inventory_completed_amount']}" \
                           f"销售实际收款：{message['actual_sales_receipts']}，盘点已付款金额：{message['inventory_received_amount']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(
            self.env.ref("fsn_timed_task.fsn_finance_daily_inspect_channel1111").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel

    def finance_sends_enterprise_wechat(self, today, message_content):
        """财务对账发送企业微信"""
        messages_list = []

        sales_reconciliation = f"{today}:\n"
        sales_reconciliation += f"共有{len(message_content['obtain_sale']['result'])}条销售账款与盘点销售收入不符\n"

        for i in message_content['obtain_sale']['result']:
            sales_reconciliation += f"月份：{i['month']}, 销售订单总数价格：{i['total_sales_order']}，盘点已签订单金额：{i['total_count']}" \
                           f"销售应收款：{i['sales_accounts_receivable']}，盘点已完成金额：{i['inventory_completed_amount']}" \
                           f"销售实际收款：{i['actual_sales_receipts']}，盘点已付款金额：{i['inventory_received_amount']}\n"
        messages_list.append(sales_reconciliation)

        def send_weixin_messages(messages):
            weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.financial_group)  # 财务群

        for messages in messages_list:
            send_weixin_messages(messages)
