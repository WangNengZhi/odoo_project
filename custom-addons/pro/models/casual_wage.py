from odoo.exceptions import ValidationError
from odoo import models, fields, api



class CasualWage(models.Model):
    _name = 'casual_wage'
    _description = '临时工工资'
    _order = 'dDate'

    
    dDate = fields.Date(string='日期')
    employee_id = fields.Many2one('hr.employee', string="员工")
    contract_type = fields.Char(string="合同")
    group = fields.Char(string='组别')
    number = fields.Float(string="件数")
    price = fields.Float(string="价格")
    cost = fields.Float(string='工资', compute="set_cost", store=True)


    # 设置件数
    def set_data(self):
        for record in self:

            on_work_objs = self.env["on.work"].sudo().search([
                ("date1", "=", record.dDate),   # 日期
                ("employee", "=", record.employee_id.id),   # 员工
            ])

            tem_number = 0
            for on_work_obj in on_work_objs:
                tem_number = tem_number + on_work_obj.over_number
            
            record.number = tem_number


    # 设置工资
    @api.depends('number', 'price')
    def set_cost(self):
        for record in self:

            record.cost = record.number * record.price

            


            

