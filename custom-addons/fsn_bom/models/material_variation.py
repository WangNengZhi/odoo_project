
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class MaterialPreset(models.Model):
    _name = 'material_preset'
    _description = '物料预设'


    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'), 
        ], string="类型", required=True)
    material_name_list_id = fields.Many2one("material_name_list", string="物料名称")
    name = fields.Char(string="名称", compute="set_name", store=True)
    @api.depends("material_name_list_id", "material_name_list_id.name")
    def set_name(self):
        for record in self:
            if record.material_name_list_id:
                record.name = record.material_name_list_id.name
            else:
                record.name = False

    unit = fields.Char(string="单位")
    unit_id = fields.Many2one("fsn_unit", string="单位", required=True)
    is_size = fields.Boolean(string="是否分尺码")

    variation_preset_ids = fields.One2many("variation_preset", "material_preset_id", string="变体预设")


class VariationPreset(models.Model):
    _name = 'variation_preset'
    _description = '变体预设'

    material_preset_id = fields.Many2one("material_preset", string="物料预设")
    key = fields.Many2one("variation_preset_key", string="属性")
    value = fields.Many2one("variation_preset_value", string="值")


    @api.onchange('key')
    def _onchange_value(self):

        self.value = False

        if self.key:
            return {'domain': {'value': [('variation_preset_key_ids', '=', self.key.id)]}}
        else:
            return {'domain': {'value': []}}


class MaterialVariation(models.Model):
    _name = 'variation_preset_key'
    _description = '变体预设属性'

class VariationPresetKey(models.Model):
    _name = 'variation_preset_key'
    _description = '变体预设属性'

    name = fields.Char(string="属性", required=True)
    variation_preset_value_ids = fields.One2many("variation_preset_value", "variation_preset_key_ids", string="值")

class VariationPresetValue(models.Model):
    _name = 'variation_preset_value'
    _description = '变体预设属性'

    variation_preset_key_ids = fields.Many2one("variation_preset_key", string="属性", required=True)
    name = fields.Char(string="值", required=True)


    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.variation_preset_key_ids.name}:{record.name}"
            result.append((record.id, rec_name))
        return result


