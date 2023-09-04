import datetime

from odoo import models, fields, api


class SaleReturn(models.TransientModel):
    """销售退货与仓库退货对应"""
    _inherit = "fsn_daily"

    def obtain_customer_return_information(self):
        # 查询所有销售订单
        sales_orders = self.env['fsn_sales_order'].search([])

        result_list = []

        today = datetime.date.today()

        # 遍历销售订单
        for order in sales_orders:
            order_lines = order.fsn_sales_order_line_ids  # 获取关联的销售订单明细

            # 从销售订单明细中获取款号和退货数量
            style_numbers = order_lines.mapped('style_number')
            quantities_returned = order_lines.mapped('quantity_returned')

            print("订单编号:", order.sale_pro_ids.order_number)
            for style_number, quantity_returned in zip(style_numbers, quantities_returned):
                print("款号:", style_number.style_number)
                print("退货数量:", quantity_returned)

                finished = self.env['finished_product_ware_line'].search([('character', '=', '退货'),
                                                                          # ('order_number', '=',order.sale_pro_ids.order_number),
                                                                          # ('style_number', '=', style_number.style_number)
                                                                          ('order_number', '=', order.sale_pro_ids.id),
                                                                          ('style_number', '=', style_number.id)
                                                                          ])

                for fin in finished:
                    print("finished_product_ware_line数量:", fin.number)
                    print("fsn_sales_order_line数量:", quantity_returned)
                    if fin.number != quantity_returned:
                        result_dict = {
                            'date': order.date,
                            'order_number': order.sale_pro_ids.order_number,
                            'style_number': style_number.style_number,
                            'return_quantity': quantity_returned,
                            'number_of_warehouse_items': fin.number
                        }
                        result_list.append(result_dict)
        print(result_list)
        return {'today': today, 'result_list': result_list}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_sales_return_comparison_daily_report(self):
        """发送销售退货数量和仓库退货数量不符 """
        message_content = {}

        message_content['obtain_customer'] = self.env['fsn_daily'].sudo().obtain_customer_return_information()

        message_str = f"<b>{message_content['obtain_customer']['today']}共有{len(message_content['obtain_customer']['result_list'])}" \
                      f"条销售退货件数与仓库退货件数不符：</b><br/>"
        for message in message_content['obtain_customer']['result_list']:
            message_str += f"下单日期：{message['date']}，订单号：{message['order_number']}，款号：{message['style_number']}， " \
                           f"销售退货件数：{message['return_quantity']}, 仓库退货件数：{message['number_of_warehouse_items']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_sales_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
