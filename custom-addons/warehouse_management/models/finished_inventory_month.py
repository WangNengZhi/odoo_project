from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date


class Finishedinventorymonth(models.Model):
    '''成品仓月库存信息'''
    _name = "finished_inventory_month"
    _description = '成品月仓库存'
    _order = "write_date desc"
    
    
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=False)
    date = fields.Date(string="更新日期")
    number = fields.Integer(string="总库存件数", store=True)
    put_number = fields.Integer(string="月总入库件数", store=True)
    normal_number = fields.Integer(string='正常库存件数')
    defective_number = fields.Integer(string='报次库存件数')
    no_accomplish_number = fields.Integer(string='半成品库存件数')
    cutting_number = fields.Integer(string='裁片库存件数')
    no_normal_number = fields.Integer(string='非正常库存件数')
    size = fields.Many2one("fsn_size", string="尺码", required=False)
    style_number = fields.Many2one('ib.detail', string='款号', required=False)
    fsn_color = fields.Many2one("fsn_color", string="颜色", store=True)
    
   

    def get_month_date_finished_inventory(self, today):
        first_day = datetime(today.year, today.month, 1)
        month_dates = self.env['finished_inventory'].sudo().search([('write_date', '<=', today), ('write_date', '>', first_day)])
        
        for month_date in month_dates:
           
            data = {
                'order_number':month_date.order_number.id,
                'date': today,
                'number': month_date.number,
                'put_number': month_date.put_number,
                'normal_number': month_date.normal_number,
                'defective_number': month_date.defective_number,
                'no_accomplish_number': month_date.no_accomplish_number,
                'cutting_number': month_date.cutting_number,
                'no_normal_number': month_date.no_normal_number,
                'size': month_date.size.id,
                'style_number': month_date.style_number.id,
                'fsn_color': month_date.fsn_color.id,
                
            }
            
            
            self.sudo().create(data)
            # print(self.put_number_month)
        