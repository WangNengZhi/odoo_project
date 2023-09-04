# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Channel(models.Model):
    _inherit = 'mail.channel'


    def examine_customer_delivery_time(self, message_list):
        # [{'id': 359, 'order_number': '2208502'}]
        # 消息
        message_str = f"{len(message_list)}个订单已经超过计划完成日期！<br/>"
        for message in message_list:
            message_str += f"{message}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("sale_pro.sale_pro_mail_channel_01").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel