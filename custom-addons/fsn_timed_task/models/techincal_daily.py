import datetime

from odoo import models, fields, api

from utils import weixin_utils


class TechnicalDaily(models.TransientModel):
    """技术科日报"""
    _inherit = "fsn_daily"

    def obtain_sales_order_information(self, sales_order_record):
        """获取销售订单信息"""
        # 获取当前日期
        today = datetime.date.today()

        sale_list = []
        for line in sales_order_record.fsn_sales_order_line_ids:
            sale_list.append({
                'date': sales_order_record.date,
                'order_number': sales_order_record.sale_pro_ids.order_number,
                'style_number': line.style_number.style_number,
                'attribute': sales_order_record.attribute.name,
                'quantity': line.quantity
            })
        return {'today': today, 'sale_list': sale_list}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_technical_department_daily_report(self, record):
        """发送技术科日报"""

        message_content = {}

        message_content['obtain_sales_order'] = self.env['fsn_daily'].obtain_sales_order_information(record)

        # 消息发送企业微信
        self.technology_sending_enterprise_wechat(message_content['obtain_sales_order']['today'], message_content)

        message_str = f"<b>日期：{message_content['obtain_sales_order']['today']}</b><br/>"
        for message in message_content['obtain_sales_order']['sale_list']:
            message_str += f"下单日期：{message['date']}，单号：{message['order_number']}，款号：{message['style_number']}，属性：{message['attribute']}，件数：{message['quantity']}，已下单<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_technology_section_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel


    def technology_sending_enterprise_wechat(self, today, message_content):
        """发送技术科日报到企业微信"""
        messages_list = []
        sales_reconciliation = f"{today}:\n"
        for i in message_content['obtain_sales_order']['sale_list']:
            sales_reconciliation += f"下单日期：{i['date']}，单号：{i['order_number']}，款号：{i['style_number']}，属性：{i['attribute']}，件数：{i['quantity']}，已下单\n"
        messages_list.append(sales_reconciliation)

        def send_weixin_messages(messages):
            weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.technology_group)  # 技术科群

        for messages in messages_list:
            send_weixin_messages(messages)
