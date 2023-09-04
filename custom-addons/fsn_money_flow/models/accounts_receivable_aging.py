from datetime import datetime, timedelta
from odoo import models, fields, api


class AccountsReceivableAging(models.Model):
    _name = 'accounts_receivable_aging'
    _description = '应收账款账龄分析表'

    date = fields.Date(string='日期')
    aging_1_30_days = fields.Integer(string='账龄0-30天')
    aging_31_60_days = fields.Integer(string='帐龄31-60天')
    aging_61_90_days = fields.Integer(string='帐龄61-90天')
    aging_91_180_days = fields.Integer(string='帐龄91-180天')
    over_180_days = fields.Integer(string='帐龄180天以上')

    def update_aging(self):
        """更新账龄"""
        today = fields.Date.today()
        sales_orders = self.env['fsn_sales_order'].search([
            ('fsn_payment_state', '=', '未付款')
        ])

        aging_data = {
            'date': today,
            'aging_1_30_days': 0,
            'aging_31_60_days': 0,
            'aging_61_90_days': 0,
            'aging_91_180_days': 0,
            'over_180_days': 0
        }

        for sale in sales_orders:
            days_diff = (today - sale.fsn_delivery_date).days

            if 0 <= days_diff <= 30:
                aging_data['aging_1_30_days'] += sale.after_tax_total
            elif 31 <= days_diff <= 60:
                aging_data['aging_31_60_days'] += sale.after_tax_total
            elif 61 <= days_diff <= 90:
                aging_data['aging_61_90_days'] += sale.after_tax_total
            elif 91 <= days_diff <= 180:
                aging_data['aging_91_180_days'] += sale.after_tax_total
            elif days_diff > 180:
                aging_data['over_180_days'] += sale.after_tax_total

        self.sudo().create(aging_data)
