from odoo import models, fields, api


class FsnSalesReturn(models.Model):
    _name = 'fsn_sales_return'
    _description = 'FSN销售退货'
    _rec_name = 'style_number'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    customer_id = fields.Many2one("fsn_customer", string="客户", required=True)
    employee_id = fields.Many2one('hr.employee', string='经手人', required=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    number = fields.Integer(string="件数")
    quality = fields.Selection([('合格', '合格'), ('次品', '次品')], string="产品质量", required=True)

        
