from odoo import models, fields, api

class EmployeesStatistical(models.Model):
    _name = 'employees_statistical'
    _description = '员工返修统计'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    employee_id = fields.Many2one('hr.employee', string='员工')
    group = fields.Char(string="组别")
    style_number = fields.Many2one("ib.detail", string="款号")
    repair_quantity = fields.Integer(string='返修数量', compute="set_repair_data", store=True)
    check_quantity = fields.Integer(string='查货数量', compute="set_repair_data", store=True)
    repair_ratio = fields.Float(string="返修率", compute="set_repair_data", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核")

    invest_invest_ids = fields.One2many("invest.invest", "employees_statistical_id", string="中查明细")


    @api.depends('invest_invest_ids')
    def set_repair_data(self):
        for record in self:
            
            record.repair_quantity = sum(record.invest_invest_ids.mapped("problem_points_number"))

            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", "=", record.dDate),
                ("style_number", "=", record.style_number.id)
            ])
            if invest_invest_objs:
                record.check_quantity = max(invest_invest_objs.mapped("check_the_quantity"))
            else:
                record.check_quantity = 0

            if record.check_quantity and record.repair_quantity:
                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100
            else:
                record.repair_ratio = 0



class InvestInvest(models.Model):
    _inherit = "invest.invest"

    employees_statistical_id = fields.Many2one("employees_statistical")


    def generate_data(self, comment):

        # 获取员工id
        hr_employee_obj = self.env["hr.employee"].sudo().search([
            ("name", "=", comment)
        ])
        if hr_employee_obj:

            # 员工返修统计
            employees_statistical_obj = self.env["employees_statistical"].sudo().search([
                ("dDate", "=", self.date),      # 日期
                ("employee_id", "=", hr_employee_obj.id),       # 员工
                ("group", "=", self.group),     # 组别
                ("style_number", "=", self.style_number.id)     # 款号
            ])
            if employees_statistical_obj:
                self.employees_statistical_id = employees_statistical_obj.id

            else:
                new_obj = self.env["employees_statistical"].sudo().create({
                    "dDate": self.date,
                    "employee_id": hr_employee_obj.id,
                    "group": self.group,
                    "style_number": self.style_number.id,
                })

                self.employees_statistical_id = new_obj.id



    def set_employees_statistical(self):

        for record in self:

            if record.comment:
                comment = record.comment.strip()

                if "," in comment:
                    staff_name_list = comment.split(",")
                    for staff_name in staff_name_list:
                        record.generate_data(staff_name)

                elif "、" in comment:
                    staff_name_list = comment.split("、")
                    for staff_name in staff_name_list:
                        record.generate_data(staff_name)

                else:
                    record.generate_data(comment)



    @api.model
    def create(self, val):

        instance = super(InvestInvest, self).create(val)

        instance.set_employees_statistical()

        return instance




