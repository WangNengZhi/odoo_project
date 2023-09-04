from odoo import fields, models, api
from odoo.exceptions import ValidationError



class InheritIbDetail(models.Model):
    _inherit = "ib.detail"


    fsn_color = fields.Many2one("fsn_color", string="颜色", required=True,)


    style_number_base_id = fields.Many2one("style_number_base", string="款号前缀", compute="set_style_number_base_id", store=True)
    @api.depends('style_number_base')
    def set_style_number_base_id(self):
        for record in self:
            if record.style_number_base:

                style_number_base_obj = self.env['style_number_base'].sudo().search([("name", "=", record.style_number_base)])
                if not style_number_base_obj:
                    style_number_base_obj = self.env['style_number_base'].sudo().create({"name": record.style_number_base})
                
                record.style_number_base_id = style_number_base_obj.id
            
            else:
                record.style_number_base_id = False
                


class StyleNumberBase(models.Model):
    _name = "style_number_base"
    _description = '款号前缀（产品编码）'


    ib_detail_ids = fields.One2many("ib.detail", "style_number_base_id")
    name = fields.Char(string="款号前缀")

    # 检查数据唯一性
    @api.constrains('name')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('name', '=', self.name)
        ])

        if len(demo) > 1:
            raise ValidationError("已经该名字的款号前缀了！请联系管理员！")