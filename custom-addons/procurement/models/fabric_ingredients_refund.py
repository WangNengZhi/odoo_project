from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FabricIngredientsRefund(models.Model):
    _name = 'fabric_ingredients_refund'
    _description = '面辅料退还'
    _rec_name = 'date'
    _order = "date desc"


    fabric_ingredients_procurement_id = fields.Many2one("fabric_ingredients_procurement", string="采购", required=True)
    date = fields.Date(string="日期", required=True)
    material_code = fields.Many2one("material_code", string="物品编码", store=True)


    state = fields.Selection([
        ('待审批', '待审批'),
        ('待退还', '待退还'),
        ('已退还', '已退还')
        ], string="状态", default="待审批")

    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
        ], string="物料类型", related="fabric_ingredients_procurement_id.type", store=True)
        
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="fabric_ingredients_procurement_id.order_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="fabric_ingredients_procurement_id.style_number", store=True)

    material_name = fields.Char(string="物品名称", related="fabric_ingredients_procurement_id.material_name", store=True)
    department_name = fields.Char(string="退还部门", related="fabric_ingredients_procurement_id.department_name", store=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", related="fabric_ingredients_procurement_id.supplier_supplier_id", store=True)
    specification = fields.Char(string="规格", related="fabric_ingredients_procurement_id.specification", store=True)
    unit_price = fields.Float(string="单价", digits=(16, 3), related="fabric_ingredients_procurement_id.unit_price", store=True)
    unit = fields.Char(string="单位", related="fabric_ingredients_procurement_id.unit", store=True)

    amount = fields.Float(string="数量")

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(f"数量不可小于0")

    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True, digits=(16, 3))

    manager = fields.Many2one('hr.employee', string="负责人")

    payment_state = fields.Selection([
        ("未退款", "未退款"),
        ("部分付款", "部分付款"),
        ("已退款", "已退款"),
    ], string="退款状态", default="未退款")

    def set_payment_state(self):
        for record in self:
            record.payment_state = "未退款"


    is_invoice = fields.Boolean(string='是否开票', related="fabric_ingredients_procurement_id.is_invoice", store=True)

    tax = fields.Float(string="税点", digits=(16, 10), related="fabric_ingredients_procurement_id.tax", store=True)
    after_tax_amount = fields.Float(string="税后金额", compute="_set_after_tax_amount", store=True, digits=(16, 3))
    # 计算税后金额
    @api.depends('tax', 'money_sum', 'is_invoice')
    def _set_after_tax_amount(self):
        for record in self:

            if record.is_invoice:

                if record.tax:
                    record.after_tax_amount = record.money_sum * (1 + record.tax)
                else:

                    record.after_tax_amount = record.money_sum
            else:
                record.tax = 0
                record.after_tax_amount = record.money_sum

    remark = fields.Char(string="备注")


    plus_material_inventory_id = fields.Many2one("plus_material_inventory", string="面料库存")

    warehouse_bom_inventory_id = fields.Many2one("warehouse_bom_inventory", string="物料库存")


    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price




    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"
        elif button_type == "设为已付款":
            name = "确认设为已付款吗？"
        elif button_type == "设为未付款":
            name = "确认设为未付款吗？"
        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'fabric_ingredients_refund',
            'view_id': self.env.ref('procurement.fabric_ingredients_refund_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action



    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            if self.state == "待退还":
                self.state = "待审批"
            elif self.state == "已退还":
                self.state = "待退还"

        elif button_type == "through":

            if not self.material_code or not self.manager or self.manager == 0:
                raise ValidationError(f"物料编码、负责人、采购数量未设置！")

            self.state = "待退还"

        elif button_type == "设为已付款":
            self.payment_state = "已付款"
        elif button_type == "设为未付款":
            self.payment_state = "未付款"



    

    def check_inventory(self, vals):
        if self.type == "面料":
            if vals['amount'] > self.plus_material_inventory_id.amount:
                raise ValidationError(f"退还数量不可大于库存数！")
        else:
            if vals['amount'] > self.warehouse_bom_inventory_id.amount:
                raise ValidationError(f"退还数量不可大于库存数！")


    def write(self, vals):

        for record in self:

        
            if record.state == "待退还":
                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass
                else:
                    raise ValidationError(f"已经审批的记录, 不可编辑！")

                    
            elif record.state == "已退还":

                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass
                else:
                    raise ValidationError(f"已经审批的记录, 不可编辑！")
                    
            if "amount" in vals:
                record.check_inventory(vals)

        res = super(FabricIngredientsRefund, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "待退还" or record.state == "已退还":

                raise ValidationError(f"已经审批的记录, 不可删除！")

        res = super(FabricIngredientsRefund, self).unlink()

        return res


