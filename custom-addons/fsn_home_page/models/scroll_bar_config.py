
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ScrollBarConfig(models.Model):
    _name = 'scroll_bar_config'
    _description = '主页滚动条设置'


    content = fields.Char(string="文本内容", required=True)
    user_ids = fields.Many2many("res.users", string="用户")
    is_enable = fields.Boolean(string="启用")