from odoo import models, fields, api


class B2bOrder(models.Model):
    _name = 'b2b_order'
    _description = 'B2B订单'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    customer_name = fields.Char(string="客户名称", required=True)
    managers = fields.Char(string="经手人", required=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号')
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", compute="_set_fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", store=True)
    # 设置颜色
    @api.depends('style_number')
    def _set_fsn_color(self):
        for record in self:
            record.fsn_color = record.style_number.fsn_color.id


    number = fields.Integer(string="件数")
    unit_price = fields.Float(string="单价")
    total_amount = fields.Float(string="总金额", compute="_set_total_amount", store=True)
    actual_deliveries = fields.Float(string="实际交货数")
    actual_payment_amount = fields.Float(string="实际付款金额")

    # 计算总金额
    @api.depends('number', 'unit_price')
    def _set_total_amount(self):
        for record in self:
            record.total_amount = record.number * record.unit_price

    state = fields.Selection([('已付款', '已付款'), ('未付款', '未付款'), ('付款未完成', '付款未完成')], string="状态", required=True)