from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EfficiencyBonusSetting(models.Model):
    _name = 'efficiency_bonus_setting'
    _description = '效率奖金设置'
    _rec_name = 'month'
    # _order = "month desc"

    month = fields.Char(string='月份', required=True)
    workpiece_ratio_lower_limit = fields.Float(string="效率下限")
    workpiece_ratio_upper_limit = fields.Float(string="效率上限")
    bonus_quota = fields.Float(string="奖金额度")

