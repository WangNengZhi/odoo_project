from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LossAccountingStatement(models.Model):
    _name = 'loss_accounting_statement'
    _description = '损失核算表'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")
    department_id = fields.Many2one("hr.department", string="部门", required=True)

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}

    name_or_style = fields.Char(string="品名/款式", required=True)
    unit_working_hours = fields.Float(string="单件工时")
    accounting_numbersa = fields.Integer(string="核算数量（件）")
    unit_wages = fields.Float(string="单件工价", digits=(16, 3))
    fabric_price = fields.Float(string="面料价格/件", digits=(16, 3))
    material_price = fields.Float(string="辅料价格/件", digits=(16, 3))
    total_price = fields.Float(string="总价", digits=(16, 3), compute="set_total_price", store=True)
    @api.depends('accounting_numbersa', 'unit_wages', 'fabric_price', 'material_price')
    def set_total_price(self):
        for record in self:
            record.total_price = record.accounting_numbersa * (record.unit_wages + record.fabric_price + record.material_price)

    responsibility_people = fields.Many2one("hr.employee", string="责任人")
    responsibility_peoples = fields.Many2many("hr.employee", string="责任人")

    note = fields.Text(string="备注")
    show_how = fields.Text(string="情况说明")



    # 审批通过
    def through(self):
        for record in self:
            if record.state == "待审批":
                record.state = "已审批"
    # 回退
    def fallback(self):
        for record in self:
            if record.state == "已审批":
                record.state = "待审批"