from odoo.exceptions import ValidationError
from odoo import models, fields, api


class InvestGeneral(models.Model):
    '''继承总检'''
    _inherit = "general.general"

    secondary_repair_number = fields.Integer(string="二次返修数")
    secondary_check_number = fields.Integer(string="二次返修查货数")
    secondary_delivery_number = fields.Integer(string="二次返修交货数")


    problem_points_number = fields.Integer(string="问题点数")