from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductionOperationIngredientsOutbound(models.Model):
    _name = 'production_operation_ingredients_outbound'
    _description = '仓库生产工具(出库)'
    _rec_name = 'material_name'
    _order = "date desc"


    date = fields.Date(string="日期", required=True, default=fields.Datetime.now())
    state = fields.Selection([('草稿', '草稿'),('已出库', '已出库')], string="状态", default="草稿")
    odd_numbers = fields.Char(string="出库单号", required=True)
    supplier = fields.Char(string="班组", required=True)

    inventory = fields.Many2one("production_operation_ingredients_inventory", string="库存", required=True)
    material_coding = fields.Many2one("production_operation_ingredients_list", string="物料编码", related="inventory.material_coding", store=True)
    inventory_number = fields.Float(string="库存数量", related="inventory.amount", store=True)


    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    # supplier_supplier_id = fields.Many2one("supplier_supplier", related="material_coding.supplier_supplier_id", store=True, string="供应商")
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))

    amount = fields.Float(string="数量", required=True)
    money_sum = fields.Float(string="金额", digits=(16, 5))
    remark = fields.Char(string="备注")


    consignee = fields.Many2one("hr.employee", string="收货人", required=True)
    consigner = fields.Many2one("hr.employee", string="发货人", required=True)

    production_operation_ingredients_inventory_id = fields.Many2one("production_operation_ingredients_inventory", string="库存id")




    # 确认出库
    def affirm_outbound(self):

        if self.amount > self.inventory.amount:
            raise ValidationError(f"出库数量不能大于库存数量!")


        # 库存数量减去出库的数量
        self.inventory.amount = self.inventory.amount - self.amount

        # 添加到库存表中的出库明细中
        self.production_operation_ingredients_inventory_id = self.inventory.id

        self.state = "已出库"


    def write(self, vals):

        if self.state == "已出库":
            raise ValidationError(f"{self.odd_numbers}已经确认，不可修改或者删除。")

        res = super(ProductionOperationIngredientsOutbound, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "已出库":

                record.production_operation_ingredients_inventory_id.amount = record.production_operation_ingredients_inventory_id.amount + record.amount

        res = super(ProductionOperationIngredientsOutbound, self).unlink()

        return res