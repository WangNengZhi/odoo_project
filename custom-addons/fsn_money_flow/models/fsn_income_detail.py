from odoo import models, fields, api
# import requests

class JdyExpensesDetails(models.Model):
    _inherit = "jdy_expenses_details"


    fsn_income_detail_id = fields.Many2one("fsn_income_detail", string="收入明细")


    def set_fsn_income_detail(self):
        for record in self:
            
            fsn_income_detail_obj = self.env['fsn_income_detail'].sudo().search([("month", "=", record.month)])
            if not fsn_income_detail_obj:
                fsn_income_detail_obj = self.env['fsn_income_detail'].sudo().create({"month": record.month})
            record.fsn_income_detail_id = fsn_income_detail_obj.id

    @api.model
    def create(self, vals):
        res = super(JdyExpensesDetails,self).create(vals)

        res.set_fsn_income_detail()

        return res


class FsnAccountingDetail(models.Model):
    _inherit = "fsn_accounting_detail"

    
    fsn_income_detail_id = fields.Many2one("fsn_income_detail", string="收入明细")


    def set_fsn_income_detail(self):
        for record in self:
            *year_month, _ = str(record.ymd).split("-")
            year_month = "-".join(year_month)
            
            fsn_income_detail_obj = self.env['fsn_income_detail'].sudo().search([("month", "=", year_month)])
            if not fsn_income_detail_obj:
                fsn_income_detail_obj = self.env['fsn_income_detail'].sudo().create({"month": year_month})
            record.fsn_income_detail_id = fsn_income_detail_obj.id

    @api.model
    def create(self, vals):
        res = super(FsnAccountingDetail,self).create(vals)

        res.set_fsn_income_detail()

        return res



class FsnIncomeDetail(models.Model):
    _name = 'fsn_income_detail'
    _description = 'FSN收入明细'
    # _rec_name = 'jdy_subject_id'

    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")
                
    jdy_expenses_details_ids = fields.One2many("jdy_expenses_details", "fsn_income_detail_id", string="费用明细")
    sell_income = fields.Float(string="销售收入", compute="set_income_line", store=True)
    processing_income = fields.Float(string="加工收入", compute="set_income_line", store=True)
    government_subsidy = fields.Float(string="政府补助", compute="set_income_line", store=True)
    other_income = fields.Float(string="其他收入", compute="set_income_line", store=True)
    @api.depends("jdy_expenses_details_ids", "jdy_expenses_details_ids.jdy_subject_id", "jdy_expenses_details_ids.expense")
    def set_income_line(self):
        for record in self:
            record.sell_income = sum(record.jdy_expenses_details_ids.filtered(lambda x: x.jdy_subject_id.name == "网店销售收入").mapped("expense"))
            record.processing_income = sum(record.jdy_expenses_details_ids.filtered(lambda x: x.jdy_subject_id.name == "服装加工费收入").mapped("expense"))
            record.government_subsidy = sum(record.jdy_expenses_details_ids.filtered(lambda x: x.jdy_subject_id.name == "政府补助").mapped("expense"))
            record.other_income = sum(record.jdy_expenses_details_ids.filtered(lambda x: x.parent_jdy_subject_id.name == "营业外收入" and x.jdy_subject_id.name != "政府补助").mapped("expense"))


    total = fields.Float(string="合计", compute="set_total", store=True)
    @api.depends("sell_income", "processing_income", "government_subsidy", "other_income")
    def set_total(self):
        for record in self:
            
            record.total = (record.sell_income + record.processing_income + record.government_subsidy + record.other_income)


    fsn_accounting_detail_ids = fields.One2many("fsn_accounting_detail", "fsn_income_detail_id", string="会计明细")
    bank_income = fields.Float(string="银行收入", compute="set_bank_income", store=True)
    @api.depends("fsn_accounting_detail_ids", "fsn_accounting_detail_ids.type", "fsn_accounting_detail_ids.remark", "fsn_accounting_detail_ids.debit", "fsn_accounting_detail_ids.credit")
    def set_bank_income(self):
        for record in self:

            bank_filter_config_objs = self.env['bank_filter_config'].sudo().search([])

            filter_key_list = bank_filter_config_objs.mapped("filter_key")

            type_list = ["1001", "1002", "1012"]

            temp_bank_income = 0

            for i in record.fsn_accounting_detail_ids:
                if i.type in type_list:
                    for filter_key in filter_key_list:
                        if filter_key not in i.remark:
                            temp_bank_income += i.debit

            record.bank_income = temp_bank_income










