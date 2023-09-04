from odoo.exceptions import ValidationError
from odoo import models, fields, api


class FsnKanbanSetting(models.Model):
    _name = 'fsn_kanban_setting'
    _description = '风丝袅看板设置'


    # data_page = fields.Char(string="数据页面")
    # refresh_frequency = fields.Integer(string="刷新频率")
    template_serial_number = fields.Char(string="模块编号")