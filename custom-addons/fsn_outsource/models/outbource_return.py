from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OutsourceOrder(models.Model):
    """ 继承外发订单"""
    _inherit = 'outsource_order'



    outbource_return_ids = fields.One2many("outbource_return", "outsource_order_id", string="外发退货")
    sales_return_number = fields.Integer(string="退货数量", compute="set_sales_return_number", store=True)

    # 设置颜色
    @api.depends('outbource_return_ids', 'outbource_return_ids.number')
    def set_sales_return_number(self):
        for record in self:
            record.sales_return_number = sum(record.outbource_return_ids.mapped("number"))

    @api.onchange('outbource_return_ids', 'outbource_return_ids.repair_total_price', 'outbource_return_ids.repair_type')
    def set_deduct_money(self):
        for record in self:
            record.deduct_money = sum(record.outbource_return_ids.filtered(lambda x: x.repair_type == "工厂返修").mapped("repair_total_price"))


class OutbourceReturn(models.Model):
    _name = 'outbource_return'
    _description = '外发退货'
    _order = "date desc"

    outsource_order_id = fields.Many2one("outsource_order", string="外发订单")

    date = fields.Date(string="日期", required=True)

    outsource_order_line_ids = fields.Many2one("outsource_order_line", string="订单明细", required=True)
    outsource_plant_id = fields.Many2one("outsource_plant", string="加工厂", related="outsource_order_id.outsource_plant_id", store=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="outsource_order_id.order_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="outsource_order_line_ids.style_number", store=True)


    fsn_color = fields.Many2one("fsn_color", string="颜色", related="outsource_order_line_ids.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", related="outsource_order_line_ids.size", store=True)




    number = fields.Integer(string="件数")



    problem = fields.Char(string="问题")
    quality_inspection_id = fields.Many2one('hr.employee', string='总检', required=True)

    repair_type = fields.Selection([
        ('工厂返修', '工厂返修'),
        ('外发返修', '外发返修'),
        ], string="返修类型", required=True)
    
    repair_ie_price = fields.Float(string="返修IE工价")

    repair_ie_total_price = fields.Float(string="返修总IE工价", compute="set_repair_ie_price", store=True)

    @api.depends("repair_ie_price", "number")
    def set_repair_ie_price(self):
        for record in self:
            record.repair_ie_total_price = record.repair_ie_price * record.number

    repair_price = fields.Float(string="返修工价")

    repair_total_price = fields.Float(string="返修总工价", compute="set_repair_price", store=True)

    @api.depends("repair_price", "number")
    def set_repair_price(self):
        for record in self:
            record.repair_total_price = record.repair_price * record.number


    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")

    def set_lock_state(self):
        ''' 设置审批状态'''

        for record in self:
            lock_state = self.env.context.get("lock_state")
            if lock_state == "已审批":
                record.sudo().lock_state = "已审批"
            elif lock_state == "未审批":
                record.sudo().lock_state = "未审批"


    def check_lock_state(self):
        ''' 检查审批状态'''
        if self.lock_state == "已审批":
            raise ValidationError(f"该外发退货已审批，不可对其进行操作！")



    def write(self, vals):

        for record in self:
            record.check_lock_state()


        res = super(OutbourceReturn, self).write(vals)

        return res



    def unlink(self):

        for record in self:
            record.check_lock_state()

        res = super(OutbourceReturn, self).unlink()

        return res












