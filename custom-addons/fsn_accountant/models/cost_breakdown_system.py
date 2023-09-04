from odoo import models, fields, api


class CostBreakdownSystem(models.Model):
    _name = "cost_breakdown_system"
    _description = '费用明细(系统)'

    date = fields.Date(string='日期')
    parent_account = fields.Many2one("cost_type", string="父级科目")
    account = fields.Many2one("expense_type", string="所属科目")
    cost = fields.Float(string='费用')

    def renewal_expense(self):
        """更新费用"""
        expenses = self.env['hr.expense'].search([])

        for e in expenses:
            existing_record = self.env['cost_breakdown_system'].search([
                ('date', '=', e.date),
                ('parent_account', '=', e.cost_type_id.id),
                ('account', '=', e.expense_type_id.id)
            ])

            if not existing_record:
                expense_data = {
                    'date': e.date,
                    'parent_account': e.cost_type_id.id,
                    'account': e.expense_type_id.id,
                    'cost': e.total_amount
                }
                self.sudo().create(expense_data)
