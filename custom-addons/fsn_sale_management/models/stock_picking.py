
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    quantity_completion = fields.Float(string="完成数量", compute='set_quantity_completion', store=True)
    @api.depends("move_ids_without_package", "move_ids_without_package.quantity_done")
    def set_quantity_completion(self):
        for record in self:
            record.quantity_completion = sum(i.quantity_done for i in record.move_ids_without_package)