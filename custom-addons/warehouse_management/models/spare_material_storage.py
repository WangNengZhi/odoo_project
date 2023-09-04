from odoo import models, fields, api
from odoo.exceptions import ValidationError
from decimal import *

class SpareMaterialEnter(models.Model):
    _name = 'spare_material_enter'
    _description = '备用物料入库'
    _rec_name = 'odd_numbers'
    _order = "date desc"


    date = fields.Date(string="日期", required=True, default=fields.Datetime.now())
    state = fields.Selection([('草稿', '草稿'),('已入库', '已入库')], string="状态", default="草稿")
    odd_numbers = fields.Char(string="入库单号", required=True)

    material_coding = fields.Many2one("material_list", string="物料编号", required=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="material_coding.order_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="material_coding.style_number", store=True)

    supplier = fields.Char(string="供应商", related="material_coding.supplier", store=True)
    client_id = fields.Many2one("fsn_customer", related="material_coding.client_id", store=True, string="客户")
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    color = fields.Char(string="颜色", related="material_coding.color", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)
    reality_amount = fields.Float(string="验布数量")
    amount = fields.Float(string="数量", compute="set_money_sum", store=True)
    money_sum = fields.Float(string="金额", compute="set_money_sum", store=True, digits=(16, 5))

    @api.depends('spare_material_enter_line_ids', 'spare_material_enter_line_ids.amount', 'unit_price')
    def set_money_sum(self):
        for record in self:
            record.amount = sum(record.spare_material_enter_line_ids.mapped("amount"))
            record.money_sum = record.amount * record.unit_price


    remark = fields.Char(string="备注")
    consigner = fields.Char(string="发货人", required=True)
    select_consignee = fields.Many2one("hr.employee", string="收货人", required=True)

    spare_material_enter_line_ids = fields.One2many("spare_material_enter_line", "spare_material_enter_id", string="备用物料入库明细")


    spare_material_inventory_id = fields.Many2one("spare_material_inventory", string="备用面料库存")


    @api.constrains('spare_material_enter_line_ids', 'spare_material_enter_line_ids.batch_number')
    def _check_unique(self):
        for record in self:
            tem_list = record.spare_material_enter_line_ids.mapped("batch_number")
            if len(set(tem_list)) != len(tem_list):
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
        for record in self:

            inventory_obj = self.env["spare_material_inventory"].sudo().search([("material_coding", "=", record.material_coding.id)])
            if not inventory_obj:
                inventory_obj = self.env["spare_material_inventory"].sudo().create({"material_coding": record.material_coding.id})

            record.spare_material_inventory_id = inventory_obj.id
            record.state = "已入库" 
            record.set_procurement_complete()


    # 回退按钮
    def back_button(self):
        for record in self:

            record.state = "草稿"
            record.spare_material_inventory_id = False
            record.set_procurement_complete()


    def write(self, vals):
        if self.state == "已入库":
            if "state" in vals and len(vals) == 1:
                pass
            else:
                raise ValidationError(f"{self.odd_numbers}已经确认，不可修改！。")
        res = super(SpareMaterialEnter, self).write(vals)
        return res


    def unlink(self):
        if self.state == "已入库":
            raise ValidationError(f"{self.odd_numbers}已经确认，不可删除！。")
        res = super(SpareMaterialEnter, self).unlink()
        return res


class SpareMaterialEnterLine(models.Model):
    _name = 'spare_material_enter_line'
    _description = '备用物料入库明细'

    spare_material_enter_id = fields.Many2one("spare_material_enter", string="备用物料入库", ondelete="cascade")
    batch_number = fields.Integer(string="批次",  required=True)
    amount = fields.Float(string="数量")



class SpareMaterialInventory(models.Model):
    _name = 'spare_material_inventory'
    _description = '备用物料库存'
    _rec_name = 'material_coding'


    material_coding = fields.Many2one("material_list", string="物料编号")
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="material_coding.order_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="material_coding.style_number", store=True)

    supplier = fields.Char(string="供应商", related="material_coding.supplier", store=True)
    client_id = fields.Many2one("fsn_customer", related="material_coding.client_id", store=True, string="客户")
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    color = fields.Char(string="颜色", related="material_coding.color", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)

    amount = fields.Float(string="数量", compute="set_amount", store=True)
    money_sum = fields.Float(string="总价", compute="_set_money_sum", store=True, digits=(16, 5))

    spare_material_enter_ids = fields.One2many("spare_material_enter", "spare_material_inventory_id", string="备用物料入库")

    warehouse_bom_ids = fields.One2many("warehouse_bom", "spare_material_inventory_id", string="物料入库")


    # 计算库存数量
    @api.depends('spare_material_enter_ids', 'spare_material_enter_ids.amount', 'spare_material_enter_ids.state',\
                'warehouse_bom_ids', 'warehouse_bom_ids.amount', 'warehouse_bom_ids.state')
    def set_amount(self):
        for record in self:

            enter_amount = Decimal(str(sum(Decimal(str(i.amount)) for i in record.spare_material_enter_ids if i.state == "已入库")))
            out_amount = Decimal(str(sum(Decimal(str(i.amount)) for i in record.warehouse_bom_ids if i.state == "已入库")))
            inventory = enter_amount - out_amount
            if inventory < 0:
                raise ValidationError(f"库存数量不足不可操作！")
            record.amount = inventory


    # 计算总价格
    @api.depends('amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:
            record.money_sum = record.amount * record.unit_price


    def conversion_materials_stored(self):
        ''' 转用料入库'''
        action = {
            'name': "转为用料入库",
            'view_mode': 'form',
            'res_model': 'spare_material_inventory_wizard',
            'view_id': self.env.ref('warehouse_management.spare_material_inventory_wizard_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_spare_material_inventory_id': self.id,
            }
        }
        return action


class WarehouseBom(models.Model):
    """ 物料入库"""
    _inherit = 'warehouse_bom'

    spare_material_inventory_id = fields.Many2one("spare_material_inventory", string="备用物料库存", ondelete="restrict")
    spare_material_out_state = fields.Selection([('草稿', '草稿'),('已出库', '已出库')], string="备用出库状态", compute="set_spare_material_out_state", store=True)
    @api.depends("state")
    def set_spare_material_out_state(self):
        for record in self:
            if record.state == "草稿":
                record.spare_material_out_state = "草稿"
            
            if record.state == "已入库":
                record.spare_material_out_state = "已出库"




class SpareMaterialInventoryWizard(models.TransientModel):
    _name = 'spare_material_inventory_wizard'
    _description = '备用物料库存向导'

    date = fields.Date(string="日期")
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号')
    @api.onchange('order_id')
    def _onchange_style_number(self):

        self.style_number = False

        if self.order_id and not self.order_id.is_conceal:
            
            return {'domain': {'style_number': [('id', 'in', self.order_id.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
        
    style_number = fields.Many2one('ib.detail', string='款号')
    amount = fields.Float(string="数量")

    spare_material_inventory_id = fields.Many2one("spare_material_inventory", string="备用面料库存")

    responsible_person = fields.Many2one("hr.employee", string="操作人")

    def set_odd_numbers(self):
        spare_material_inventory_obj = self.env['spare_material_inventory'].sudo().browse(self.env.context.get("default_spare_material_inventory_id"))
        return [(i.odd_numbers, i.odd_numbers) for i in spare_material_inventory_obj.spare_material_enter_ids]
    odd_numbers = fields.Selection(selection=set_odd_numbers, string="单据编号")


    def confirm_conversion_materials_stored(self):
        ''' 确认转为用料'''

        self.env['warehouse_bom'].sudo().create({
            "date": self.date,
            "odd_numbers": self.odd_numbers,
            "material_coding": self.spare_material_inventory_id.material_coding.id,
            "order_id": self.order_id.id,
            "style_number": self.style_number.id,
            "spare_material_inventory_id": self.spare_material_inventory_id.id,
            "consigner": self.responsible_person.name,
            "select_consignee":  self.responsible_person.id,
            "warehouse_bom_line_ids": [(0, 0, {'batch_number': 1, 'amount': self.amount})]
        })