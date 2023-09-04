from odoo import models, fields, api
from odoo.exceptions import ValidationError
from decimal import *
from datetime import datetime, timedelta, date


class Sparematerialinventorymonth(models.Model):
    _name = 'spare_material_inventory_month'
    _description = '备用物料仓月库存'
    _order = "write_date desc"


    

    date = fields.Date(string="更新日期")
    material_coding = fields.Char( string="物料编号")
    material_name = fields.Char(string="物料名称", store=True)
    order_id = fields.Char( string='订单号')
    style_number = fields.Char(string="款号")
    supplier = fields.Char(string="供应商", store=True)
    client_id = fields.Char(string="客户", store=True)
    specification = fields.Char(string="规格", store=True)
    color = fields.Char(string="颜色", store=True)
    amount = fields.Integer(string="数量")
    money_sum = fields.Float(string="总价")
    
    
   

    def get_spare_material_inventory_monthh(self,today):
        first_day = datetime(today.year, today.month, 1)
        month_dates = self.env['spare_material_inventory'].sudo().search([('write_date', '<=', today), ('write_date', '>', first_day)])
        for month_date in month_dates:
            data = {
                'date': today,
                'material_coding':month_date.material_coding.material_code.name,
                'material_name': month_date.material_name,
                'order_id': month_date.order_id.order_number,
                'style_number': month_date.style_number.style_number,
                'supplier': month_date.supplier,
                'client_id': month_date.client_id,
                'specification': month_date.specification,
                'color': month_date.color,
                'amount': month_date.amount,
                'money_sum': month_date.money_sum,
                
            }
            #print(data)
            self.sudo().create(data)
        
        


    
