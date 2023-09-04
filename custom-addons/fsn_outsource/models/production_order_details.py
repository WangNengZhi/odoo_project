from odoo import models, fields, api

class ProductionOrderDetails(models.Model):
    _name = 'production_order_details'
    _description = 'FSN外发生产订单明细表'
    # _rec_name = 'voucher_number'
    # _order = "date desc"

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}

    style = fields.Char(string="款式")
    outsource_plant_id = fields.Many2one("outsource_plant", string="生产厂商", required=True)

    voucher_quantity = fields.Integer(string="订单数量")
    solid_cutting_quantity = fields.Integer(string="实裁数量")

    contract_delivery_date = fields.Date(string="合同货期")
    sample_sealing_date = fields.Date(string="封样日期")
    picking_date = fields.Date(string="领料日期")
    online_date = fields.Date(string="上线日期")
    first_package_date = fields.Date(string="首包日期")
    day_production = fields.Date(string="日产量")
    quantity_remaining = fields.Integer(string="剩余数量")
    down_date = fields.Date(string="下线日期")
    after_road_repairs = fields.Integer(string="后道返修数")
    rate_repair = fields.Float(string='返修率')
    final_inbound_date = fields.Date(string="最终入库日期")
    responsible_person = fields.Many2one("hr.employee", string="负责人", required=True)
    note = fields.Text(string="备注")