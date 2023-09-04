from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FabricIngredientsProcurement(models.Model):
    """ 面辅料采购继承"""
    _inherit = 'fabric_ingredients_procurement'


    material_name_list_id = fields.Many2one("material_name_list", string="物料名称", ondelete='restrict')
    material_name = fields.Char(string="物品名称", compute="set_material_name", store=True)
    @api.depends("material_name_list_id", "material_name_list_id.name")
    def set_material_name(self):
        for record in self:
            if record.material_name_list_id:
                record.material_name = record.material_name_list_id.name
            else:
                record.material_name = False

class MaterialNameList(models.Model):
    _name = 'material_name_list'
    _description = '物料名称列表'

    active = fields.Boolean(default=True)
    name = fields.Char(string="物料名称", required=True)
    material_name_type_id = fields.Many2one("material_name_type", string="物料品类", required=True)


    @api.constrains('name')
    def check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"物料名称不可重复！")


class MaterialNameType(models.Model):
    _name = 'material_name_type'
    _description = '物料品类'


    name = fields.Char(string="品类名称", required=True)


    @api.constrains('name')
    def check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"物料名称不可重复！")