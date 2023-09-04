from odoo.exceptions import ValidationError
from odoo import models, fields, api


class BankAccount(models.Model):
    _name = 'bank_account'
    _description = 'fsn_银行记账'

    date = fields.Date(string="付款日期", required=True)
    personage_or_unit = fields.Char(string="付款单位/个人")
    category = fields.Many2one("account_type", string="类别")
    income = fields.Float(string="收入")
    expenditure = fields.Float(string="支出")
    bank_or_cash = fields.Selection([('银行', '银行'),('现金', '现金')], string="银行/现金")
    proposer = fields.Many2one("hr.employee", string="申请人")
    abstract = fields.Char(string="摘要")
    comment = fields.Char(string="备注")
    voucher_number = fields.Char(string="凭证号")

    
class AccountType(models.Model):
    _name = "account_type"
    _description = '记账类别类别'

    name = fields.Char(string="记账类别名称")
