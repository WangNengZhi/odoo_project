from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FsnSourceWhere(models.Model):
    _name = 'fsn_source_where'
    _description = 'FSN来源与去向'
    _rec_name = 'name'
    # _order = "date desc"


    name = fields.Char(string="名称", required=True)



    @api.constrains('name')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"不可重复创建尺码！")