from odoo import models, fields, api

class ManufacturingBom(models.Model):
    _name = 'manufacturing_bom'
    _description = 'FSN生产物料清单'
    # _rec_name = 'style_number'
    # _order = "style_number desc"



    manufacturing_order_line_id = fields.Many2one("manufacturing_order_line", string="生产工单明细id", ondelete="cascade")
    name = fields.Char(string="物料名称")
    type = fields.Selection([('面料', '面料'), ('辅料', '辅料')], string='物料类型')
    quantity_demanded = fields.Float(string="需求量")
    unit_price = fields.Float(string="单价", digits=(16, 5))
    price = fields.Float(string="价格", compute="_value_price", store=True, digits=(16, 5))

    reserved_amount = fields.Float(string="已备好")



    # 计算价格
    @api.depends('quantity_demanded', 'unit_price')
    def _value_price(self):
        for record in self:
            record.price = record.quantity_demanded * record.unit_price
