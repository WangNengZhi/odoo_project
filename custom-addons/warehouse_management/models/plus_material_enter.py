from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PlusMaterialEnter(models.Model):
    _name = 'plus_material_enter'
    _description = '仓库布料单(入库)'
    _rec_name = 'odd_numbers'
    _order = "date desc"


    date = fields.Date(string="日期", required=True, default=fields.Datetime.now())
    state = fields.Selection([('草稿', '草稿'),('已入库', '已入库')], string="状态", default="草稿")
    odd_numbers = fields.Char(string="入库单号", required=True)

    material_coding = fields.Many2one("plus_material_list", string="面料编号", required=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号')
    style_number = fields.Many2one('ib.detail', string='款号')
    @api.onchange('material_coding')
    def set_style_number_info(self):
        for record in self:
            if record.material_coding:
                record.order_id = record.material_coding.order_id.id
                record.style_number = record.material_coding.style_number.id

    supplier = fields.Char(string="供应商", related="material_coding.supplier", store=True)
    client = fields.Char(string="客户", related="material_coding.client", store=True)
    client_id = fields.Many2one("fsn_customer", related="material_coding.client_id", store=True, string="客户")
    material_name = fields.Char(string="面料名称", related="material_coding.material_name", store=True)
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    color = fields.Char(string="颜色", related="material_coding.color", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)

    amount = fields.Float(string="数量", compute="_set_money_sum", store=True)
    reality_amount = fields.Float(string="验布数量")
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True, digits=(16, 5))
    remark = fields.Char(string="备注")
    consigner = fields.Char(string="发货人", required=True)
    consignee = fields.Char(string="收货人")
    select_consignee = fields.Many2one("hr.employee", string="收货人", required=True)

    plus_material_enter_line_ids = fields.One2many("plus_material_enter_line", "plus_material_enter_id", string="仓库布料单明细")


    plus_material_inventory_id = fields.Many2one("plus_material_inventory", string="库存id", ondelete="restrict")


    @api.constrains('plus_material_enter_line_ids', 'plus_material_enter_line_ids.batch_number')
    def _check_unique(self):

        for record in self:

            tem_list = []

            for line in record.plus_material_enter_line_ids:
                tem_list.append(line.batch_number)

            if len(set(tem_list)) == len(tem_list):
                pass
            else:
                raise ValidationError(f"明细表中批次重复了！")



    # 设置采购完成
    def set_procurement_complete(self):
        for record in self:
            if record.material_coding.material_code:

                fip_obj = self.env["fabric_ingredients_procurement"].sudo().search([("material_code", "=", record.material_coding.material_code.id)])
                if fip_obj:

                    if len(fip_obj) > 1:
                        raise ValidationError(f"发生异常，采购中存在相同物料编号的记录！")

                    if not fip_obj.state == "已采购":

                        objs = self.search([("material_coding", "=", record.material_coding.id), ("state", "=", "已入库")])
                        amount_list = objs.mapped("amount")

                        if sum(amount_list) == fip_obj.amount:
                            fip_obj.state = "已采购"
                        elif sum(amount_list) > fip_obj.amount:
                            raise ValidationError(f"入库数量大于采购数量。请检查或联系相关人员！")
                        elif sum(amount_list) < fip_obj.amount:
                            fip_obj.state = "待采购"


    # 确认入库
    def affirm_enter(self):

        inventory_obj = self.env["plus_material_inventory"].sudo().search([
            ("material_coding", "=", self.material_coding.id),
            ("order_id", "=", self.order_id.id),
            ("style_number", "=", self.style_number.id)
        ])
        if not inventory_obj:
            inventory_obj = inventory_obj.create({
                "material_coding": self.material_coding.id,
                "order_id": self.order_id.id,
                "style_number": self.style_number.id
            })

        self.plus_material_inventory_id = inventory_obj.id

        self.state = "已入库"
        self.set_procurement_complete()


    # 回退按钮
    def back_button(self):
        for record in self:
            if record.plus_material_inventory_id.amount < record.amount:

                raise ValidationError(f"库存数量少于入库数量，不可退回！")
                
            else:

                record.state = "草稿"
                record.plus_material_inventory_id = False
                record.set_procurement_complete()
    

    # 计算总价格
    @api.depends('plus_material_enter_line_ids', 'plus_material_enter_line_ids.amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:
            tem_amount = 0
            for line in record.plus_material_enter_line_ids:
                tem_amount = tem_amount + line.amount
            
            record.amount = tem_amount

            record.money_sum = record.amount * record.unit_price







    def write(self, vals):

        if self.state == "已入库":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"{self.odd_numbers}已经确认，不可修改！。")

        res = super(PlusMaterialEnter, self).write(vals)

        return res


    def unlink(self):
        if self.state == "已入库":


                
            raise ValidationError(f"{self.odd_numbers}已经确认，不可删除！。")

        res = super(PlusMaterialEnter, self).unlink()

        return res



class PlusMaterialEnterLine(models.Model):
    _name = 'plus_material_enter_line'
    _description = '仓库布料单明细'

    plus_material_enter_id = fields.Many2one("plus_material_enter", string="仓库布料单id", ondelete="cascade")
    batch_number = fields.Integer(string="批次",  required=True)
    amount = fields.Float(string="数量")