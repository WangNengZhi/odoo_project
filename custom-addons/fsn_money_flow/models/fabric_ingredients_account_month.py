from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta



class Fabricingredientsaccountmonth(models.Model):
    _name = 'fabric_ingredients_account_month'
    _description = '原材料采购成本月报'
    _order = "date desc"


    date = fields.Date(string="日期")
    type = fields.Selection([('面料', '面料'),('辅料', '辅料'),('特殊工艺', '特殊工艺'),], string="采购原材料类别")
    use_type = fields.Selection([('用料', '用料'), ('储备用料', '储备用料')], string="物料类型")
    month_count_number = fields.Float(string="本月采购数量")
    month_unit_price = fields.Float(string="本月平均采购单价")
    month_count_money = fields.Float(string="本月采购金额")
    year_count_number = fields.Float(string="今年采购数量")
    year_unit_price = fields.Float(string="今年平均采购单价")
    year_count_money = fields.Float(string="今年采购金额")
    month_update_count = fields.Float(string="环比上月采购量增减")
    month_update_money = fields.Float(string="环比上月采购单价增减")
    manager = fields.Many2one('hr.employee', string="负责人")
    month = fields.Integer(string='日期月份')
    year = fields.Integer(string='日期年份')
    def update_month_data(self, today):
        first_day_month = datetime(today.year, today.month, 1)
        first_day_year = datetime(today.year, 1, 1)
        last_month_firstday = first_day_month - relativedelta(months=1)
        last_month_lostday = first_day_month - timedelta(days=1)
        month_dates = self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_month)])
        month_date_types = ['面料', '辅料', '特殊工艺']
        for month_date_type in month_date_types:
            month_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_month), ('type', '=', month_date_type)])
            year_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_year), ('type', '=', month_date_type)])
            last_month_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', last_month_lostday), ('date', '>=', last_month_firstday), ('type', '=', month_date_type)])
            if month_dates:
                data = {
                     'date' :today,
                     'type' :month_date_type,
                     'month_count_number' :sum(month_date.amount for month_date in month_dates),
                     'month_unit_price' :sum(month_date.money_sum for month_date in month_dates)/sum(month_date.amount for month_date in month_dates),
                     'month_count_money' :sum(month_date.money_sum for month_date in month_dates),
                     'year_count_number' :sum(year_date.amount for year_date in year_dates),
                     'year_unit_price' :sum(year_date.money_sum for year_date in year_dates)/sum(year_date.amount for year_date in year_dates),
                     'year_count_money' :sum(year_date.money_sum for year_date in year_dates),
                     'month_update_count' :(sum(month_date.amount for month_date in month_dates) - sum(last_month_date.amount for last_month_date in last_month_dates)) / sum(last_month_date.amount for last_month_date in last_month_dates),
                     'month_update_money' :(sum(month_date.money_sum for month_date in month_dates)/sum(month_date.amount for month_date in month_dates) - sum(last_month_date.money_sum for last_month_date in last_month_dates)/sum(last_month_date.amount for last_month_date in last_month_dates)) / (sum(last_month_date.money_sum for last_month_date in last_month_dates)/sum(last_month_date.amount for last_month_date in last_month_dates)),
                     'month' :today.month,
                     'year' :today.year               
                }      
                self.env['fabric_ingredients_account_month'].sudo().search([('type', '=', month_date_type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
        
    def get_month_data(self, today):
        first_day_month = datetime(today.year, today.month, 1)
        first_day_year = datetime(today.year, 1, 1)
        last_month_firstday = first_day_month - relativedelta(months=1)
        last_month_lostday = first_day_month - timedelta(days=1)
        month_dates = self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_month)])
        month_date_types = ['面料', '辅料', '特殊工艺']
        for month_date_type in month_date_types:
            month_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_month), ('type', '=', month_date_type)])
            year_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', today), ('date', '>=', first_day_year), ('type', '=', month_date_type)])
            last_month_dates =  self.env['fabric_ingredients_procurement'].sudo().search([('date', '<=', last_month_lostday), ('date', '>=', last_month_firstday), ('type', '=', month_date_type)])
            data = {
                     'date' :today,
                     'type' :month_date_type,
                     'month_count_number' :0,
                     'month_unit_price' :0,
                     'month_count_money' :0,
                     'year_count_number' :0,
                     'year_unit_price' :0,
                     'year_count_money' :0,
                     'month_update_count' :0,
                     'month_update_money' :0,
                     'month' :today.month,
                     'year' :today.year               
            }         
            self.create(data)









   