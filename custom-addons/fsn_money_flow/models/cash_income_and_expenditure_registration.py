from odoo import models, fields, api


class Cash_income_and_expenditure_registration(models.Model):
    """固定资产分类登记表"""
    _name = 'cash_income_and_expenditure_registration'
    _description = '现金收支登记表'
    _rec_name = 'date'

    date = fields.Date(string='日期', required=True)
    income_type = fields.Char(string="收支类别")
    income_name = fields.Char(string="收方", required=True)
    out_name = fields.Char(string="支方", required=True)
    income_date = fields.Char(string="收/支内容", required=True)
    bank = fields.Char(string="银行", required=True)
    number = fields.Char(string="票据号码", required=True)
    money = fields.Integer(string="金额", required=True)
    