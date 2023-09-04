# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"


    gst_sql_server_host = fields.Char(string="GST数据库地址")
    gst_sql_server_user = fields.Char(string="GST数据库用户名")
    gst_sql_server_password = fields.Char(string="GST数据库密码")
    gst_sql_server_database = fields.Char(string="GST数据库名")



