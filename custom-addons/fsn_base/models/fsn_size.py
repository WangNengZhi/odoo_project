from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FsnSize(models.Model):
    _name = 'fsn_size'
    _description = 'FSN_尺码'
    _rec_name = 'name'
    _order = "sequence"


    name = fields.Char(string="尺码名称", required=True)
    sequence = fields.Integer()

    @api.constrains('name')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"不可重复创建尺码！")