from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaintainInventory(models.Model):
    _name = 'maintain_inventory'
    _description = '机修库存'
    _rec_name = 'material_name'
    _order = "write_date desc"



    # date = fields.Date(string="日期", required=True)
    material_code = fields.Many2one("maintain_object_instance", string="物品编码")
    material_name = fields.Char(string="物品名称", store=True, compute="set_material_info")
    department_name = fields.Char(string="采购部门", store=True, compute="set_material_info")
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", store=True, compute="set_material_info")
    specification = fields.Char(string="规格", store=True, compute="set_material_info")
    unit = fields.Char(string="单位", store=True, compute="set_material_info")
    @api.depends('material_code')
    def set_material_info(self):
        for record in self:
            if record.material_code:
                record.material_name = record.material_code.material_name
                record.department_name = record.material_code.department_name
                record.specification = record.material_code.specification
                record.supplier_supplier_id = record.material_code.supplier_supplier_id.id
                record.unit = record.material_code.unit

                
    put_amount = fields.Float(string="入库数量")
    recipients_amount = fields.Float(string="领用数量")
    return_amonut = fields.Float(string="归还数量")

    amount = fields.Float(string="库存数量", store=True, compute="set_amount")


    maintain_procurement_line_ids = fields.One2many("maintain_procurement", "inventory_id", string="采购明细（旧）")

    maintain_put_line_ids = fields.One2many("maintain_put", "inventory_id", string="入库明细")

    maintain_recipients_line_ids = fields.One2many("maintain_recipients", "inventory_id", string="领用明细")

    maintain_return_line_ids = fields.One2many("maintain_return", "inventory_id", string="归还明细")


    # 计算入库数量
    @api.depends('maintain_put_line_ids', 'maintain_recipients_line_ids', 'maintain_return_line_ids')
    def set_amount(self):
        for record in self:

            # 入库明细 + 归还明细
            put_number = sum(record.maintain_put_line_ids.mapped('amount')) + sum(record.maintain_return_line_ids.mapped('amount'))

            out_number = sum(record.maintain_recipients_line_ids.mapped('amount'))

            if put_number < out_number:

                if put_number == 0 and record.amount > 0:
                    put_number = record.amount
                else:
                    raise ValidationError(f"库存不足，无法操作！")

            record.amount = put_number - out_number