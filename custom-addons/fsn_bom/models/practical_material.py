from odoo.exceptions import ValidationError
from odoo import models, fields, api
from decimal import *

class FabricIngredientsProcurement(models.Model):
    """ 继承面辅料采购"""
    _inherit = 'fabric_ingredients_procurement'

    def set_practical_material(self):
        for record in self:
            if not self.env["practical_material"].sudo().search([("fabric_ingredients_procurement_id", "=", record.id)]):
                self.env['practical_material'].sudo().create({"fabric_ingredients_procurement_id": record.id})
    

    @api.model
    def create(self, vals):

        res = super(FabricIngredientsProcurement, self).create(vals)

        res.sudo().set_practical_material()

        return res

class FabricIngredientsRefund(models.Model):
    """ 继承面辅料退还"""
    _inherit = 'fabric_ingredients_refund'

    def set_practical_material(self):

        for record in self:
            practical_material_obj = self.env['practical_material'].sudo().search([("material_code", "=", record.material_code.id)])
            practical_material_obj.fabric_ingredients_refund_id = record.id

    @api.model
    def create(self, vals):

        res = super(FabricIngredientsRefund, self).create(vals)

        res.sudo().set_practical_material()

        return res



class PracticalMaterial(models.Model):
    _name = 'practical_material'
    _description = '实际用料表'
    _rec_name = 'style_number'
    _order = 'date desc'

    fabric_ingredients_procurement_id = fields.Many2one("fabric_ingredients_procurement", string="面辅料采购",  ondelete='cascade')
    fabric_ingredients_refund_id = fields.Many2one("fabric_ingredients_refund", string="面辅料退还")


    date = fields.Date(string="日期", compute="set_practical_material_info", store=True)
    material_code = fields.Many2one("material_code", string="物品编码", compute="set_practical_material_info", store=True)
    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
        ], string="物料类型", compute="set_practical_material_info", store=True)
    state = fields.Selection([
        ('待审批', '待审批'),
        ('待采购', '待采购'),
        ('已采购', '已采购')
        ], string="状态", compute="set_practical_material_info", store=True)
        
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', compute="set_practical_material_info", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', compute="set_practical_material_info", store=True)

    material_name = fields.Char(string="物品名称", compute="set_practical_material_info", store=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", compute="set_practical_material_info", store=True)
    specification = fields.Char(string="规格", compute="set_practical_material_info", store=True)
    unit_price = fields.Float(string="单价", digits=(16, 3), compute="set_practical_material_info", store=True)
    unit = fields.Char(string="单位", compute="set_practical_material_info", store=True)

    amount = fields.Float(string="数量", compute="set_practical_material_info", store=True)
            
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True, digits=(16, 3))

    manager = fields.Many2one('hr.employee', string="负责人", compute="set_practical_material_info", store=True)

    payment_state = fields.Selection([
        ("未付款", "未付款"),
        ("部分付款", "部分付款"),
        ("已付款", "已付款"),
    ], string="付款状态", default="未付款", compute="set_practical_material_info", store=True)

    is_invoice = fields.Boolean(string='是否开票', compute="set_practical_material_info", store=True)

    tax = fields.Float(string="税点", digits=(16, 10), compute="set_practical_material_info", store=True)
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

    remark = fields.Char(string="备注", compute="set_practical_material_info", store=True)


    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price

    @api.depends("fabric_ingredients_procurement_id",\
        'fabric_ingredients_procurement_id.date',\
        'fabric_ingredients_procurement_id.material_code',\
        'fabric_ingredients_procurement_id.type',\
        'fabric_ingredients_procurement_id.state',\
        'fabric_ingredients_procurement_id.order_id',\
        'fabric_ingredients_procurement_id.style_number',\
        'fabric_ingredients_procurement_id.material_name',\
        'fabric_ingredients_procurement_id.supplier_supplier_id',\
        'fabric_ingredients_procurement_id.specification',\
        'fabric_ingredients_procurement_id.unit_price',\
        'fabric_ingredients_procurement_id.unit',\
        'fabric_ingredients_procurement_id.amount',\
        'fabric_ingredients_procurement_id.manager',\
        'fabric_ingredients_procurement_id.payment_state',\
        'fabric_ingredients_procurement_id.is_invoice',\
        'fabric_ingredients_procurement_id.tax',\
        "fabric_ingredients_refund_id",\
        "fabric_ingredients_refund_id.amount")
    def set_practical_material_info(self):
        for record in self:
            if record.fabric_ingredients_procurement_id:
                record.date = record.fabric_ingredients_procurement_id.date
                record.material_code = record.fabric_ingredients_procurement_id.material_code.id
                record.type = record.fabric_ingredients_procurement_id.type
                record.state = record.fabric_ingredients_procurement_id.state
                record.order_id = record.fabric_ingredients_procurement_id.order_id
                record.style_number = record.fabric_ingredients_procurement_id.style_number
                record.material_name = record.fabric_ingredients_procurement_id.material_name
                record.supplier_supplier_id = record.fabric_ingredients_procurement_id.supplier_supplier_id.id


                record.specification = record.fabric_ingredients_procurement_id.specification
                record.unit_price = record.fabric_ingredients_procurement_id.unit_price
                record.unit = record.fabric_ingredients_procurement_id.unit
                record.amount = Decimal(str(record.fabric_ingredients_procurement_id.amount)) - Decimal(str(record.fabric_ingredients_refund_id.amount)) if record.fabric_ingredients_refund_id else record.fabric_ingredients_procurement_id.amount
                record.manager = record.fabric_ingredients_procurement_id.manager.id
                record.payment_state = record.fabric_ingredients_procurement_id.payment_state
                record.is_invoice = record.fabric_ingredients_procurement_id.is_invoice
                record.tax = record.fabric_ingredients_procurement_id.tax







