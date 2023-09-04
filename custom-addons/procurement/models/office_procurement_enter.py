from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfficeProcurementEnter(models.Model):
    _name = 'office_procurement_enter'
    _description = '办公室采购记录'
    _rec_name = 'material_name'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    state = fields.Selection([
        ('待审批', '待审批'),
        ('待采购', '待采购'),
        ('已采购', '已采购')
        ], string="状态", default="待审批")

    material_code = fields.Many2one("office_object_instance", string="物品编码", required=True)
    material_name = fields.Char(string="物品名称", store=True, compute="set_material_info")

    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", compute="set_material_info", store=True)
    specification = fields.Char(string="规格", compute="set_material_info", store=True)
    unit_price = fields.Float(string="单价")
    unit = fields.Char(string="单位", compute="set_material_info", store=True)
    is_consumables = fields.Selection([('是', '是'), ('否', '否')], string="是否消耗品", store=True, compute="set_material_info")
    @api.depends('material_code')
    def set_material_info(self):
        for record in self:
            if record.material_code:
                record.material_name = record.material_code.material_name
                record.specification = record.material_code.specification
                record.supplier_supplier_id = record.material_code.supplier_supplier_id.id
                record.unit = record.material_code.unit
                record.is_consumables = record.material_code.is_consumables



    amount = fields.Float(string="数量")
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True)

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

    admin_department = fields.Many2one("hr.department", string="采购部门", required=True)
    manager = fields.Many2one('hr.employee', string="采购人", required=True)

    remark = fields.Char(string="备注")

    payment_state = fields.Selection([
        ("未付款", "未付款"),
        ("已付款", "已付款"),
    ], string="付款状态", default="未付款")

    procurement_inventory_id = fields.Many2one("office_procurement_inventory", string="库存id")



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
            'res_model': 'office_procurement_enter',
            'view_id': self.env.ref('procurement.office_procurement_enter_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.state = "待审批"

        elif button_type == "through":
            self.state = "待采购"
        elif button_type == "设为已付款":
            self.payment_state = "已付款"
        elif button_type == "设为未付款":
            self.payment_state = "未付款"


    def write(self, vals):

        for record in self:
            if record.state == "待采购":
                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass
                elif record.payment_state == "未付款" and all(i in ["is_invoice", "tax", "after_tax_amount"] for i in vals):
                    pass
                else:

                    raise ValidationError(f"已经审批的记录, 不可编辑！")

            if record.state == "已采购":

                if ("state" in vals or "inventory_id" in vals or "payment_state" in vals) and len(vals) == 1:
                    pass
                elif record.payment_state == "未付款" and all(i in ["is_invoice", "tax", "after_tax_amount"] for i in vals):
                    pass
                else:

                    raise ValidationError(f"已采购的记录, 不可编辑！")

        res = super(OfficeProcurementEnter, self).write(vals)

        return res


    def unlink(self):

        for record in self:
            if record.state == "待采购" or record.state == "已采购":

                raise ValidationError(f"已经审批或已经采购的记录不可删除")

        res = super(OfficeProcurementEnter, self).unlink()

        return res