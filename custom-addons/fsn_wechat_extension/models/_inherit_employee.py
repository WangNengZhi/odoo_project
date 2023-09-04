from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"


    wx_password = fields.Char(string="微信小程序密码", default="123")