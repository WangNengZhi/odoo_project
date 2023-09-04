from odoo import models, fields


class CuttingBedConnectSetting(models.Model):
    _name = 'cutting_bed_connect_setting'
    _description = '自动裁床连接配置'


    key = fields.Char(string="键")
    value = fields.Char(string="值")
