from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FsnUnit(models.Model):
    _name = 'fsn_unit'
    _description = 'FSN_单位'
    _rec_name = 'name'
    _order = "name desc"


    name = fields.Char(string="单位名称", required=True)

    @api.constrains('name')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"不可重复创建尺码！")