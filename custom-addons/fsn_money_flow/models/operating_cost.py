from odoo.exceptions import ValidationError
from odoo import models, fields, api

import calendar, datetime


class OperatingCost(models.Model):
    _name = 'operating_cost'
    _description = '运营成本'
    _rec_name = 'month'
    _order = 'month desc'
    
    month = fields.Char(string="月份")

    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

    raw_material_cost = fields.Float(string="原材料成本")
    def calculation_raw_material_cost(self, start_date, end_date):
        ''' 计算面辅料成本'''
        fabric_ingredients_summary_objs = self.env['fabric_ingredients_summary'].sudo().search([
            ("date", ">=", start_date),
            ("date", "<=", end_date),
            ("state", "in", ['已退还', '已采购']),
        ])
        self.raw_material_cost = sum(fabric_ingredients_summary_objs.mapped("after_tax_amount"))

    labor_cost = fields.Float(string="人力成本")
    def calculation_labor_cost(self, year_month):
        ''' 计算人力成本'''
        payroll3_objs = self.env['payroll3'].sudo().search([("month", "=", year_month)])
        self.labor_cost = sum(payroll3_objs.mapped("should_wage1"))

    outgoing_cost = fields.Float(string="外发成本")
    def calculation_outgoing_cost(self, start_date, end_date):
        ''' 计算外发成本'''
        outsource_order_objs = self.env['outsource_order'].sudo().search([
            ("customer_delivery_time", ">=", start_date),
            ("customer_delivery_time", "<=", end_date),
            ("payment_state", "=", "已付款")
        ])
        self.outgoing_cost = sum(outsource_order_objs.mapped("customer_payment_amount"))

    equipment_cost = fields.Float(string="设备成本")
    def calculation_equipment_cost(self, start_date, end_date):
        ''' 计算设备成本'''
        maintain_procurement_objs = self.env['maintain_procurement'].sudo().search([("state", "=", "已采购"), ("date", ">=", start_date), ("date", "<=", end_date)])
        self.equipment_cost = sum(maintain_procurement_objs.mapped("after_tax_amount"))

    lease_cost = fields.Float(string="租赁成本")
    def calculation_lease_cost(self, start_date, end_date):
        ''' 计算租赁成本'''
        equipment_leasing_objs = self.env['equipment_leasing'].sudo().search([("date", ">=", start_date), ("date", "<=", end_date), ("approve_state", "=", "已审批")])
        self.lease_cost = sum(equipment_leasing_objs.mapped("money_sum"))

    transportation_cost = fields.Float(string="运输成本")
    def calculation_transportation_cost(self, start_date, end_date):
        ''' 计算运输成本'''
        team_cost_objs = self.env['team_cost'].sudo().search([("date", ">=", start_date), ("date", "<=", end_date), ("state", "=", "确认")])
        car_rental_cost_objs = self.env['car_rental_cost'].sudo().search([("date", ">=", start_date), ("date", "<=", end_date), ("state", "=", "确认")])
        self.transportation_cost = sum(team_cost_objs.mapped("cost")) + sum(car_rental_cost_objs.mapped("costs"))

    tax_cost = fields.Float(string="税费成本")
    other_cost = fields.Float(string="其他杂项费用成本")
    def calculation_other_cost(self, start_date, end_date):
        ''' 计算其他杂项费用成本'''
        office_procurement_enter_objs = self.env['office_procurement_enter'].sudo().search([("date", ">=", start_date), ("date", "<=", end_date), ("state", "=", "已采购")])
        self.other_cost = sum(office_procurement_enter_objs.mapped("money_sum"))


    @staticmethod
    def compute_start_and_end(year_month):
        ''' 获取指定日期月份的第一天和最后一天'''
        year, month = map(int, year_month.split("-"))
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, last_day)

        return start_date, end_date


    def refresh_cost(self, today):
        ''' 刷新成本'''

        year, month, _ = str(today).split("-")
        year_month = f"{year}-{month}"

        operating_cost_obj = self.env['operating_cost'].sudo().search([("month", "=", year_month)])
        if not operating_cost_obj:
            operating_cost_obj = self.env["operating_cost"].sudo().create({"month": year_month})

        operating_cost_objs = self.env['operating_cost'].sudo().search([])

        for operating_cost_obj in operating_cost_objs:

            start_date, end_date = self.compute_start_and_end(operating_cost_obj.month)

            operating_cost_obj.calculation_raw_material_cost(start_date, end_date)

            operating_cost_obj.calculation_labor_cost(operating_cost_obj.month)

            operating_cost_obj.calculation_outgoing_cost(start_date, end_date)

            operating_cost_obj.calculation_equipment_cost(start_date, end_date)

            operating_cost_obj.calculation_lease_cost(start_date, end_date)

            operating_cost_obj.calculation_transportation_cost(start_date, end_date)

            operating_cost_obj.calculation_other_cost(start_date, end_date)

        



