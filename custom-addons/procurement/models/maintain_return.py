from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaintainReturn(models.Model):
    _name = 'maintain_return'
    _description = '机修归还'
    # _rec_name = 'material_name'
    _order = "date desc"


    state = fields.Selection([
        ('草稿', '草稿'),
        ('已归还', '已归还'),
        ], string="状态", default="草稿")

    inventory = fields.Many2one("maintain_inventory", string="库存", required=True)


    inventory_number = fields.Float(string="库存数量", related="inventory.amount", store=True)

    date = fields.Date(string="归还日期", required=True)
    # serial_number = fields.Many2one("production_operation_ingredients_list", string="物品编号")
    material_name = fields.Char(string="物品名称", related="inventory.material_name", store=True)
    material_code = fields.Many2one("maintain_object_instance", string="物品编码", related="inventory.material_code", store=True)
    supplier_supplier_id = fields.Many2one("supplier_supplier", string="供应商", related="inventory.supplier_supplier_id", store=True)
    specification = fields.Char(string="规格", related="inventory.specification", store=True)
    department_name = fields.Char(string="归还部门", related="inventory.department_name", store=True)
    unit = fields.Char(string="单位", related="inventory.unit", store=True)
    amount = fields.Float(string="数量", required=True)


    manager = fields.Many2one('hr.employee', string="负责人", required=True)
    recipients_people = fields.Many2one('hr.employee', string="归还人", required=True)

    inventory_id = fields.Many2one("maintain_inventory", string="采购库存")



    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        if button_type == "confirm":
            action = {
                'name': "确认归还吗？",
                'view_mode': 'form',
                'res_model': 'maintain_return',
                'view_id': self.env.ref('procurement.maintain_return_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new'
            }
        elif button_type == "fallback":
            action = {
                'name': "确认回退吗？",
                'view_mode': 'form',
                'res_model': 'maintain_return',
                'view_id': self.env.ref('procurement.maintain_return_fallback_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
                'target': 'new'
            }
        return action
    
    # 确认回退
    def action_fallback(self):
        for record in self:
            if record.state == "已归还":

                record.state = "草稿"

                record.inventory_id = False

            else:
                raise ValidationError(f"发生错误。出 库状态异常！")

    # 确认出库
    def action_through(self):
        for record in self:
            if record.state == "草稿":
                
                record.inventory_id = record.inventory.id

                record.state = "已归还"
            
            else:
               raise ValidationError(f"发生错误。出库状态异常！")




    def write(self, vals):

        if self.state == "已领用":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"已领用的记录, 不可修改！。")


        res = super(MaintainReturn, self).write(vals)

        return res


    def unlink(self):

        for record in self:
            if record.state == "已归还":

                raise ValidationError(f"已经归还的记录, 不可删除！")

        res = super(MaintainReturn, self).unlink()

        return res