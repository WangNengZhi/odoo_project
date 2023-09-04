
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"


    dg_host = fields.Char(string="吊挂系统地址")
    dg_port = fields.Char(string="吊挂系统端口")
    # dg_db_database = fields.Char(string="吊挂数据库名")
    # dg_db_user = fields.Char(string="吊挂数据库用户名")
    # dg_db_password = fields.Char(string="吊挂数据库密码")



