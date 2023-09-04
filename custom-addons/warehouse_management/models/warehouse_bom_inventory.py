from odoo import models, fields, api
from odoo.exceptions import ValidationError
from decimal import *


class WarehouseBomInventory(models.Model):
    _name = 'warehouse_bom_inventory'
    _description = '仓库物料单(库存)'
    _rec_name = 'material_name'
    _order = "write_date desc"


    # date = fields.Date(string="日期", required=True)
    # odd_numbers = fields.Char(string="入库单号", required=True)

    material_coding = fields.Many2one("material_list", string="物料")
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号')
    style_number = fields.Many2one('ib.detail', string='款号')


    supplier = fields.Char(string="供应商", related="material_coding.supplier", store=True)
    client = fields.Char(string="客户", related="material_coding.client", store=True)
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    color = fields.Char(string="颜色", related="material_coding.color", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)

    amount = fields.Float(string="数量", compute="set_amount", store=True)
    money_sum = fields.Float(string="总价", compute="_set_money_sum", store=True, digits=(16, 5))

    warehouse_bom_id = fields.One2many("warehouse_bom", "warehouse_bom_inventory_id", string="入库明细")

    outbound_ids = fields.One2many("warehouse_bom_outbound", "warehouse_bom_inventory_id", string="出库明细")



    # 计算库存数量
    @api.depends('warehouse_bom_id', 'outbound_ids', 'warehouse_bom_id.amount', 'outbound_ids.amount')
    def set_amount(self):
        for record in self:

            record.amount = Decimal(str(sum(Decimal(str(i.amount)) for i in record.warehouse_bom_id))) - Decimal(str(sum(Decimal(str(i.amount)) for i in record.outbound_ids)))


    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price



    
