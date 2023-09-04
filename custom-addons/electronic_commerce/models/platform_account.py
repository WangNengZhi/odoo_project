from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PlatformAccount(models.Model):
    _name = 'platform_account'
    _description = '平台账号'
    _rec_name = 'name'
    # _order = "platform_number desc"

    platform_type_id = fields.Many2one("platform_type", string="平台", required=True)
    name = fields.Char(string="昵称", required=True)
    account = fields.Char(string="账号", required=True)