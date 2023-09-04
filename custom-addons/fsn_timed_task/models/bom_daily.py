import datetime

from odoo import models, fields, api


class BomDaily(models.TransientModel):
    """bom用量异常信息发送日报"""
    _inherit = "fsn_daily"

    def obtain_bom_exception_information(self):
        """获取bom汇总计划用量与实际用量不服偏差大于或者小于千分之三"""

        objs = self.env['material_summary_sheet'].search([("date_order", ">=", "2023-07-01"), ('state', '=', '未确认')])

        today = datetime.date.today()

        exception_list = []
        for obj in objs:
            if (obj.actual_usage > (obj.outbound_dosage + obj.outbound_dosage * 0.003)) or (obj.actual_usage < (obj.outbound_dosage - obj.outbound_dosage * 0.003)):
                exception_list.append(
                    {
                        "date_order": obj.date_order,
                        "order_id": obj.order_id.order_number,
                        "name": obj.material_name,
                        "type": obj.material_type,
                        "actual_usage": obj.actual_usage,
                        "outbound_dosage": obj.outbound_dosage,
                        "style_number": obj.style_number.style_number,
                    }
                )
        # return exception_list
        return {'today': today, 'exception_list': exception_list}

    def abnormal_bom_procurement_usage(self):
        """bom采购异常的等于库存量+出库量"""
        objs = self.env['material_summary_sheet'].search([("date_order", ">=", "2023-07-01"), ('state', '=', '未确认')])

        today = datetime.date.today()
        abnormal_procurement = []
        for obj in objs:
            if obj.actual_dosage != (obj.inventory_dosage + obj.outbound_dosage):
                abnormal_procurement.append(
                    {
                        "date_order": obj.date_order,
                        "order_id": obj.order_id.order_number,
                        "name": obj.material_name,
                        "type": obj.material_type,
                        "style_number": obj.style_number.style_number,
                    }
                )
        return {'today': today, 'abnormal_procurement': abnormal_procurement}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_fsn_bom_daily(self):
        """发送bom日报"""

        message_content = self.env['fsn_daily'].obtain_bom_exception_information()

        abnormal_bom = self.env['fsn_daily'].abnormal_bom_procurement_usage()

        message_str = f"<b>{message_content['today']}共有{len(message_content['exception_list'])}条bom物料实际用量与出库用量不符差大于或者小于千分之三:</b><br/>"
        # for message in message_content['exception_list']:
        #     message_str += f"下单日期：{message['date_order']}，订单号：{message['order_id']}，物料名称：{message['name']}，" \
        #                    f"款号：{message['style_number']}，实际用量：{message['actual_usage']}，出库用量：{message['outbound_dosage']}<br/>"

        message_str += '<br/>'

        message_str += f"<b>{abnormal_bom['today']}共有{len(abnormal_bom['abnormal_procurement'])}条bom物料库存量与出库量之和不等于采购用量:</b><br/>"
        for message in abnormal_bom['abnormal_procurement']:
            message_str += f"下单日期：{message['date_order']}，订单号：{message['order_id']}，物料名称：{message['name']}， 款号：{message['style_number']}<br/>"


        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
