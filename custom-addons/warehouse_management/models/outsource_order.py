from odoo import api, fields, models
from odoo.exceptions import ValidationError

''' 库存'''
class FinishedInventory(models.Model):
    _inherit = "finished_inventory"


    def set_outsource_order(self):
        for record in self:
            
            outsource_order_line_objs = self.env['outsource_order_line'].sudo().search([
                ("outsource_order_id.order_id", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.size.id)
            ])
            for outsource_order_line_obj in outsource_order_line_objs:
                outsource_order_line_obj.outsource_order_id.finished_inventory_id = [(4, record.id)]


    @api.model
    def create(self, vals):

        res = super(FinishedInventory, self).create(vals)

        res.sudo().set_outsource_order()

        return res


class OutsourceOrder(models.Model):
    """ 继承外发订单"""
    _inherit = 'outsource_order'



    finished_inventory_id = fields.Many2many("finished_inventory", string="成衣库存")
    stock = fields.Integer(string="存量", compute="set_stock", store=True)
    @api.depends("finished_inventory_id", "finished_inventory_id.stock")
    def set_stock(self):
        for record in self:
            if record.order_id:

                outsource_order_objs = self.env['outsource_order'].sudo().search([("order_id", "=", record.order_id.id)], order='date')
                if len(outsource_order_objs) == 1:
                    record.stock = sum(record.finished_inventory_id.mapped("stock"))
                else:

                    total_stock = sum(outsource_order_objs.mapped("finished_inventory_id").mapped("stock"))
                    
                    for outsource_order_obj in outsource_order_objs:
                        if outsource_order_obj.order_quantity < total_stock:
                            outsource_order_obj.stock = outsource_order_obj.order_quantity
                            total_stock = total_stock - outsource_order_obj.order_quantity
                        else:
                            outsource_order_obj.stock = total_stock
                            total_stock = 0


    incomplete_quantity = fields.Integer(string="未完成件数", compute="set_incomplete_quantity", store=True)
    @api.depends("order_quantity", "stock")
    def set_incomplete_quantity(self):
        for record in self:
            incomplete_quantity = record.order_quantity - record.stock
            if incomplete_quantity >= 0:
                record.incomplete_quantity = incomplete_quantity
            else:
                record.incomplete_quantity = 0
    
    incomplete_deduction = fields.Float(string="未完成扣款", compute="set_incomplete_deduction", store=True)
    @api.depends("incomplete_quantity", "outsource_price")
    def set_incomplete_deduction(self):
        for record in self:
            record.incomplete_deduction = record.incomplete_quantity * record.outsource_price


    state = fields.Selection([
        ('未上线', '未上线'),
        ('未完成', '未完成'),
        ('已完成', '已完成'),
        ('退单', '退单')
        ], string="订单状态", default="未上线", compute="auto_complete", store=True)
    @api.depends('order_quantity', 'stock')
    def auto_complete(self):
        for record in self:
            if record.state != "退单":
                if record.order_quantity and record.stock and record.order_quantity <= record.stock:
                    record.state = "已完成"
                else:
                    record.state = "未完成"

    defective_number = fields.Integer(string="报次件数", compute="set_defective_number", store=True)
    @api.depends('finished_inventory_id', 'finished_inventory_id.defective_put_number')
    def set_defective_number(self):
        for record in self:
            # record.defective_number = sum(record.finished_inventory_id.mapped("defective_put_number"))
            record.defective_number = sum(record.finished_inventory_id.finished_product_ware_line_ids.filtered(lambda x: x.production_factory.id == record.outsource_plant_id.id and x.type == '入库' and x.quality == '报次').mapped("number"))

    defective_deduction = fields.Float(string="报次扣款", compute="set_defective_deduction", store=True)
    @api.depends("defective_number", "outsource_price")
    def set_defective_deduction(self):
        for record in self:
            record.defective_deduction = record.defective_number * record.outsource_price
    
    is_compensation = fields.Boolean(string="是否赔偿")
    compensation = fields.Float(string="赔偿", compute="set_compensation", store=True)
    @api.depends('defective_number')
    def set_compensation(self):
        for record in self:
            record.compensation = record.defective_number * 10


    total_deduction = fields.Float(string="总扣款", compute="set_total_deduction", store=True)
    @api.depends('deduct_money', 'incomplete_deduction', 'defective_deduction', 'other_deductions', 'compensation', 'is_compensation')
    def set_total_deduction(self):
        for record in self:
            if record.is_compensation:
                record.total_deduction = (record.deduct_money + record.incomplete_deduction + record.defective_deduction + record.other_deductions + record.compensation)
            else:
                record.total_deduction = (record.deduct_money + record.incomplete_deduction + record.defective_deduction + record.other_deductions)


    @api.depends("total_price", "total_deduction")
    def set_customer_payment_amount(self):
        ''' 重写计算付款金额的方法'''
        for record in self:
            
            record.customer_payment_amount = record.total_price - record.total_deduction


    # @api.depends('outsource_price', 'outsource_order_line_ids', 'outsource_order_line_ids.actual_cutting_price', 'total_deduction')
    # def _value_total_price(self):
    #     ''' 重写计算加工费的方法'''
    #     for record in self:
    #         record.total_price = sum(record.outsource_order_line_ids.mapped("actual_cutting_price")) - record.total_deduction



    def refresh_stock(self):
        for record in self:
            
            finished_inventory_objs = self.env['finished_inventory'].sudo().search([
                ("order_number", "=", record.order_id.id),
                ("style_number", "in", record.outsource_order_line_ids.style_number.ids),
                ("size", "in", record.outsource_order_line_ids.size.ids)
            ])

            record.finished_inventory_id = [(6, 0, finished_inventory_objs.ids)]



    def mod_stock(self):
        ''' 用于手动修改存量'''

        action = {
            'name': "修改存量",
            'view_mode': 'form',
            'res_model': 'outsource_order_stock_setting_wizard',
            'view_id': self.env.ref('warehouse_management.outsource_order_stock_setting_wizard_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

        return action


class OutsourceOrderStockSettingWizard(models.TransientModel):
    _name = 'outsource_order_stock_setting_wizard'
    _description = '外发订单存量设置向导'


    stock = fields.Integer(string="存量")


    def set_stock(self):
        ''' 用于手动修改存量'''
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')
        for active_id in active_ids:
            obj = self.env[active_model].sudo().browse(active_id)
            obj.stock = self.stock






    