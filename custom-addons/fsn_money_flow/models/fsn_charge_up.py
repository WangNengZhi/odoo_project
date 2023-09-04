from odoo.exceptions import ValidationError
from odoo import models, fields, api

import datetime
import calendar

class FsnChargeUp(models.Model):
    _name = 'fsn_charge_up'
    _description = 'fsn_记账'
    _rec_name = 'month'
    _order = 'month desc'
    
    # money_flow_id = fields.Many2one("money_flow", string="资金流向")
    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

    bank_id = fields.Many2one("res.bank", string="银行", required=True)
    balance = fields.Float(string="余额")
    income = fields.Float(string="收入")
    disburse = fields.Float(string="支出")
    fsn_charge_up_id = fields.Many2one("fsn_charge_up", string="上一月记录", compute="set_fsn_charge_up_id", store=True)
    @api.depends("month", "bank_id")
    def set_fsn_charge_up_id(self):
        for record in self:
            if record.month and record.bank_id:
                year, month = map(int, record.month.split("-"))
                previous_year_month = self.get_last_year_month(year, month)

                previous_obj = self.search([("month", "=", previous_year_month), ("bank_id", "=", record.bank_id.id)])
                if previous_obj:
                    record.fsn_charge_up_id = previous_obj.id
          
                else:
                    record.fsn_charge_up_id = False
            else:
                record.fsn_charge_up_id = False


    audit_value = fields.Float(string="审核值", compute="set_audit_value", store=True)
    @api.depends("fsn_charge_up_id", "fsn_charge_up_id.balance", "fsn_charge_up_id.income", "fsn_charge_up_id.disburse", "balance")
    def set_audit_value(self):
        for record in self:
            if record.fsn_charge_up_id:
                # 上个月的余额 + 上个月的收入 - 上个月的支出 - 当前月的余额
                record.audit_value = (record.fsn_charge_up_id.balance + record.fsn_charge_up_id.income - record.fsn_charge_up_id.disburse - record.balance)
            else:
                record.audit_value = 0

    @staticmethod
    def get_last_year_month(year, month):
        ''' 获取指定月份之前的上一个月份'''

        month -= 1
        if month == 0:
            year, month = year - 1, 12
        
        return f'{year}-{month:02}'
    
    @staticmethod
    def set_begin_and_end(year, month):
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end


    jdy_income = fields.Float(string="收入", compute="set_jdy_info", store=True)
    jdy_disburse = fields.Float(string="支出", compute="set_jdy_info", store=True)
    @api.depends("month", "bank_id")
    def set_jdy_info(self):
        for record in self:
            
            if record.month and record.bank_id:
                
                year, month = map(int, record.month.split("-"))
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                fsn_accounting_detail_objs = self.env['fsn_accounting_detail'].sudo().search([
                    ("jdy_subject_id.name", "=", record.bank_id.name),
                    ("ymd", ">=", this_month_start),
                    ("ymd", "<=", this_month_end)
                ])

                record.jdy_income = sum(fsn_accounting_detail_objs.mapped("debit"))
                record.jdy_disburse = sum(fsn_accounting_detail_objs.mapped("credit"))
            else:
                record.jdy_income = 0
                record.jdy_disburse = 0