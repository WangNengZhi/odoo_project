from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.expense'


    expenses_detail_statistics_id = fields.Many2one("expenses_detail_statistics", string="成本详情", compute="set_expenses_detail_statistics", store=True)

    @api.depends("date", "cost_type_id", "expense_type_id")
    def set_expenses_detail_statistics(self):
        for record in self:

            if record.cost_type_id and record.expense_type_id:

                *year_month, _ = str(record.date).split("-")
                year_month = '-'.join(year_month)

                expenses_detail_statistics_obj = self.env['expenses_detail_statistics'].sudo().search([
                    ("month", "=", year_month),
                    ("cost_type_id", "=", record.cost_type_id.id),
                    ("expense_type_id", "=", record.expense_type_id.id),
                ])
                if not expenses_detail_statistics_obj:
                    expenses_detail_statistics_obj = self.env['expenses_detail_statistics'].sudo().create({
                        "month": year_month,
                        "cost_type_id": record.cost_type_id.id,
                        "expense_type_id": record.expense_type_id.id
                    })
                if record.expenses_detail_statistics_id:
                    tem_obj = record.expenses_detail_statistics_id
                else:
                    tem_obj = False
                record.expenses_detail_statistics_id = expenses_detail_statistics_obj.id
                if tem_obj:
                    tem_obj.set_expense()



    @api.model
    def create(self, vals):

        res = super(HrEmployee, self).create(vals)

        res.sudo().set_expenses_detail_statistics()

        return res


class ExpensesDetailStatistics(models.Model):
    _name = 'expenses_detail_statistics'
    _description = '成本详情'
    # _rec_name = 'month'
    # _order = 'month desc'


    hr_expense_ids = fields.One2many("hr.expense", "expenses_detail_statistics_id", string="费用")

    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

    cost_type_id = fields.Many2one("cost_type", string="成本类别")

    expense_type_id = fields.Many2one("expense_type", string="费用类别")

    expense = fields.Float(string="费用", compute="set_expense", store=True)
    @api.depends("hr_expense_ids", "hr_expense_ids.total_amount", "hr_expense_ids.date", "hr_expense_ids.cost_type_id", "hr_expense_ids.expense_type_id")
    def set_expense(self):
        for record in self:
            record.expense = sum(record.hr_expense_ids.mapped("total_amount"))


    def test(self):
        for record in self:
            expenses_detail_details_obj = self.env['expenses_detail_details'].sudo().search([("month", "=", record.month), ("expense_type_id", "=", record.expense_type_id.id)])
            if not expenses_detail_details_obj:
                expenses_detail_details_obj = self.env['expenses_detail_details'].sudo().create({
                    "month": record.month,
                    "expense_type_id": record.expense_type_id.id
                })
            # 运输费
            if record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_freight').id:
                expenses_detail_details_obj.transport_cost = record.expense
            # 办公费
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_office').id:
                expenses_detail_details_obj.office_cost = record.expense
            # 生产成本费用
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_production_costs').id:
                expenses_detail_details_obj.production_cost = record.expense
            # 工资费用
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_wages').id:
                expenses_detail_details_obj.wages_cost = record.expense
            # 公积金及社保
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_social_security').id:
                expenses_detail_details_obj.social_security_cost = record.expense
            # 税费
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_taxation').id:
                expenses_detail_details_obj.taxation_cost = record.expense
            # 加油费
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_refueling_fee').id:
                expenses_detail_details_obj.refuelingr_cost = record.expense
            # 员工餐费
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_meals').id:
                expenses_detail_details_obj.staff_meals_cost = record.expense
            # 厂房租金
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_plant_rent').id:
                expenses_detail_details_obj.plant_rent_cost = record.expense
            # 固定资产
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_fixed_assets').id:
                expenses_detail_details_obj.fixed_assets_cost = record.expense

            # 其他费用
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_other_expenses').id:
                expenses_detail_details_obj.other_cost = record.expense
            # 无形资产
            elif record.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_intangible').id:
                expenses_detail_details_obj.intangible_assets = record.expense


class ExpensesDetailDetails(models.Model):
    _name = 'expenses_detail_details'
    _description = '成本详情'

    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")
    expense_type_id = fields.Many2one("expense_type", string="费用类别")
    transport_cost = fields.Float(string="运输费")
    office_cost = fields.Float(string="办公费")
    production_cost = fields.Float(string="生产成本")
    wages_cost = fields.Float(string="工资")
    social_security_cost = fields.Float(string="公积金及社保")
    taxation_cost = fields.Float(string="税费")
    refuelingr_cost = fields.Float(string="加油费")
    staff_meals_cost = fields.Float(string="员工餐费")
    plant_rent_cost = fields.Float(string="厂房租金")
    fixed_assets_cost = fields.Float(string="固定资产")
    other_cost = fields.Float(string="其他费用")
    intangible_assets = fields.Float(string="无形资产")
    total_cost = fields.Float(string="合计", compute="set_total_cost", store=True)
    # 计算合计费用
    @api.depends("transport_cost", "office_cost", "production_cost", "wages_cost", "social_security_cost", "taxation_cost", "refuelingr_cost", "staff_meals_cost", "plant_rent_cost", "fixed_assets_cost", "other_cost", "intangible_assets")
    def set_total_cost(self):

        for obj in self:

            obj.total_cost = obj.transport_cost + obj.office_cost + obj.production_cost + obj.wages_cost + obj.social_security_cost + obj.taxation_cost + obj.refuelingr_cost + obj.staff_meals_cost + obj.plant_rent_cost + obj.fixed_assets_cost + obj.other_cost + obj.intangible_assets



