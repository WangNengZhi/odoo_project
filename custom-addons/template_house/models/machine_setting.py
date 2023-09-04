
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    machine_setting_ids = fields.Many2many("machine_setting", string="模板设备配置")





class MachineSetting(models.Model):
    _name = "machine_setting"
    _rec_name = 'Machine_table_name'

    Machine_table_name = fields.Char(string="设备表名")
