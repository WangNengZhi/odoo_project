
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EcProductData(models.Model):
    _name = 'ec_product_data'
    _description = '电商货品数据'
    _rec_name = 'item_style_number'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)
    item_style_number = fields.Char(string="货品款号")
    style_picture = fields.Image(string='款式图片')
    live_type = fields.Selection([
        ('主讲款','主讲款'),
        ('链接款','链接款'),
        ], string='直播类型', required=True)
    exposure_click_rate = fields.Float(string="曝光点击率")
    click_conversion_rate = fields.Float(string="点击转化率")
    click_rate = fields.Float(string="点击率")
    order_quantity = fields.Float(string="订单数")
    refund_quantity = fields.Float(string="退款数")
    return_goods_quantity = fields.Float(string="退货数")
    GMV = fields.Float(string="GMV")

    type = fields.Selection([
        ('福利款','福利款'),
        ('引流款','引流款'),
        ('正价款','正价款'),
        ], string='类型', required=True)
    cost = fields.Float(string="成本")
    price = fields.Float(string="价格")
    difference = fields.Float(string="差价", compute="set_difference", store=True)

    @api.depends('cost', 'price')
    def set_difference(self):
        for record in self:
            record.difference = record.price - record.cost

    price_addition_cost = fields.Float(string="价格/成本", compute="set_price_addition_cost", store=True)

    @api.depends('cost', 'price')
    def set_price_addition_cost(self):
        for record in self:
            if record.cost:
                record.price_addition_cost = record.price / record.cost