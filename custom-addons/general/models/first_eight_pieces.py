from odoo import models, fields, api


class FirstEightPieces(models.Model):
    _name = 'first_eight_pieces'
    _description = '首八件'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    fsn_customer_id = fields.Many2one("fsn_customer", string="客户", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    picture = fields.Image(string='图片', required=True)
    report = fields.Image(string='报告', required=True)
    is_workshop = fields.Boolean(string="车间")
    is_posterior_channel = fields.Boolean(string="后道")
    is_quality_control_approval = fields.Boolean(string="品控主管审批")
    hand_in_quantity = fields.Integer(string="上交件数")
    qualified_quantity = fields.Integer(string="合格件数")
    pass_rate = fields.Float(string="合格率", compute="set_pass_rate", store=True)
    @api.depends('hand_in_quantity', 'qualified_quantity')
    def set_pass_rate(self):
        for record in self:
            if record.hand_in_quantity:
                record.pass_rate = record.qualified_quantity / record.hand_in_quantity
            else:
                record.pass_rate = 0
    is_customer_approval = fields.Boolean(string="客户审批")

