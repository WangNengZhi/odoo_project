
from odoo import models, fields, api
import qrcode

from io import BytesIO
import base64


class CounterSalesOrder(models.Model):
    _name = 'counter_sales_order'
    _description = '柜台销售订单'
    _rec_name = 'order_number'
    # _inherit = ['mail.thread']
    # _order = "order_number"


    date = fields.Date(string="日期")
    order_number = fields.Char(string="订单编号")
    state = fields.Selection([('已完成', '已完成'), ('已取消', '已取消'), ('已退换', '已退换')], string="状态", default="已完成")
    # qr_code = fields.Image(string="二维码", compute="generate_qr_code", store=True)
    order_amount = fields.Float(string="订单金额", compute="set_order_amount", store=True)
    salesman = fields.Many2one('hr.employee', string="售货员")

    customer_name = fields.Char(string="客户姓名")
    customer_phone = fields.Char(string="客户电话")
    customer_address = fields.Text(string="客户地址")

    counter_sales_order_line_ids = fields.One2many("counter_sales_order_line", "counter_sales_order_id", string="柜台销售订单明细")

    # counter_sales_order_return_line_ids = fields.One2many("counter_sales_order_return_line", "counter_sales_order_id", string="柜台销售退换货明细")

    # 计算订单金额
    @api.depends('counter_sales_order_line_ids', 'counter_sales_order_line_ids.total_price')
    def set_order_amount(self):
        for record in self:


            normal_line_objs = record.counter_sales_order_line_ids.sudo().filtered(lambda x: x.state == "正常")

            return_line_objs = record.counter_sales_order_line_ids.sudo().filtered(lambda x: x.state == "退货")

            record.order_amount = sum(normal_line_objs.mapped('total_price')) - sum(return_line_objs.mapped('total_price'))


    @api.model
    def create(self, vals):

        vals['order_number'] = self.env['ir.sequence'].next_by_code('counter_sales_order')

        return super(CounterSalesOrder,self).create(vals)





class CounterSalesOrderLine(models.Model):
    _name = 'counter_sales_order_line'
    _description = '柜台销售订单明细'


    counter_sales_order_id = fields.Many2one("counter_sales_order", ondelete="cascade")
    good_id = fields.Many2one("goods_info", string="商品")
    style_number = fields.Many2one('ib.detail', string='款号', related="good_id.style_number", store=True)
    product_barcode = fields.Char(string="产品编码", related="good_id.product_barcode", store=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="good_id.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", related="good_id.size", store=True)
    number = fields.Integer(string="件数")
    unit_price = fields.Float(string="单价")
    total_price = fields.Float(string="总价", compute="set_total_price", store=True)
    state = fields.Selection([('正常', '正常'), ('退货', '退货'), ('换货', '换货'), ('新增', '新增')], string="状态", default="正常")

    order_line_id = fields.Many2one("counter_sales_order_line", string="退货id")



    # 计算价格
    @api.depends('number', 'unit_price')
    def set_total_price(self):
        for record in self:

            record.total_price = record.unit_price * record.number


class CounterSalesOrderReturnLine(models.Model):
    _name = 'counter_sales_order_return_line'
    _description = '柜台销售订单退换货明细'

#     counter_sales_order_id = fields.Many2one("counter_sales_order", ondelete="cascade")
#     good_id = fields.Many2one("goods_info", string="商品")
#     style_number = fields.Many2one('ib.detail', string='款号', related="good_id.style_number", store=True)
#     product_barcode = fields.Char(string="产品编码", related="good_id.product_barcode", store=True)
#     fsn_color = fields.Many2one("fsn_color", string="颜色", related="good_id.fsn_color", store=True)
#     size = fields.Many2one("fsn_size", string="尺码", related="good_id.size", store=True)
#     number = fields.Integer(string="件数")
#     unit_price = fields.Float(string="单价")
#     total_price = fields.Float(string="总价", compute="set_total_price", store=True)
#     state = fields.Selection([('退货', '退货'), ('换货', '换货'), ('新增', '新增')], string="状态")



#     # 计算价格
#     @api.depends('number', 'unit_price')
#     def set_total_price(self):
#         for record in self:

#             record.total_price = record.unit_price * record.number




