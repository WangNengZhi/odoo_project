from odoo import fields, models, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    ''' 生产订单'''
    _inherit = "sale_pro.sale_pro"


    sale_order_ids = fields.One2many("sale.order", "sale_pro_id", string="销售订单")