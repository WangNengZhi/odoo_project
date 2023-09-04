from odoo.exceptions import ValidationError
from odoo import models, fields, api, tools


class FsnSalesOrder(models.Model):
    _inherit = "fsn_sales_order"

    cost_sales_id = fields.Many2one("cost_sales", string="销售成本", compute="set_cost_sales_id", store=True)

    @api.depends('fsn_delivery_date')
    def set_cost_sales_id(self):
        for record in self:
            if record.fsn_delivery_date:

                *year_month_list, _ = str(record.fsn_delivery_date).split("-")
                year_month = '-'.join(year_month_list)
                cost_sales_obj = self.env['cost_sales'].sudo().search([("month", "=", year_month)])
                if not cost_sales_obj:
                    cost_sales_obj = self.env['cost_sales'].sudo().create({"month": year_month})
                
                temp_cost_sales_id = False
                if record.cost_sales_id and record.cost_sales_id.id != cost_sales_obj.id:
                    temp_cost_sales_id = record.cost_sales_id

                record.cost_sales_id = cost_sales_obj.id

                if temp_cost_sales_id:
                    temp_cost_sales_id.set_fsn_sales_order_info()


class CostSales(models.Model):
    _name = 'cost_sales'
    _description = '销售成本'
    _rec_name = 'month'
    _order = 'month desc'
    

    fsn_sales_order_ids = fields.One2many("fsn_sales_order", "cost_sales_id", string="销售订单")
    month = fields.Char(string="月份")
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

    order_amount = fields.Float(string="已签订单金额", compute="set_fsn_sales_order_info", store=True)
    completed_amount = fields.Float(string="已完成金额", compute="set_fsn_sales_order_info", store=True)
    amount_paid = fields.Float(string="已付款金额", compute="set_fsn_sales_order_info", store=True)
    @api.depends("fsn_sales_order_ids", "fsn_sales_order_ids.state", "fsn_sales_order_ids.fsn_payment_state", "fsn_sales_order_ids.after_tax_total")
    def set_fsn_sales_order_info(self):
        for record in self:
            record.order_amount = sum(record.fsn_sales_order_ids.filtered(lambda x: x.state != "草稿").mapped("after_tax_total"))
            record.completed_amount = sum(record.fsn_sales_order_ids.filtered(lambda x: x.state == "已完成").mapped("after_tax_total"))
            record.amount_paid = sum(record.fsn_sales_order_ids.filtered(lambda x: x.state != "草稿" and x.fsn_payment_state == "已付款").mapped("after_tax_total"))

