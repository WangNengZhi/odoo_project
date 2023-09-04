from odoo.exceptions import ValidationError
from odoo import models, fields, api


class FsnDgSetting(models.Model):
    _name = 'fsn_dg_setting'
    _description = '吊挂设置'

    key = fields.Char(string="Key")
    value = fields.Char(string="Value")
