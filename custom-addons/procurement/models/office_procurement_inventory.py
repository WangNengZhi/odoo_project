from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OfficeProcurementInventory(models.Model):
    _name = 'office_procurement_inventory'
    _description = '办公室采购库存记录'
    _rec_name = 'material_name'
    _order = "write_date desc"



    material_code = fields.Many2one("office_object_instance", string="物品编码")
    material_name = fields.Char(string="物品名称", related="material_code.material_name", store=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", related="material_code.supplier_supplier_id", store=True)
    specification = fields.Char(string="规格", related="material_code.specification", store=True)

    unit = fields.Char(string="单位", related="material_code.unit", store=True)

    amount = fields.Float(string="库存数量", compute="set_amount", store=True)


    procurement_enter_line_ids = fields.One2many("office_procurement_enter", "procurement_inventory_id", string="采购明细（作废）")

    procurement_put_line_ids = fields.One2many("office_procurement_put", "procurement_inventory_id", string="入库明细")

    procurement_outbound_line_ids = fields.One2many("office_procurement_outbound", "procurement_inventory_id", string="出库明细")



    # 计算入库数量
    @api.depends('procurement_put_line_ids', 'procurement_outbound_line_ids')
    def set_amount(self):
        for record in self:


            put_number = sum(record.procurement_put_line_ids.mapped('amount'))

            out_number = sum(record.procurement_outbound_line_ids.mapped('amount'))

            if put_number < out_number:
                raise ValidationError(f"库存不足，无法操作！")

            record.amount = put_number - out_number






