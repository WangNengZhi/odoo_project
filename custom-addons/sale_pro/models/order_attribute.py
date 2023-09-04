from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError


class OrderAttribute(models.Model):
    _name = 'order_attribute'
    _description = '销售订单属性'


    name = fields.Char(string="属性名称", required=True)