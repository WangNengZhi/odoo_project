from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Blacklist(models.Model):
    _name = 'blacklist'
    _description = '黑名单'
    _rec_name = 'numerical_order'
    # _order = "date desc"

    numerical_order = fields.Integer(string="序号")
    name = fields.Char(string="姓名")
    gender = fields.Selection([('male','男'), ('female','女')], string='性别')
    id_number = fields.Char(string='身份证号')
    home_address = fields.Char(string="家庭住址")
    description = fields.Text(string="备注")

    @api.constrains('numerical_order')
    def _check_unique(self):
        for record in self:
            demo = self.env[self._name].sudo().search([('numerical_order', '=', record.numerical_order)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在序号为：{record.numerical_order}的记录了！")
 
