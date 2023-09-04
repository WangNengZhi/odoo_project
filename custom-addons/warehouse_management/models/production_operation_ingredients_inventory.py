from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PlusMaterialInventory(models.Model):
    _name = 'production_operation_ingredients_inventory'
    _description = '仓库生产工具(库存)'
    _rec_name = 'material_name'
    _order = "write_date desc"


    material_coding = fields.Many2one("production_operation_ingredients_list", string="物料编号")
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    # supplier_supplier_id = fields.Many2one("supplier_supplier", related="material_coding.supplier_supplier_id", store=True, string="供应商")
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)

    amount = fields.Float(string="数量", store=True)
    money_sum = fields.Float(string="总价", compute="_set_money_sum", store=True, digits=(16, 5))

    production_operation_ingredients_enter_ids = fields.One2many("production_operation_ingredients_enter", "production_operation_ingredients_inventory_id", string="入库明细")

    production_operation_ingredients_outbound_ids = fields.One2many("production_operation_ingredients_outbound", "production_operation_ingredients_inventory_id", string="出库明细")




    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price