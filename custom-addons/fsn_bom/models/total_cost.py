from odoo.exceptions import ValidationError
from odoo import models, fields, api

class PracticalMaterial(models.Model):
    """ 继承实际用料表"""
    _inherit = 'practical_material'

    total_cost_id = fields.Many2one("total_cost", string="总成本")
    
    def set_practical_material(self):
        for record in self:

            practical_material_obj = self.env['total_cost'].sudo().search([("order_number", "=", record.order_id.id), ("style_number", "=", record.style_number.id)])
            if not practical_material_obj:
                practical_material_obj = self.env['total_cost'].sudo().create({
                    "order_number": record.order_id.id,
                    "style_number": record.style_number.id
                })

            record.total_cost_id = practical_material_obj.id
        

    @api.model
    def create(self, vals):

        res = super(PracticalMaterial, self).create(vals)

        res.sudo().set_practical_material()

        return res





class TotalCost(models.Model):
    _name = 'total_cost'
    _description = '总成本'
    # _rec_name = 'style_number'
    # _order = 'date desc'


    practical_material_ids = fields.One2many("practical_material", "total_cost_id", string="实际用量表")
    mhp_mhp_id = fields.Many2one("mhp.mhp", string="工时成本")

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)

    practical_material_cost = fields.Float(string="实际用量成本", compute="set_practical_material_cost", store=True)
    @api.depends('practical_material_ids')
    def set_practical_material_cost(self):
        for record in self:
            if record.practical_material_ids:
                record.practical_material_cost = sum(record.practical_material_ids.mapped("after_tax_amount"))
            else:
                record.practical_material_cost = 0



    number = fields.Integer(string="件数", compute="set_number", store=True)
    @api.depends('order_number', 'order_number.sale_pro_line_ids', 'order_number.sale_pro_line_ids.actual_cutting_count', 'style_number')
    def set_number(self):
        for record in self:
            if record.order_number and record.style_number:
                if record.order_number.sale_pro_line_ids:
                    record.number = record.order_number.sale_pro_line_ids.filtered(lambda x: x.style_number.id == record.style_number.id).actual_cutting_count
                else:
                    record.number = record.order_number.ib_detail_ids.filtered(lambda x: x.id == record.style_number.id).s_totle
            else:
                record.number = 0

