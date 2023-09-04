
from odoo import api, fields, models
from odoo.exceptions import ValidationError




class FabricIngredientsProcurement(models.Model):
    """ 继承面辅料采购"""
    _inherit = 'fabric_ingredients_procurement'


    # 查询入库记录
    def search_put_storage(self):
        for record in self:

            context = {
                'create': False,
                'edit': False,
                'delete': False,
                "show_button": True,
                "procurement_id": record.id,
                "procurement_model_name": record._name,
            }
            def filtering_methods(obj):
                
                if obj.material_coding.material_code:
                    fabric_ingredients_procurement_objs = self.env["fabric_ingredients_procurement"].sudo().search([
                        ("material_code", "=", obj.material_coding.material_code.id)
                    ])
                    return not fabric_ingredients_procurement_objs

            if record.type == "面料":

                plus_material_enter_objs = self.env["plus_material_enter"].sudo().search([
                    ("order_id", "=", record.order_id.id),
                    ("style_number", "=", record.style_number.id),
                ])

                plus_material_enter_objs_ids = [obj.id for obj in filter(filtering_methods, plus_material_enter_objs)]


                action = {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'name': "选择面料入库记录",
                    'res_model': 'plus_material_enter',
                    'target': 'new',
                    'domain': [("id", "in", plus_material_enter_objs_ids)],
                    'context': context,
                }

                
            else:
                warehouse_bom_objs = self.env["warehouse_bom"].sudo().search([
                    ("order_id", "=", record.order_id.id),
                    ("style_number", "=", record.style_number.id),
                ])

                warehouse_bom_objs_ids = [obj.id for obj in filter(filtering_methods, warehouse_bom_objs)]
                action = {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'name': "选择辅料入库记录",
                    'res_model': 'warehouse_bom',
                    'target': 'new',
                    'domain': [("id", "in", warehouse_bom_objs_ids)],
                    'context': context,
                }


            return action

    # 生成物料编码
    def generate_material_code(self):
        for record in self:

            if record.material_code:
                raise ValidationError(f"已经存在物料编码！不可生成！")
            else:

                material_code_obj = self.material_code.sudo().create({
                    "date": fields.datetime.now(),
                })
                record.material_code = material_code_obj.id
                material_code_obj.procurement_id = record.id


class WarehouseBom(models.Model):
    """ 辅料料入库"""
    _inherit = 'warehouse_bom'


    def choose_material_code(self):

        material_coding_objs = self.mapped("material_coding")

        if len(material_coding_objs) != 1:
            raise ValidationError(f"不可同时选择不同物料编码的记录！")
        else:
            procurement_id = self._context.get("procurement_id")
            procurement_model_name = self._context.get("procurement_model_name")

            procurement_obj = self.env[procurement_model_name].sudo().browse(procurement_id)
            
            procurement_obj.sudo().write({
                "material_code": material_coding_objs.material_code.id,
                "material_name": material_coding_objs.material_name,
                "supplier_supplier_id": self.env["supplier_supplier"].sudo().search([("supplier_name", "=", material_coding_objs.supplier)], limit=1).id,
                "specification": material_coding_objs.specification,
                "unit_price": material_coding_objs.unit_price,
                "unit": material_coding_objs.unit,
                "amount": sum(self.mapped("amount"))
            })

            procurement_obj.material_code.sudo().write({
                "type": "待采购"
            })

class PlusMaterialEnter(models.Model):
    """ 面料入库"""
    _inherit = 'plus_material_enter'


    def choose_material_code(self):
        material_coding_objs = self.mapped("material_coding")
        if len(material_coding_objs) != 1:
            raise ValidationError(f"不可同时选择不同物料编码的记录！")
        else:
            procurement_id = self._context.get("procurement_id")
            procurement_model_name = self._context.get("procurement_model_name")

            procurement_obj = self.env[procurement_model_name].sudo().browse(procurement_id)
            
            procurement_obj.sudo().write({
                "material_code": material_coding_objs.material_code.id,
                "material_name": material_coding_objs.material_name,
                "supplier_supplier_id": self.env["supplier_supplier"].sudo().search([("supplier_name", "=", material_coding_objs.supplier)], limit=1).id,
                "specification": material_coding_objs.specification,
                "unit_price": material_coding_objs.unit_price,
                "unit": material_coding_objs.unit,
                "amount": sum(self.mapped("amount"))
            })

            procurement_obj.material_code.sudo().write({
                "type": "待采购"
            })