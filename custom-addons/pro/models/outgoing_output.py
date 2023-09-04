from odoo.exceptions import ValidationError
from odoo import models, fields, api


class OutgoingOutput(models.Model):
    _name = "outgoing_output"
    _description = '外发产值'
    _rec_name = "date"
    _order = "date desc"


    date = fields.Date('日期', required=True)
    outsource_plant_id = fields.Many2one("outsource_plant", string="外发工厂", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer('件数')

    pro_value = fields.Float('产值', compute="set_pro_value", store=True)
    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)



    @api.constrains('date', "outsource_plant_id", "order_number", "style_number", "product_size")
    def _check_unique(self):
        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ("outsource_plant_id", "=", self.outsource_plant_id.id),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("product_size", "=", self.product_size.id),
        ])
        if len(demo) > 1:
            raise ValidationError(f"{self.date},{self.outsource_plant_id.name},{self.order_number.order_number},{self.style_number.style_number},{self.product_size.name},记录重复！")