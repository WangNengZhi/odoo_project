from odoo.exceptions import ValidationError
from odoo import models, fields, api


class FinishedProductWareLine(models.Model):
    """ 继承仓库明细"""
    _inherit = 'finished_product_ware_line'


    output_value = fields.Float(string="产值", compute="set_enter_warehouse_value", store=True)


    @api.depends('order_number', 'order_number.order_price', 'number')
    def set_enter_warehouse_value(self):
        for record in self:
            if record.order_number and record.number:
                record.output_value = float(record.order_number.order_price) * record.number
            else:
                record.output_value = 0