from odoo import fields, models, api
from odoo.exceptions import ValidationError
import itertools

class SaleOrder(models.Model):
    ''' 销售订单'''
    _inherit = "sale.order"


    sale_pro_id = fields.Many2one("sale_pro.sale_pro", string="生产订单")
    fsn_customer_order_date = fields.Date(string="下单日期", required=True)
    fsn_purchase_order_number = fields.Char(string="采购单号")
    fsn_payment_state = fields.Selection([("未付款", "未付款"), ("已付款", "已付款")], string="付款状态", default="未付款")
    fsn_delivery_date = fields.Date(string="合同日期", required=True)

    fsn_order_category = fields.Selection([("成衣采购", "成衣采购"), ("承揽加工", "承揽加工")], string="订单类别", required=True)
    quantity_delivered = fields.Float(string="发货数量")
    actual_collection = fields.Float(string="实际收款")

    shipping_status = fields.Selection([("订单取消", "订单取消"), ("等待发货", "等待发货"), ("发货完成", "发货完成")], string="发货状态", default="等待发货", compute='set_shipping_status', store=True)
    @api.depends('order_line', 'order_line.quantity_delivered', 'order_line.product_uom_qty')
    def set_shipping_status(self):
        for record in self:

            if sum(record.order_line.mapped("product_uom_qty")) != 0:

                if sum(record.order_line.mapped("product_uom_qty")) == sum(record.order_line.mapped("quantity_delivered")):
                    record.shipping_status = "发货完成"
                else:
                    record.shipping_status = "等待发货"
            else:
                record.shipping_status = "等待发货"


    fsn_approval_status = fields.Selection([("未审批", "未审批"), ("已审批", "已审批")], string="审批状态", required=True, default="未审批")
    def set_fsn_approval_status(self):
        ''' 设置审批状态'''

        for record in self:
            fsn_approval_status = self.env.context.get("fsn_approval_status")
            if fsn_approval_status == "已审批":
                record.sudo().fsn_approval_status = "已审批"
            elif fsn_approval_status == "未审批":
                record.sudo().fsn_approval_status = "未审批"


    def action_cancel(self):
        if self.fsn_payment_state == "已付款":
            raise ValidationError("已付款的订单无法取消！")
        res = super(SaleOrder, self).action_cancel()

        if self.state == "已取消":
            self.shipping_status = "订单取消"
        else:
            self.shipping_status = "等待发货"
        return res

    def set_fsn_payment_state(self):

        self.fsn_payment_state = self._context.get("type")



    def anto_sync_outbound_data(self):
        ''' 自动同步出库数据'''
        print("-------------------")
        sale_order_objs = self.env['sale.order'].sudo().search([("shipping_status", "=", "等待发货"), ("sale_pro_id", "!=", False)], order="sale_pro_id")

        for sale_pro_id, sale_order_objs in itertools.groupby(sale_order_objs, key=lambda x:x.sale_pro_id.id):

            sale_order_objs_list = list(sale_order_objs)

            sale_order_objs_list.sort(key=lambda x: x.partner_id.id, reverse=False)

            for partner_id, partner_sale_order_objs in itertools.groupby(sale_order_objs_list, key=lambda x: x.partner_id.id):
            
                order_line_list = [i.order_line for i in partner_sale_order_objs]
                order_line_list = [j for i in order_line_list for j in i]
                order_line_list.sort(key=lambda x: x.order_id.fsn_customer_order_date)

                temp_value = 0

                for order_line_obj in order_line_list:

                    color_name, size_name = order_line_obj.product_id.product_template_attribute_value_ids.mapped("name")

                    fsn_color_obj = self.env['fsn_color'].sudo().search([("name", "=", color_name)])
                    fsn_size_obj = self.env['fsn_size'].sudo().search([("name", "=", size_name)])
                    # sale_pro_obj = self.env['sale_pro.sale_pro'].sudo().browse(sale_pro_id)
                    partner_obj = self.env['res.partner'].sudo().browse(partner_id)
                    fsn_customer_obj = self.env['fsn_customer'].sudo().search([("res_partner_id", "=", partner_obj.id)])

                    objs = self.env['finished_product_ware_line'].sudo().search([
                        ("type", "=", "出库"),
                        ("quality", "=", "合格"),
                        ("character", "=", "正常"),
                        ("source_destination", "=", fsn_customer_obj.id),
                        ("order_number", "=", sale_pro_id),
                        ("style_number.style_number_base_id.name", "=", order_line_obj.product_id.name),
                        ("style_number.fsn_color.id", "=", fsn_color_obj.id),
                        ("size", "=", fsn_size_obj.id),
                    ])

                    quantity_delivered = sum(objs.mapped("number"))     # 出库总数

                    if order_line_obj.product_uom_qty >= (quantity_delivered - temp_value):
                        order_line_obj.quantity_delivered = quantity_delivered
                        break
                    else:
                        order_line_obj.quantity_delivered = order_line_obj.product_uom_qty

                    temp_value += order_line_obj.quantity_delivered    




    is_test = fields.Boolean(string="是否备份")

    def test(self):
        ''' 数据迁移'''

        print("-------------------11")
        # objs = self.search([])
        for obj in self:
            
            if obj.fsn_customer_order_date and obj.fsn_delivery_date and obj.fsn_order_category and obj.partner_id:
                print(obj.fsn_customer_order_date, obj.fsn_purchase_order_number, obj.fsn_delivery_date, obj.fsn_order_category, obj.partner_id)

                lines = []

                for line in obj.order_line:

                    color_name, size_name = line.product_id.product_template_attribute_value_ids.mapped("name")

                    fsn_color_obj = self.env['fsn_color'].sudo().search([("name", "=", color_name)])
                    fsn_size_obj = self.env['fsn_size'].sudo().search([("name", "=", size_name)])
                    style_number_base_obj = self.env['style_number_base'].sudo().search([("name", "=", line.product_id.name)])
                    ib_detail_obj = self.env['ib.detail'].sudo().search([("style_number_base_id", "=", style_number_base_obj.id), ("fsn_color", "=", fsn_color_obj.id)], limit=1)

                    account_tax_obj = self.env['account.tax'].sudo().search([("price_include", "=", line.tax_id.price_include), ("amount", "=", line.tax_id.amount)])


                    if account_tax_obj:
                        lines.append((0, 0, {
                            # "style_number_base": style_number_base_obj.id,
                            "style_number": ib_detail_obj.id,
                            "fsn_color_id": fsn_color_obj.id,
                            "product_size": fsn_size_obj.id,
                            "quantity": line.product_uom_qty,
                            "unit_price": line.price_unit,
                            "account_tax_ids": [(4, account_tax_obj.id)]
                        }))
                    else:
                        lines.append((0, 0, {
                            # "style_number_base": style_number_base_obj.id,
                            "style_number": ib_detail_obj.id,
                            "fsn_color_id": fsn_color_obj.id,
                            "product_size": fsn_size_obj.id,
                            "quantity": line.product_uom_qty,
                            "unit_price": line.price_unit,
                        }))

                fsn_sales_order_obj = self.env['fsn_sales_order'].create({
                    "sale_order_id": obj.id,     # 销售订单id
                    "date": obj.fsn_customer_order_date,    # 下单日期
                    "fsn_order_category": obj.fsn_order_category,   # 订单类别
                    "fsn_purchase_order_number": obj.fsn_purchase_order_number,     # 采购单号
                    "fsn_delivery_date": obj.fsn_delivery_date,     # 合同日期
                    "fsn_customer_id": self.env['fsn_customer'].search([("res_partner_id", "=", obj.partner_id.id)]).id,    # 客户
                    "fsn_sales_order_line_ids": lines,
                    "actual_collection": obj.actual_collection,     # 实际付款金额
                    "fsn_payment_state": obj.fsn_payment_state,     # 付款状态
                    "state": "确认",
                })
                if obj.sale_pro_id:
                    fsn_sales_order_obj.sale_pro_ids = [(4, obj.sale_pro_id.id)]







class SaleOrderLine(models.Model):
    ''' 销售订单明细'''
    _inherit = "sale.order.line"


    returned_quantity = fields.Float(string="退回数量", compute='set_returned_quantity', store=True)
    @api.depends('order_id.picking_ids', 'order_id.picking_ids.move_ids_without_package', 'order_id.picking_ids.move_ids_without_package.quantity_done')
    def set_returned_quantity(self):
        for record in self:

           temp_picking_objs = record.order_id.picking_ids.filtered(lambda x: x.picking_type_id.code == "incoming")

           record.returned_quantity = sum(i.quantity_done for i in temp_picking_objs.move_ids_without_package if i.product_id.id == record.product_id.id)


    quantity_delivered = fields.Float(string="出库数量")




