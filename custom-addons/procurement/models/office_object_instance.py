from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfficeObjectInstance(models.Model):
    _name = 'office_object_instance'
    _description = '办公室物品实例'
    _rec_name = 'material_code'



    material_code = fields.Char(string="物品编码")
    material_name = fields.Char(string="物品名称", required=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", store=True, string="供应商", domain=[('is_activity', '=', True)], required=True)
    specification = fields.Char(string="规格", required=True)
    unit = fields.Char(string="单位", required=True)
    is_consumables = fields.Selection([('是', '是'), ('否', '否')], string="是否消耗品", required=True)

    @api.model
    def create(self, vals):

        vals['material_code'] = self.env['ir.sequence'].next_by_code('office_object_instance')

        return super(OfficeObjectInstance,self).create(vals)