
from odoo import api, fields, models
from odoo.exceptions import ValidationError




class FabricIngredientsRefund(models.Model):
    """ 继承面辅料退回"""
    _inherit = 'fabric_ingredients_refund'
    



class PlusMaterialInventory(models.Model):
    """ 面料库存"""
    _inherit = 'plus_material_inventory'



    def create_fabric_ingredients_refund(self):
        try:
            self.ensure_one()
        except Exception as e:
            raise ValidationError(f"{e}请选择一个库存记录！")
        else:
            
            self.env["fabric_ingredients_refund"].sudo().create({
                "plus_material_inventory_id": self.id,
                "date": fields.Datetime.now(),
                "material_code": self.material_coding.material_code.id,
                "fabric_ingredients_procurement_id": self.env["fabric_ingredients_procurement"].sudo().search([("material_code", "=", self.material_coding.material_code.id)]).id
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




class PlusMaterialOutbound(models.Model):
    """ 面料出库"""
    _inherit = 'plus_material_outbound'


    def affirm_detection_refund(self):
        fabric_ingredients_refund_obj = self.env["fabric_ingredients_refund"].sudo().search([
            ("material_code", "=",  self.material_coding.material_code.id),
            ("state", "=", "待退还")
        ])
        if fabric_ingredients_refund_obj:

            if fabric_ingredients_refund_obj.amount == self.amount:
                fabric_ingredients_refund_obj.state = "已退还"
            else:
                raise ValidationError(f"退还物料数量异常，无法出库！")


    def affirm_outbound(self):

        res = super(PlusMaterialOutbound, self).affirm_outbound()

        self.affirm_detection_refund()

        return res



    def back_detection_refund(self):
        fabric_ingredients_refund_obj = self.env["fabric_ingredients_refund"].sudo().search([
            ("material_code", "=",  self.material_coding.material_code.id),
            ("amount", "=", self.amount),
            ("state", "=", "已退还")
        ])
        if fabric_ingredients_refund_obj:

            fabric_ingredients_refund_obj.state = "待退还"



    def back_button(self):

        res = super(PlusMaterialOutbound, self).back_button()

        self.back_detection_refund()

        return res


class WarehouseBomInventory(models.Model):
    """ 辅料库存"""
    _inherit = 'warehouse_bom_inventory'

    def create_fabric_ingredients_refund(self):
        try:
            self.ensure_one()
        except Exception as e:
            raise ValidationError(f"{e}请选择一个库存记录！")
        else:

            self.env["fabric_ingredients_refund"].sudo().create({
                "warehouse_bom_inventory_id": self.id,
                "date": fields.Datetime.now(),
                "material_code": self.material_coding.material_code.id,
                "fabric_ingredients_procurement_id": self.env["fabric_ingredients_procurement"].sudo().search([("material_code", "=", self.material_coding.material_code.id)]).id
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



class WarehouseBomOutbound(models.Model):
    """ 物料出库"""
    _inherit = 'warehouse_bom_outbound'



    def affirm_detection_refund(self):
        fabric_ingredients_refund_obj = self.env["fabric_ingredients_refund"].sudo().search([
            ("material_code", "=",  self.material_coding.material_code.id),
            ("state", "=", "待退还")
        ])
        if fabric_ingredients_refund_obj:
            if fabric_ingredients_refund_obj.amount == self.amount:

                fabric_ingredients_refund_obj.state = "已退还"

            else:
                raise ValidationError(f"退还物料数量异常，无法出库！")
        
        


    def affirm_outbound(self):

        res = super(WarehouseBomOutbound, self).affirm_outbound()

        self.affirm_detection_refund()

        return res



    def back_detection_refund(self):
        fabric_ingredients_refund_obj = self.env["fabric_ingredients_refund"].sudo().search([
            ("material_code", "=",  self.material_coding.material_code.id),
            ("amount", "=", self.amount),
            ("state", "=", "已退还")
        ])
        if fabric_ingredients_refund_obj:
            fabric_ingredients_refund_obj.state = "待退还"



    def back_button(self):

        res = super(WarehouseBomOutbound, self).back_button()

        self.back_detection_refund()

        return res


