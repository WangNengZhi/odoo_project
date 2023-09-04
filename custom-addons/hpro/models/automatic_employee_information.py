from odoo.exceptions import ValidationError
from odoo import models, fields, api


class AutoEmployeeInformation(models.Model):
    _name='auto_employee_information'
    _description = '自动员工信息'
    _order = 'date desc'

    date = fields.Date('日期')
    employee_id = fields.Many2one('hr.employee', string="员工")
    group_id = fields.Many2one("check_position_settings", string="组别")