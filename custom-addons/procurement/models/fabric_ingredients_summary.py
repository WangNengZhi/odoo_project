from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class FabricIngredientsProcurement(models.Model):
    """ 面辅料采购继承"""
    _inherit = 'fabric_ingredients_procurement'

    def create_fabric_ingredients_summary(self):
        for record in self:
            if not self.env["fabric_ingredients_summary"].sudo().search(
                    [("fabric_ingredients_procurement_id", "=", record.id)]):
                self.env["fabric_ingredients_summary"].sudo().create({
                    "fabric_ingredients_procurement_id": record.id,
                })

    @api.model
    def create(self, vals):
        res = super(FabricIngredientsProcurement, self).create(vals)

        res.create_fabric_ingredients_summary()

        return res


class FabricIngredientsRefund(models.Model):
    """ 面辅料退还继承"""
    _inherit = 'fabric_ingredients_refund'

    def create_fabric_ingredients_summary(self):
        for record in self:
            if not self.env["fabric_ingredients_summary"].sudo().search(
                    [("fabric_ingredients_refund_id", "=", record.id)]):
                self.env["fabric_ingredients_summary"].sudo().create({
                    "fabric_ingredients_refund_id": record.id,
                })

    @api.model
    def create(self, vals):
        res = super(FabricIngredientsRefund, self).create(vals)

        res.create_fabric_ingredients_summary()

        return res


