from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PlatformType(models.Model):
    _name = 'platform_type'
    _description = '平台类型'
    _rec_name = 'name'
    _order = "platform_number desc"

    platform_number = fields.Char(string="平台编号")
    name = fields.Char(string="平台名称", required=True)
    note = fields.Char(string="备注")
    is_activity = fields.Boolean(string="启用", default=True)


    # 检查数据唯一性
    @api.constrains('name')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('name', '=', self.name),
        ])

        if len(demo) > 1:
            raise ValidationError(f"平台名称不可重复！")


    @api.model
    def create(self, vals):


        vals['platform_number'] = self.env['ir.sequence'].next_by_code('platform_type')

        return super(PlatformType,self).create(vals)




