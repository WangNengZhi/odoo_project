from odoo.exceptions import ValidationError
from odoo import models, fields, api



class ExchangeRest(models.Model):
    _name = 'exchange_rest'
    _description = '调休记录'
    _rec_name = 'employee'


    employee = fields.Many2one('hr.employee', string="员工", required=True)
    department = fields.Many2one("hr.department", string="部门", required=True)
    time_remaining = fields.Float(string="可调休时长", compute="_value_time_remaining", store=True)
    exchange_rest_add_line_ids = fields.One2many("exchange_rest_add_line", "exchange_rest_id", string="调休增加明细")
    exchange_rest_use_line_ids = fields.One2many("exchange_rest_use_line", "exchange_rest_id", string="调休使用明细")


    @api.constrains('employee')
    def _check_employee(self):

        for record in self:
            demo = self.env[record._name].sudo().search([
                ("employee", "=", record.employee.id),
                ])
            if len(demo) > 1:
                raise ValidationError(f"已经存在该员工的调休记录了，请在已有的调休记录上面做修改。")


    @api.depends('exchange_rest_add_line_ids', 'exchange_rest_add_line_ids.hours', 'exchange_rest_use_line_ids', 'exchange_rest_use_line_ids.hours')
    def _value_time_remaining(self):
        for record in self:
            tem_time_remaining = 0

            # 增加时长
            for exchange_rest_add_line_id in record.exchange_rest_add_line_ids:
                tem_time_remaining = tem_time_remaining + exchange_rest_add_line_id.hours

            # 使用时长
            for exchange_rest_use_line_id in record.exchange_rest_use_line_ids:
                tem_time_remaining = tem_time_remaining - exchange_rest_use_line_id.hours

            record.time_remaining = tem_time_remaining



class ExchangeRestAddLine(models.Model):
    _name = 'exchange_rest_add_line'
    _description = '调休增加明细'

    exchange_rest_id = fields.Many2one("exchange_rest", string="调休记录")
    start_date = fields.Datetime('开始日期', required=True)
    end_date = fields.Datetime('结束日期', required=True)
    hours = fields.Float(string='增加时间（小时/h)', required=True)
    remarks = fields.Char(string="备注")
    employee_id = fields.Many2one('hr.employee', string='员工', store=True, compute="set_employee_id")

    # 设置员工
    @api.depends('exchange_rest_id')
    def set_employee_id(self):
        for record in self:
            record.employee_id = record.exchange_rest_id.employee.id



class ExchangeRestUseLine(models.Model):
    _name = 'exchange_rest_use_line'
    _description = '调休使用明细'

    exchange_rest_id = fields.Many2one("exchange_rest", string="调休记录")
    start_date = fields.Datetime('开始日期', required=True)
    end_date = fields.Datetime('结束日期', required=True)
    hours = fields.Float(string='调休时间（小时/h)', required=True)
    remarks = fields.Char(string="备注")
    employee_id = fields.Many2one('hr.employee', string='员工', store=True, compute="set_employee_id")

    # 设置员工
    @api.depends('exchange_rest_id')
    def set_employee_id(self):
        for record in self:
            record.employee_id = record.exchange_rest_id.employee.id


