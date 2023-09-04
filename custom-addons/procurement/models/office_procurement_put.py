from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OfficeProcurementPut(models.Model):
    _name = 'office_procurement_put'
    _description = '办公室采购入库'
    _rec_name = 'material_name'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    state = fields.Selection([
        ('草稿', '草稿'),
        ('确认', '确认'),
        ], string="状态", default="草稿")


    material_name = fields.Many2one("office_procurement_enter", string="物品名称", domain=[('state', '=', '待采购')])
    material_code = fields.Many2one("office_object_instance", string="物品编码", related="material_name.material_code", store=True)
    # material_name = fields.Char(string="物品名称", store=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", related="material_name.supplier_supplier_id", store=True, string="供应商")
    specification = fields.Char(string="规格", related="material_name.specification", store=True)

    # unit_price = fields.Float(string="单价", store=True)
    unit = fields.Char(string="单位", related="material_name.unit", store=True)

    amount = fields.Float(string="数量", related="material_name.amount", store=True)
    # money_sum = fields.Float(string="金额", store=True)

    admin_department = fields.Many2one("hr.department", string="部门", required=True)
    manager = fields.Many2one('hr.employee', string="负责人", required=True)

    remark = fields.Char(string="备注")


    procurement_inventory_id = fields.Many2one("office_procurement_inventory", string="库存id")



    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.material_name.material_name}({record.material_code.material_code})"
            result.append((record.id, rec_name))
        return result




    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        if button_type == "confirm":
            action = {
                'name': "确认通过吗？",
                'view_mode': 'form',
                'res_model': 'office_procurement_put',
                'view_id': self.env.ref('procurement.office_procurement_put_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new'
            }
        elif button_type == "fallback":
            action = {
                'name': "确认回退吗？",
                'view_mode': 'form',
                'res_model': 'office_procurement_put',
                'view_id': self.env.ref('procurement.office_procurement_put_fallback_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new'
            }
        return action
    
    # 确认回退
    def action_fallback(self):
        for record in self:
            if record.state == "确认":

                record.state = "草稿"

                record.procurement_inventory_id = False


                record.material_name.state = "待采购"
            else:
                raise ValidationError(f"发生错误。入库状态异常！")

    # 确认入库
    def action_through(self):
        for record in self:
            
            if record.material_name.state == "待采购":

                inventory_obj = record.procurement_inventory_id.sudo().search([("material_code", "=", record.material_code.id)])
                if inventory_obj:
                    pass
                else:
                    inventory_obj = record.procurement_inventory_id.sudo().create({
                        "material_code": record.material_code.id
                    })

                record.procurement_inventory_id = inventory_obj.id

                record.state = "确认"

                record.material_name.state = "已采购"
            
            else:
                raise ValidationError(f"采购订单状态错误,无法入库！")




    def write(self, vals):


        if self.state == "确认":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"已经确认的记录, 不可修改！。")


        res = super(OfficeProcurementPut, self).write(vals)

        return res


    def unlink(self):

        for record in self:
            if record.state == "确认":

                raise ValidationError(f"已经确认的记录, 不可删除！")

        res = super(OfficeProcurementPut, self).unlink()

        return res