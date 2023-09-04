from odoo import models, fields, api

import datetime




class OutsourceOrder(models.Model):
    _inherit = 'outsource_order'

    def set_plan_complete_date(self, outsource_order_obj):
        ''' 设计计划完成日期'''

        production_delivery_time_list = self.env["fsn_month_plan"].sudo().search([("order_number", "=", outsource_order_obj.order_id.id)]).mapped("production_delivery_time")
        outsource_order_obj.plan_finish_date = max(production_delivery_time_list, default=False)


    def automatic_outsource_order(self):
        ''' 自动生成外发订单'''

        current_date = fields.Datetime.now()

        current_date = current_date - datetime.timedelta(days=30)

        sale_pro_objs = self.env['sale_pro.sale_pro'].sudo().search([
            ("is_finish", "not in", ['已完成', '退单']),
            ("processing_type", "=", "外发"),
            ("create_date", ">=", current_date),
            ("sale_pro_line_ids", "!=", False),
        ])

        for sale_pro_obj in sale_pro_objs:

            if not self.env['outsource_order'].sudo().search([("order_id", "=", sale_pro_obj.id)]):

                lines = []

                for sale_pro_obj_line in sale_pro_obj.sale_pro_line_ids:

                    for voucher_detail_obj in sale_pro_obj_line.voucher_details:

                        lines.append((0, 0, {
                            "style_number": sale_pro_obj_line.style_number.id,
                            "size": voucher_detail_obj.size.id,
                            "voucher_count": voucher_detail_obj.number,
                        }))

                outsource_order_obj = self.env['outsource_order'].sudo().create({
                    "date": sale_pro_obj.date,
                    "order_id": sale_pro_obj.id,
                    "outsource_contract": sale_pro_obj.order_number,
                    "style_number": sale_pro_obj.sale_pro_line_ids[0].style_number.id,
                    "customer_delivery_time": sale_pro_obj.customer_delivery_time,
                    "outsource_order_line_ids": lines,
                    "attribute": sale_pro_obj.attribute.id,
                    "product_name": sale_pro_obj.product_name,
                    "style_picture": sale_pro_obj.style_picture
                })


                self.set_plan_complete_date(outsource_order_obj)


