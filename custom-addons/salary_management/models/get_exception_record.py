from odoo.exceptions import ValidationError
from odoo import models, fields, api




class GetExceptionRecord(models.Model):
    _name = 'get_exception_record'
    _description = 'FSN薪酬明细'
    _order = "date desc"
    _rec_name = 'date'

    date = fields.Char(string='月份', required=True)
    hr_employee_id = fields.Many2one('hr.employee', string='员工', track_visibility='onchange')