class FabricIngredientsSummary(models.Model):
    _name = 'fabric_ingredients_summary'
    _description = '面辅料采购汇总'
    _rec_name = 'date'
    _order = "date desc"

    fabric_ingredients_procurement_id = fields.Many2one("fabric_ingredients_procurement", string="采购",
                                                        ondelete='cascade')

    fabric_ingredients_refund_id = fields.Many2one("fabric_ingredients_refund", string="退还", ondelete='cascade')

    date = fields.Date(string="日期", compute="set_rec_info", store=True)
    material_code = fields.Many2one("material_code", string="物品编码", compute="set_rec_info", store=True)

    event_type = fields.Selection([('采购', '采购'), ('退还', '退还')], string="事件类型", compute="set_rec_info",
                                  store=True)

    state = fields.Selection([
        ('待审批', '待审批'),
        ('待采购', '待采购'),
        ('已采购', '已采购'),
        ('待退还', '待退还'),
        ('已退还', '已退还')
    ], string="状态", compute="set_rec_info", store=True)

    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
    ], string="物料类型", compute="set_rec_info", store=True)

    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', compute="set_rec_info", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', compute="set_rec_info", store=True)

    material_name = fields.Char(string="物品名称", compute="set_rec_info")
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", compute="set_rec_info", store=True)
    specification = fields.Char(string="规格", compute="set_rec_info")
    department_name = fields.Char(string="采购部门")
    unit_price = fields.Float(string="单价", digits=(16, 3), compute="set_rec_info")
    unit = fields.Char(string="单位", compute="set_rec_info")

    amount = fields.Float(string="数量", compute="set_rec_info", store=True)
    fine = fields.Float(string='罚款')
    money_sum = fields.Float(string="金额", compute="set_rec_info", store=True)

    manager = fields.Many2one('hr.employee', string="负责人", compute="set_rec_info", store=True)

    is_invoice = fields.Boolean(string='是否开票', compute="set_rec_info", store=True)

    tax = fields.Float(string="税点", digits=(16, 10), compute="set_rec_info")
    after_tax_amount = fields.Float(string="税后金额", compute="_set_after_tax_amount_test", store=True)

    payment_state = fields.Selection([
        ("未付款", "未付款"),
        ("部分付款", "部分付款"),
        ("已付款", "已付款"),
        ("未退款", "未退款"),
        ("已退款", "已退款"),
    ], string="付款状态")

    payment_state_date = fields.Date(string="付款状态改变日期")

    def set_payment_state(self):
        for record in self:
            record.payment_state = "未退款"

    remark = fields.Char(string="备注", compute="set_rec_info")

    @api.depends("fabric_ingredients_procurement_id",
                 "fabric_ingredients_procurement_id.date",
                 "fabric_ingredients_procurement_id.material_code",
                 "fabric_ingredients_procurement_id.state",
                 "fabric_ingredients_procurement_id.type",
                 "fabric_ingredients_procurement_id.order_id",
                 "fabric_ingredients_procurement_id.style_number",
                 "fabric_ingredients_procurement_id.supplier_supplier_id",
                 "fabric_ingredients_procurement_id.manager",
                 "fabric_ingredients_procurement_id.is_invoice",
                 "fabric_ingredients_refund_id",
                 "fabric_ingredients_refund_id.date",
                 "fabric_ingredients_refund_id.material_code",
                 "fabric_ingredients_refund_id.state",
                 "fabric_ingredients_refund_id.type",
                 "fabric_ingredients_refund_id.order_id",
                 "fabric_ingredients_refund_id.style_number",
                 "fabric_ingredients_refund_id.supplier_supplier_id",
                 "fabric_ingredients_refund_id.manager",
                 "fabric_ingredients_refund_id.is_invoice")
    def set_rec_info(self):

        for record in self:

            if record._context.get('bypass_rec_info'):
                print(record._context.get('bypass_rec_info'))
                continue

            if record.fabric_ingredients_procurement_id:
                obj = record.fabric_ingredients_procurement_id
                event_type = "采购"
            elif record.fabric_ingredients_refund_id:
                obj = record.fabric_ingredients_refund_id
                event_type = "退还"

            money_sum = -obj.money_sum if event_type == "退还" else obj.money_sum
            money_sum -= record.fine

            # after_tax_amount = -obj.after_tax_amount if event_type == "退还" else obj.after_tax_amount
            # after_tax_amount = (record.money_sum - record.fine) * (1 + record.tax)

            record.sudo().write({
                "date": obj.date,
                "material_code": obj.material_code.id,
                "event_type": event_type,
                "state": obj.state,
                "type": obj.type,
                "order_id": obj.order_id.id,
                "style_number": obj.style_number.id,
                "material_name": obj.material_name,
                "supplier_supplier_id": obj.supplier_supplier_id.id,
                "specification": obj.specification,
                "department_name": obj.department_name,
                "unit_price": obj.unit_price,
                "unit": obj.unit,
                "amount": -obj.amount if event_type == "退还" else obj.amount,
                "money_sum": money_sum,
                "manager": obj.manager.id,
                "is_invoice": obj.is_invoice,
                "tax": obj.tax,
                # "after_tax_amount": after_tax_amount,
                "remark": obj.remark,
                "payment_state": obj.payment_state,
            })

    @api.depends('tax', 'money_sum', 'fine')
    def _set_after_tax_amount_test(self):
        for record in self:
            if record.tax:
                record.after_tax_amount = (record.money_sum - record.fine) * (1 + record.tax)
                print(record.after_tax_amount)
            else:
                record.after_tax_amount = record.money_sum
                print(record.after_tax_amount)

    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""

        if button_type == "设为已付款":
            name = "确认设为已付款吗？"
        elif button_type == "设为未付款":
            name = "确认设为未付款吗？"
        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'fabric_ingredients_summary',
            'view_id': self.env.ref('procurement.fabric_ingredients_summary_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "设为已付款":
            self.payment_state = "已付款"
            if self.event_type == "采购":
                self.fabric_ingredients_procurement_id.payment_state = "已付款"

        elif button_type == "设为未付款":
            self.payment_state = "未付款"
            if self.event_type == "采购":
                self.fabric_ingredients_procurement_id.payment_state = "未付款"

        elif button_type == "设为部分付款":
            self.payment_state = "部分付款"
            if self.event_type == "采购":
                self.fabric_ingredients_procurement_id.payment_state = "部分付款"

        elif button_type == "设为已退款":
            self.payment_state = "已退款"
            if self.event_type == "退还":
                self.fabric_ingredients_refund_id.payment_state = "已退款"

        elif button_type == "设为未退款":
            self.payment_state = "未退款"
            if self.event_type == "退还":
                self.fabric_ingredients_refund_id.payment_state = "未退款"

        elif button_type == "部分付款":
            self.payment_state = "设为部分付款"
            if self.event_type == "退还":
                self.fabric_ingredients_refund_id.payment_state = "部分付款"

        self.payment_state_date = fields.Date.today()

    def modify_penalty(self):
        """修改罚款金额"""
        button_type = self._context.get("type")

        if button_type == "设置罚款金额":
            name = "确认设置罚款金额吗？"

            action = {
                'name': name,
                'view_mode': 'form',
                'res_model': 'fabric_ingredients_summary',
                'view_id': self.env.ref('procurement.fabric_ingredients_summary_edit_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new'
            }

            return action

    def action_state_confirm(self):
        """确认计算金额"""
        for record in self:
            pass