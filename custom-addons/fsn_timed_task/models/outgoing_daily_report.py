import datetime

from odoo import models, fields, api


class OutgoingDaily(models.TransientModel):
    """外发日报"""
    _inherit = "fsn_daily"

    def get_outbound_orders(self):
        """获取外发订单客户货期大于当前日期并且订单状态未审批"""
        today = datetime.datetime.today()
        previous_day = today.strftime('%Y-%m-%d')

        # tmp_date = '2023-05-26'

        outbound_list = []

        outbound_data = self.env['outsource_order'].search([('customer_delivery_time', '=', previous_day), ('state', '=', '未完成')])
        for outbound in outbound_data:
            order = outbound.order_id.order_number # 订单号
            processing_factory = outbound.outsource_plant_id.name # 加工厂
            head = outbound.responsible_person.name # 负责人
            customer_lead_time = outbound.date # 客户货期
            outbound_list.append({'order': order, 'processing_factory': processing_factory, 'head': head, 'customer_lead_time': customer_lead_time})
        return outbound_list


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_fsn_outbound_orders_daily(self):
        """发送外发日报"""
        message_content = {}
        message_content['get_outbound_orders_data'] = self.env['fsn_daily'].get_outbound_orders()

        message_str = f"{len(message_content['get_outbound_orders_data'])}条外发订单信息异常:<br/>"

        for message in message_content['get_outbound_orders_data']:
            message_str += f"客户货期：{message['customer_lead_time']}，订单号：{message['order']}，" \
                           f"加工厂：{message['processing_factory']}，负责人：{message['head']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
