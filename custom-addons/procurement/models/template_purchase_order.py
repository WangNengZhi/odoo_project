from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TemplatePurchaseOrder(models.Model):
    _name = 'template_purchase_order'
    _description = '模板采购单'
    _rec_name = 'apply_date'
    _order = "apply_date desc"


    apply_date = fields.Date(string="申请日期", required=True)
    apply_department = fields.Many2one("hr.department", string="申请部门", required=True)
    state = fields.Selection([('待采购', '待采购'), ('正在采购', '正在采购'), ('已领用', '已领用')], string="状态", default="待采购")

    money_sum = fields.Float(string="合计金额", compute="_set_money_sum", store=True)

    firm_principal = fields.Many2one('hr.employee', string="公司负责人", required=True)
    manager = fields.Many2one('hr.employee', string="主管/经理", required=True)
    proposer = fields.Many2one('hr.employee', string="申请人", required=True)

    template_purchase_order_line_ids = fields.One2many("template_purchase_order_line", "template_purchase_order_id", string="模板采购单明细")


    # 计算总价格
    @api.depends('template_purchase_order_line_ids')
    def _set_money_sum(self):
        for record in self:

            tem_money_sum = 0

            for line_obj in record.template_purchase_order_line_ids:

                tem_money_sum = tem_money_sum + line_obj.money_sum

            record.money_sum = tem_money_sum


    # 确认采购
    def action_confirm_purchase(self):
        for record in self:
            record.state = "正在采购"

    # 确认领用
    def action_confirm_recipients(self):
        for record in self:
            record.state = "已领用"


    # 写入方法
    def write(self, vals):

        if self.state == "正在采购":

            if len(vals) and "state" in vals:
                pass
            else:

                raise ValidationError(f"已经确认采购，不可修改。")

        elif self.state == "已领用":

            raise ValidationError(f"已经确认采购，不可修改。")

        res = super(TemplatePurchaseOrder, self).write(vals)

        return res







class TemplatePurchaseOrderLine(models.Model):
    _name = 'template_purchase_order_line'
    _description = '模板采购单明细'
    _rec_name = 'name'


    template_purchase_order_id = fields.Many2one("template_purchase_order", string="模板采购单id")
    # item_name = fields.Char(string="物品名称", required=True)
    item_name = fields.Many2one("production_operation_ingredients_list", string="物品编码")
    name = fields.Char(string="物品名称")
    # supplier_supplier_id = fields.Many2one("supplier_supplier", related="item_name.supplier_supplier_id", store=True, string="供应商")
    firm = fields.Char(string="厂商")
    brand = fields.Char(string="品牌")
    specification = fields.Char(string="规格")

    unit_price = fields.Float(string="单价")
    unit = fields.Char(string="单位")

    amount = fields.Float(string="数量", required=True)
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True)

    remark = fields.Char(string="备注")




    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price