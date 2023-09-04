from odoo.exceptions import ValidationError
from odoo import models, fields, api


class DataRefreshFrequency(models.Model):
    _name = 'data_refresh_frequency'
    _description = '数据刷新频率'


    data_page = fields.Char(string="数据页面")
    refresh_frequency = fields.Integer(string="刷新频率")

