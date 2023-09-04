from odoo.exceptions import ValidationError
from odoo import models, fields, api



class LoseRecord(models.Model):
    _name = 'lose_record'
    _description = '丢失记录'
    _rec_name = 'date'
    _order = "date desc"

    date = fields.Date(string='日期', required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer(string='件数')
    pro_value = fields.Float(string='产值', compute="set_pro_value", store=True)
    @api.depends('order_number', 'number')
    def set_pro_value(self):
        for record in self:
            record.pro_value = float(record.order_number.order_price) * record.number
            

    principal = fields.Many2many("hr.employee", string="负责人")

