from odoo import models, fields, api
from odoo.exceptions import ValidationError



class ResCompany(models.Model):
    _inherit = "res.company"

    sql_server_host = fields.Char(string="数据库地址")
    sql_server_user = fields.Char(string="数据库用户名")
    sql_server_password = fields.Char(string="数据库密码")
    sql_server_database = fields.Char(string="数据库名")

