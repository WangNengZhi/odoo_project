from odoo import models, fields, api


class TemplateIncome(models.Model):
    _name = "template_income"
    _description = '模板收入'
    _rec_name = 'receipt_coding'
    _order = 'invoice_date desc'

    receipt_coding = fields.Char(string="收据编码", required=True)
    invoice_date = fields.Date(string="开票日期", required=True)
    purchaser = fields.Char(string="购买方", required=True)
    contact_way = fields.Char(string="联系方式", required=True)

    is_receive_money = fields.Selection([('已收款', '已收款'), ('未收款', '未收款')], string="是否收款", required=True)
    receive_money_date = fields.Date(string="收款日期")
    purchaser_username = fields.Char(string="对方账户名")
    purchaser_account_number = fields.Char(string="对方账号")
    note = fields.Text(string="备注")

    company_id = fields.Many2one('res.company')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_prices = fields.Monetary(string="总价", currency_field='company_currency_id', compute="set_total_prices", store=True)


    template_income_line_ids = fields.One2many("template_income_line", "template_income_id", string="模板收入明细")


    # 计算总价
    @api.depends('template_income_line_ids', 'template_income_line_ids.total_prices')
    def set_total_prices(self):
        for record in self:
            tem_total_prices = 0    # 临时总价
            
            for template_income_line_obj in record.template_income_line_ids:
                tem_total_prices = tem_total_prices + template_income_line_obj.total_prices

            record.total_prices = tem_total_prices


class TemplateIncomeLine(models.Model):
    _name = "template_income_line"
    _description = '模板收入明细'


    template_income_id = fields.Many2one("template_income", ondelete='cascade')
    template_type = fields.Char(string="模板规格类型")
    quantity = fields.Integer(string="数量")

    company_id = fields.Many2one('res.company')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    unit_price = fields.Monetary(string="单价", currency_field='company_currency_id')
    total_prices = fields.Monetary(string="总价", currency_field='company_currency_id', compute="set_total_prices", store=True)


    # 计算总价
    @api.depends('quantity', 'unit_price')
    def set_total_prices(self):
        for record in self:
            record.total_prices = record.quantity * record.unit_price





