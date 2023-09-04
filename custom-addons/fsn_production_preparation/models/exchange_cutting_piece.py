from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ExchangeCuttingPiece(models.Model):
    _name = 'exchange_cutting_piece'
    _description = '半成品换片单'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    parts = fields.Char(string="部位")
    size = fields.Many2one("fsn_size", string="尺码")
    number = fields.Integer(string="件数")
    exchange_why = fields.Text(string="换片原因")


    group_leader = fields.Many2one("hr.employee", string="组长", required=True)
    workshop_director = fields.Many2one("hr.employee", string="车间主任", required=True)
    inspector = fields.Many2one("hr.employee", string="验片员", required=True)
    cutting_bed_head = fields.Many2one("hr.employee", string="裁床主管", required=True)