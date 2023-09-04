from odoo.exceptions import ValidationError
from odoo import models, fields, api



class Salary(models.Model):
    _inherit = "salary"


    compensation_statistics_id = fields.Many2one("compensation_statistics", string="薪酬统计")



    def set_compensation_statistics_id(self):
        for record in self:

            compensation_statistics_obj = self.compensation_statistics_id.sudo().search([("month", "=", record.date), ("department_id", "=", record.first_level_department.id)])
            if compensation_statistics_obj:
                pass
            else:
                compensation_statistics_obj = record.compensation_statistics_id.sudo().create({
                    "month": record.date,
                    "department_id": record.first_level_department.id,
                })
            record.compensation_statistics_id = compensation_statistics_obj.id


    @api.model
    def create(self, vals):

        res = super(Salary, self).create(vals)
        # res.set_compensation_statistics_id()
        
        return res




class Payroll1(models.Model):
    _inherit = "payroll1"


    compensation_statistics_id = fields.Many2one("compensation_statistics", string="薪酬统计")



    def set_compensation_statistics_id(self):
        for record in self:

            compensation_statistics_obj = self.compensation_statistics_id.sudo().search([("month", "=", record.date), ("department_id", "=", record.first_level_department.id)])
            if compensation_statistics_obj:
                pass
            else:
                compensation_statistics_obj = record.compensation_statistics_id.sudo().create({
                    "month": record.date,
                    "department_id": record.first_level_department.id,
                })
            record.compensation_statistics_id = compensation_statistics_obj.id


    @api.model
    def create(self, vals):

        res = super(Payroll1, self).create(vals)
        res.set_compensation_statistics_id()
        
        return res




class CompensationStatistics(models.Model):
    _name = 'compensation_statistics'
    _description = '薪酬统计'
    _order = "month desc"
    _rec_name = 'month'


    salary_ids = fields.One2many("salary", "compensation_statistics_id", string="薪酬明细")
    payroll1_ids = fields.One2many("payroll1", "compensation_statistics_id", string="薪酬明细")
    month = fields.Char(string="月份")
    department_type = fields.Selection([
        ('车间', '车间'),
        ('裁床', '裁床'),
        ('后道', '后道'),
        ('办公室', '办公室'),
    ], string='一级部门')
    department_id = fields.Many2one('hr.department', string="部门")
    number = fields.Integer(string="人数", compute="_set_record_info", store=True)
    total_wages = fields.Float(string="总工资", compute="_set_record_info", store=True)
    average_salary = fields.Float(string="平均工资", compute="_set_record_info", store=True)
    day_average_salary = fields.Float(string="日均工资", compute="_set_record_info", store=True)


    # 计算人数，总工资，平均工资, 日均工资
    @api.depends('payroll1_ids', 'payroll1_ids.salary_payable2', 'payroll1_ids.day_average_salary')
    def _set_record_info(self):
        for record in self:
            record.number = len(record.payroll1_ids)      # 人数
            record.total_wages = sum(record.payroll1_ids.mapped('salary_payable2'))    # 总工资

            if record.number:

                record.average_salary = record.total_wages / record.number      # 平均工资

                record.day_average_salary = sum(record.payroll1_ids.mapped('day_average_salary')) / record.number     # 日均工资






