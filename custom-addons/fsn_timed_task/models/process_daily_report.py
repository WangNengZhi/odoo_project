from datetime import datetime, timedelta

from odoo import models, fields, api


class ProcessDailyReport(models.TransientModel):
    """工时工序检查"""
    _inherit = "fsn_daily"

    def process_piece_count_query(self, today):
        """查询现场工序件数和订单件数不符"""
        # 获取当前日期
        current_date = datetime.now().date()

        # 获取年初日期
        year_start_date = datetime(current_date.year, 1, 1).date()

        result_list = []

        production_processes = self.env['on.work'].search([('state', '=', '未确认'), ('date1', '>=', year_start_date),
                                                           ('date1', '<=', current_date)])
        for production in production_processes:
            order_quantities = self.env['sale_pro.sale_pro'].search([('order_number', '=', production.order_no.order_number),
                                                                     ('sale_pro_line_ids.style_number', '=', production.order_number.id)])
            for order in order_quantities:
                ret = order.sale_pro_line_ids
                for i in ret:
                    if i.voucher_count == production.over_number:
                        production.state = '已确认'

                    if i.voucher_count != production.over_number:
                        data = {
                            'date': production.date1,
                            'order_number': production.order_no.order_number,
                            'style_number': production.order_number.style_number,
                            'work': production.over_number,
                            'sale': i.voucher_count,
                        }
                        result_list.append(data)
        return {'today': today, 'result': result_list}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_production_process_daily(self, today):
        """发送工序工时日报"""
        message_content = {}

        message_content['get_process_piece_count'] = self.env['fsn_daily'].process_piece_count_query(today)
        message_str = f"<b>{message_content['get_process_piece_count']['today']}共有" \
                      f"{len(message_content['get_process_piece_count']['result'])}条工时工序件数大于或小于订单件数:</b><br/>"
        for message in message_content['get_process_piece_count']['result']:
            message_str += f"日期：{message['date']}，订单号：{message['order_number']}，款号：{message['style_number']}，" \
                           f"工时工序件数：{message['work']}，生产订单件数：{message['sale']}<br/>"


        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
