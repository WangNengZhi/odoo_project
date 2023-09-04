from odoo.exceptions import ValidationError
from odoo import models, fields, api


class BankFilterConfig(models.Model):
    _name = 'bank_filter_config'
    _description = '银行过滤配置'
    _rec_name = 'filter_key'

    filter_key = fields.Char(string="关键字", required=True)



class FsnIncomeDetailType(models.Model):
    _name = 'fsn_income_detail_type'
    _description = 'FSN收入明细类别设置'


    name = fields.Char(string="类别名称", required=True)
    jdy_subject_id = fields.Many2many("jdy_subject", string="科目")
