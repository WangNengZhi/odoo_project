from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductionOperationIngredientsEnter(models.Model):
    _name = 'production_operation_ingredients_enter'
    _description = '仓库生产工具(入库)'
    _rec_name = 'odd_numbers'
    _order = "date desc"


    date = fields.Date(string="日期", required=True, default=fields.Datetime.now())
    state = fields.Selection([('草稿', '草稿'),('已入库', '已入库')], string="状态", default="草稿")
    odd_numbers = fields.Char(string="入库单号", required=True)


    material_coding = fields.Many2one("production_operation_ingredients_list", string="物料编号", required=True)
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    # supplier_supplier_id = fields.Many2one("supplier_supplier", related="material_coding.supplier_supplier_id", store=True, string="供应商")
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)

    amount = fields.Float(string="入库数量", required=True)
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True, digits=(16, 5))

    consigner = fields.Char(string="发货方", required=True)
    consignee = fields.Many2one("hr.employee", string="收货人", required=True)

    remark = fields.Char(string="备注")


    production_operation_ingredients_inventory_id = fields.Many2one("production_operation_ingredients_inventory", string="库存id")



    # 计算总价格
    @api.depends('unit_price', 'amount')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price



    def affirm_enter(self):
        inventory_objs = self.env["production_operation_ingredients_inventory"].sudo().search([
            ("material_coding", "=", self.material_coding.id)
        ])
        if inventory_objs:

            self.production_operation_ingredients_inventory_id = inventory_objs.id
            self.production_operation_ingredients_inventory_id.amount = self.production_operation_ingredients_inventory_id.amount + self.amount

        else:
            new_obj = inventory_objs.create({
                "material_coding": self.material_coding.id,
                "amount": self.amount,
            })

            self.production_operation_ingredients_inventory_id = new_obj


        self.state = "已入库"



    def write(self, vals):

        if self.state == "已入库":

            raise ValidationError(f"{self.odd_numbers}已经确认，不可修改。")

        res = super(ProductionOperationIngredientsEnter, self).write(vals)



        return res


    def unlink(self):

        for record in self:

            if record.state == "已入库":

                if record.production_operation_ingredients_inventory_id.production_operation_ingredients_outbound_ids:
                    # 如果入库数量小于等于库存数
                    if record.amount <= record.production_operation_ingredients_inventory_id.amount:
                        record.production_operation_ingredients_inventory_id.amount = record.production_operation_ingredients_inventory_id.amount - record.amount
                    else:
                        raise ValidationError(f"{self.odd_numbers}库存数不足，不可删除")
                else:
                    record.production_operation_ingredients_inventory_id.amount = record.production_operation_ingredients_inventory_id.amount - record.amount

        res = super(ProductionOperationIngredientsEnter, self).unlink()

        return res