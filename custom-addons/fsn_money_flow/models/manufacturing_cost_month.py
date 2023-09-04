from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta



class Manufacturingcostmonth(models.Model):
    _name = 'manufacturing_cost_month'
    _description = '制造费用成本月报'
    _order = "date desc"


    date = fields.Char(string="日期")
    cost_center = fields.Char(string="成本中心")
    type = fields.Char(string="制造费用类别")
    parent_type = fields.Char(string="父级类别")
    month_count = fields.Float(string="本月发生额")
    year_count = fields.Float(string="本年累计发生额")
    proportion = fields.Float(string="占营业成本比")
    month_update_money = fields.Float(string="环比增减")
    completion_rate = fields.Float(string="预算完成率")
    production = fields.Float(string="产量")
    unit_manufacturing_cost = fields.Float(string="单位制造费用")
    month = fields.Integer(string='日期月份')
    year = fields.Integer(string='日期年份')
    
    def get_manufacturing_cost_month(self, today):
        types = ['修理费', '折旧费', '办公费', '水电费', '燃气施工费', '房租', '交通费', '无形资产摊销费', '低值易耗品']
        month_first_day = datetime(today.year, today.month, 1)
        last_month = today - relativedelta(months=1)
        last_month_date = last_month.strftime("%Y-%m")
        today_str = today.strftime("%Y-%m")
        today_str_year = today.strftime("%Y")
        for type in types:
            month_alls = self.env['jdy_expenses_details'].sudo().search([('month', '=', today_str), ('parent_jdy_subject_id.name', '!=', '营业外收入'), ('parent_jdy_subject_id.name', '!=', '主营业务收入')])
            month_datas =  self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=', today_str), ('parent_jdy_subject_id.name', '=', '管理费用')])
            year_datas = self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=ilike', today_str_year + '%'),  ('parent_jdy_subject_id.name', '=', '管理费用')])
            last_month_datas = self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=', last_month_date), ('parent_jdy_subject_id.name', '=', '管理费用')])
            stocks = self.env['finished_inventory'].sudo().search([('write_date', '<=', today), ('write_date', '>', month_first_day)])
            result = sum(stock.stock for stock in stocks)
            print(result)
            month_alls_data = month_alls.mapped('expense')
            year_datas_num = year_datas.mapped('expense')
            if not last_month_datas or last_month_datas.expense == 0 and month_datas.expense !=0:
                month_update_money = 100
            elif last_month_datas.expense == 0 and month_datas.expense ==0:
                month_update_money = 0
            else: month_update_money = (month_datas.expense - last_month_datas.expense)/last_month_datas.expense
            year_count = sum(year_datas_num)
            if not month_datas or month_datas.expense == 0:
                proportion=0
            else:
                proportion = month_datas.expense/sum(month_alls_data)
            if result !=0:
               unit_manufacturing_cost = month_datas.expense/result
            else: unit_manufacturing_cost = 0
            data = {
                         'date' :today_str,
                         'cost_center':'生产部门',
                         'type' :type,
                         'parent_type':month_datas.parent_jdy_subject_id.name,
                         'month_count' :month_datas.expense,
                         'year_count' :year_count,
                         'proportion' :proportion,
                         'month_update_money' :month_update_money,
                         'completion_rate' :0,
                         'production' :result,
                         'unit_manufacturing_cost' :unit_manufacturing_cost,
                         'month' :today.month,
                         'year' :today.year               
            }       
            self.env['manufacturing_cost_month'].sudo().search([('type', '=', type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
    def get_month_data(self, today):
        types = ['修理费', '折旧费', '办公费', '水电费', '燃气施工费', '房租', '交通费', '无形资产摊销费', '低值易耗品']
        month_first_day = datetime(today.year, today.month, 1)
        last_month = today - relativedelta(months=1)
        last_month_date = last_month.strftime("%Y-%m")
        today_str = today.strftime("%Y-%m")
        today_str_year = today.strftime("%Y")
        for type in types:
            month_alls = self.env['jdy_expenses_details'].sudo().search([('month', '=', today_str), ('parent_jdy_subject_id.name', '!=', '营业外收入'), ('parent_jdy_subject_id.name', '!=', '主营业务收入')])
            month_datas =  self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=', today_str), ('parent_jdy_subject_id.name', '=', '管理费用')])
            year_datas = self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=ilike', today_str_year + '%'),  ('parent_jdy_subject_id.name', '=', '管理费用')])
            last_month_datas = self.env['jdy_expenses_details'].sudo().search([('jdy_subject_id.name', '=', type), ('month', '=', today_str), ('parent_jdy_subject_id.name', '=', '管理费用')])
            stocks = self.env['finished_inventory'].sudo().search([('write_date', '<=', today), ('write_date', '>', month_first_day)])
            result = sum(stock.stock for stock in stocks)
            month_alls_data = month_alls.mapped('expense')
            year_datas_num = year_datas.mapped('expense')
            if not last_month_datas or last_month_datas.expense == 0:
                month_update_money = 100
            else: month_update_money = (month_datas.expense - last_month_datas.expense)/last_month_datas.expense
            year_count = sum(year_datas_num)
            if not month_datas or month_datas.expense == 0:
                proportion=0
            else:
                proportion = month_datas.expense/sum(month_alls_data)
            if result !=0:
               unit_manufacturing_cost = month_datas.expense/result
            else: unit_manufacturing_cost = 0
            data = {
                         'date' :today_str,
                         'cost_center':'生产部门',
                         'type' :type,
                         'parent_type':month_datas.parent_jdy_subject_id.name,
                         'month_count' :0,
                         'year_count' :0,
                         'proportion' :0,
                         'month_update_money' :0,
                         'completion_rate' :0,
                         'production' :0,
                         'unit_manufacturing_cost' :0,
                         'month' :today.month,
                         'year' :today.year               
            }       
            #self.env['fabric_ingredients_account_month'].sudo().search([('type', '=', month_date_type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
            self.create(data)









   