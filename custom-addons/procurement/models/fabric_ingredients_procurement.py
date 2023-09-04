from odoo import models, fields, api
from odoo.exceptions import ValidationError



class FabricIngredientsProcurement(models.Model):
    _name = 'fabric_ingredients_procurement'
    _description = '面辅料采购'
    _rec_name = 'material_name'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    material_code = fields.Many2one("material_code", string="物品编码")
    state = fields.Selection([
        ('待审批', '待审批'),
        ('待采购', '待采购'),
        ('已采购', '已采购')
        ], string="状态", default="待审批")

    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
        ], string="物料类型", required=True)

    use_type = fields.Selection([('用料', '用料'), ('储备用料', '储备用料')], string="物料类型", required=True)
        
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)

    @api.onchange('order_id')
    def _onchange_style_number(self):

        self.style_number = False

        if self.order_id and not self.order_id.is_conceal:
            
            return {'domain': {'style_number': [('id', 'in', self.order_id.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}


    material_name = fields.Char(string="物品名称")
    department_name = fields.Char(string="采购部门")
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", domain=[('is_activity', '=', True)])
    specification = fields.Char(string="规格")
    unit_price = fields.Float(string="单价", digits=(16, 3))
    unit = fields.Char(string="单位")

    amount = fields.Float(string="数量")
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(f"数量不可小于0")
            
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True, digits=(16, 3))

    manager = fields.Many2one('hr.employee', string="负责人")

    payment_state = fields.Selection([
        ("未付款", "未付款"),
        ("部分付款", "部分付款"),
        ("已付款", "已付款"),
    ], string="付款状态", default="未付款")
    raw_materials_order_id = fields.Many2one("raw_materials_order", string="面辅料订单")

    is_invoice = fields.Boolean(string='是否开票')

    tax = fields.Float(string="税点", digits=(16, 10))
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
            'res_model': 'fabric_ingredients_procurement',
            'view_id': self.env.ref('procurement.fabric_ingredients_procurement_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action



    def is_exist_put_storage(self) -> bool:
        if self.type == "面料":
            objs = self.env["plus_material_enter"].sudo().search([
                ("material_coding.material_code", "=", self.material_code.id),
                ("state", "=", "已入库")
            ])
        else:
            objs = self.env["warehouse_bom"].sudo().search([
                ("material_coding.material_code", "=", self.material_code.id),
                ("state", "=", "已入库")
            ])
        
        return objs


    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            if self.state == "待采购":
                self.state = "待审批"
            elif self.state == "已采购":
                if self.is_exist_put_storage():
                    raise ValidationError(f"已经存在确认的入库记录,不可回退!")
                else:
                    self.state = "待采购"

        elif button_type == "through":

            if not self.material_code or not self.manager or self.manager == 0:
                raise ValidationError(f"物料编码、负责人、采购数量未设置！")

            self.state = "待采购"
            self.material_code.type = "待采购"
        elif button_type == "设为已付款":
            self.payment_state = "已付款"
        elif button_type == "设为未付款":
            self.payment_state = "未付款"



    def copy(self, default=None):
        self.ensure_one()

        if self.material_code:
            raise ValidationError(f"已经生成物料编码，不可复制！")

        return super(FabricIngredientsProcurement, self).copy(default=default)



    def write(self, vals):

        for record in self:

            

            if record.state == "待采购":
                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass

                elif record.payment_state == "未付款" and all(i in ["is_invoice", "tax", "after_tax_amount"] for i in vals):
                    pass
                else:
                    raise ValidationError(f"已经审批的记录, 不可编辑！")
                    
            elif record.state == "已采购":

                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass
                elif record.payment_state == "未付款" and all(i in ["is_invoice", "tax", "after_tax_amount"] for i in vals):
                    pass
                else:
                    raise ValidationError(f"已采购的记录, 不可编辑！")


        res = super(FabricIngredientsProcurement, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "待采购" or record.state == "已采购":

                raise ValidationError(f"已经审批的记录, 不可删除！")

            if record.type == "面料":
                fip_obj = self.env["plus_material_list"].sudo().search([("material_code", "=", record.material_code.id)])
            else:
                fip_obj = self.env["material_list"].sudo().search([("material_code", "=", record.material_code.id)])
            if fip_obj:
                record.material_code.type = record.type if record.type == "面料" else "物料"
            else:
                record.material_code.sudo().unlink()
        res = super(FabricIngredientsProcurement, self).unlink()

        return res