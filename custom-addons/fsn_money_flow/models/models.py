# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api
import calendar, datetime


class FsnAccountingDetail(models.Model):
    _inherit = "fsn_accounting_detail"

    
    money_flow_id = fields.Many2one("money_flow", string="资金流向")

    def set_money_flow_id(self):
        for record in self:
            *year_month, _ = str(record.ymd).split("-")
            year_month = "-".join(year_month)

            money_flow_obj = self.env['money_flow'].sudo().search([("month", "=", year_month)])
            if not money_flow_obj:
                money_flow_obj = self.env['money_flow'].sudo().create({"month": year_month})
            record.money_flow_id = money_flow_obj.id

    @api.model
    def create(self, vals):
        res = super(FsnAccountingDetail,self).create(vals)

        res.set_money_flow_id()

        return res



class MoneyFlow(models.Model):
    _name = 'money_flow'
    _description = '资金流向'

    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

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
    standby_application = fields.Float(string="备用金")
    total_cost = fields.Float(string="合计", compute="_set_total_cost", store=True)

    @api.constrains('month')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([('month', '=', self.month)])
        if len(demo) > 1:
            raise ValidationError(f"{self.month}的记录已经存在了！不可重复创建。")


    # 计算合计费用
    @api.depends("transport_cost", "office_cost", "production_cost", "wages_cost", "social_security_cost", "taxation_cost", "refuelingr_cost", "staff_meals_cost", "plant_rent_cost", "fixed_assets_cost", "other_cost", "intangible_assets")
    def _set_total_cost(self):

        for obj in self:

            obj.total_cost = obj.transport_cost + obj.office_cost + obj.production_cost + obj.wages_cost + obj.social_security_cost + obj.taxation_cost + obj.refuelingr_cost + obj.staff_meals_cost + obj.plant_rent_cost + obj.fixed_assets_cost + obj.other_cost + obj.intangible_assets

    fsn_accounting_detail_ids = fields.One2many("fsn_accounting_detail", "money_flow_id", string="会计明细")
    bank_income = fields.Float(string="银行收入", compute="set_fsn_accounting_detail_info", store=True)
    bank_disbursement = fields.Float(string="银行支出", compute="set_fsn_accounting_detail_info", store=True)
    @api.depends("fsn_accounting_detail_ids", "fsn_accounting_detail_ids.type", "fsn_accounting_detail_ids.remark", "fsn_accounting_detail_ids.debit", "fsn_accounting_detail_ids.credit")
    def set_fsn_accounting_detail_info(self):
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

            temp_bank_disbursement = 0

            for j in record.fsn_accounting_detail_ids:
                if j.type in type_list:
                    for filter_key in filter_key_list:
                        if filter_key not in j.remark:
                            temp_bank_disbursement += j.credit

            record.bank_disbursement = temp_bank_disbursement

            # record.bank_income = sum(record.fsn_accounting_detail_ids.filtered(lambda x: x.type == "1002" and x.remark != "划款").mapped("debit"))

            # record.bank_disbursement = sum(record.fsn_accounting_detail_ids.filtered(lambda x: x.type == "1002" and x.remark != "划款").mapped("credit"))


    # 计算月的第一天和最后一天
    def compute_start_and_end(self, record):

        if record.month:
            # 获取当前月份的第一天和最后一天
            date_list = record.month.split("-")
            date_year = int(date_list[0])
            date_month = int(date_list[1])
            last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
            start = datetime.date(date_year, date_month, 1)
            end = datetime.date(date_year, date_month, last_day)

            return {"start": start, "end": end}


    # 设置无形资产
    def set_intangible_assets(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_intangible').id)    # 运输费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "intangible_assets": tem_data
            })


    # 设置运输费
    def set_transport_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_freight').id)    # 运输费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "transport_cost": tem_data
            })


    # 设置办公费
    def set_office_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_office').id)    # 办公费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "office_cost": tem_data
            })


    # 设置生产成本费用
    def set_production_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_production_costs').id)    # 办公费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "production_cost": tem_data
            })


    # 设置工资费用
    def set_wages_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_wages').id)    # 工资费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "wages_cost": tem_data
            })


    # 公积金及社保
    def set_social_security_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_social_security').id)    # 公积金及社保
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "social_security_cost": tem_data
            })


    # 税费
    def set_taxation_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_taxation').id)    # 税费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "taxation_cost": tem_data
            })


    # 加油费
    def set_refuelingr_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_refueling_fee').id)    # 加油费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "refuelingr_cost": tem_data
            })


    # 员工餐费
    def set_staff_meals_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_meals').id)    # 员工餐费
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "staff_meals_cost": tem_data
            })


    # 厂房租金
    def set_plant_rent_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_plant_rent').id)    # 厂房租金
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "plant_rent_cost": tem_data
            })


    # 固定资产
    def set_fixed_assets_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_fixed_assets').id)    # 固定资产
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "fixed_assets_cost": tem_data
            })


    # 其他资产
    def set_other_cost(self):

        for record in self:
            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end(record)

            hr_expense_objs = self.env["hr.expense"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("cost_type_id", "=", self.env.ref('fsn_expenses.cost_type_other_expenses').id)    # 其他资产
            ])
            tem_data = 0
            for hr_expense_obj in hr_expense_objs:

                tem_data = tem_data + hr_expense_obj.total_amount

            record.write({
                "other_cost": tem_data
            })
