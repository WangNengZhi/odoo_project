from odoo.exceptions import ValidationError
from odoo import models, fields, api



class EnterWarehouse(models.Model):
    _name = 'enter_warehouse'
    _description = '入库产值'
    _order = "date desc"


    finished_product_ware_line_id = fields.Many2one("finished_product_ware_line")

    date = fields.Date(string="日期", related='finished_product_ware_line_id.date', store=True)
    type = fields.Selection([('入库', '入库'), ('出库', '出库')], string="类型", related='finished_product_ware_line_id.type', store=True)
    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", related='finished_product_ware_line_id.order_number', store=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related='finished_product_ware_line_id.order_number.processing_type', store=True)


    style_number = fields.Many2one('ib.detail', string='款号', related='finished_product_ware_line_id.style_number', store=True)
    number = fields.Integer(string='件数', related='finished_product_ware_line_id.number', store=True)

    enter_warehouse_value = fields.Float(string="入库产值", compute="set_enter_warehouse_value", store=True)
    @api.depends('order_number', 'order_number.order_price', 'number')
    def set_enter_warehouse_value(self):
        for record in self:
            if record.order_number and record.number:
                record.enter_warehouse_value = float(record.order_number.order_price) * record.number
            else:
                record.enter_warehouse_value = 0

    is_inferior = fields.Selection([('合格', '合格'),('次品', '次品')],string="合格/次品", related='finished_product_ware_line_id.quality', store=True)


    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.enter_warehouse_value = obj.number * float(obj.order_number.order_price)
