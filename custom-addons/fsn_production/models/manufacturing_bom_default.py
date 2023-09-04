from odoo import models, fields, api

class ManufacturingBomDefault(models.Model):
    _name = 'manufacturing_bom_default'
    _description = 'FSN生产物料清单(预设)'


    name = fields.Char(string="物料名称", required=True)
    type = fields.Selection([('面料', '面料'), ('辅料', '辅料')], string='物料类型', required=True)
    quantity_demanded = fields.Float(string="需求量")
    unit_price = fields.Float(string="单价", digits=(16, 5))