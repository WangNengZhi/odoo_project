from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FsnColor(models.Model):
    _name = 'fsn_color'
    _description = 'FSN_颜色'
    _rec_name = 'name'
    _order = "name desc"


    name = fields.Char(string="颜色名称", required=True)
    code = fields.Char(string="颜色代码", required=True)


    @api.constrains('name', 'code')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search(['|', ('name', '=', record.name), ('code', '=', record.code)])
            if len(demo) > 1:
                raise ValidationError(f"不可重复创建颜色！")

    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.name}({record.code})"
            result.append((record.id, rec_name))
        return result