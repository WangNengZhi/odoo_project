
from odoo import api, fields, models


class PlusMaterialOutbound(models.Model):
    _inherit = 'plus_material_outbound'
    ''' 继承面料出库'''

    production_drop_documents_material_line_id = fields.Many2one("production_drop_documents_material_line", string="生产下料单物料明细")



    def set_production_drop_documents_material_line(self):
        for record in self:
            
            obj = self.env['production_drop_documents'].sudo().search([("order_number", "=", record.order_id.id), ("style_number", "=", record.style_number.id)])

            if obj:
                material_line_obj = obj.production_drop_documents_material_line_ids.filtered(lambda x: x.type == "面料" and x.material_id.material_name == record.material_name)
                
                if material_line_obj:
                    record.production_drop_documents_material_line_id = material_line_obj.id

    @api.model
    def create(self, vals):

        res = super(PlusMaterialOutbound, self).create(vals)

        res.sudo().set_production_drop_documents_material_line()

        return res


class WarehouseBomOutbound(models.Model):
    _inherit = 'warehouse_bom_outbound'
    ''' 继承辅料出库'''

    production_drop_documents_material_line_id = fields.Many2one("production_drop_documents_material_line", string="生产下料单物料明细")


    def set_production_drop_documents_material_line(self):
        for record in self:
            
            obj = self.env['production_drop_documents'].sudo().search([("order_number", "=", record.order_id.id), ("style_number", "=", record.style_number.id)])

            if obj:
                material_line_obj = obj.production_drop_documents_material_line_ids.filtered(lambda x: x.type != "面料" and x.material_id.material_name == record.material_name)
                
                if material_line_obj:
                    record.production_drop_documents_material_line_id = material_line_obj.id

    @api.model
    def create(self, vals):

        res = super(WarehouseBomOutbound, self).create(vals)

        res.sudo().set_production_drop_documents_material_line()

        return res


class ProductionDropDocumentsMaterialLine(models.Model):
    _inherit = 'production_drop_documents_material_line'
    ''' 继承生产下料单物料明细'''

    plus_material_outbound_ids = fields.One2many("plus_material_outbound", "production_drop_documents_material_line_id", string="面料出库")
    warehouse_bom_outbound_ids = fields.One2many("warehouse_bom_outbound", "production_drop_documents_material_line_id", string="物料出库")

    actual_delivery_quantity = fields.Float(string="实发数量", compute="set_actual_delivery_quantity", store=True)

    @api.depends('type', 'plus_material_outbound_ids', 'plus_material_outbound_ids.amount', 'warehouse_bom_outbound_ids.amount')
    def set_actual_delivery_quantity(self):
        for record in self:
            if record.type == "面料":
                record.actual_delivery_quantity = sum(record.plus_material_outbound_ids.filtered(lambda x: x.state != "已出库").mapped("amount"))
            else:
                record.actual_delivery_quantity = sum(record.warehouse_bom_outbound_ids.filtered(lambda x: x.state != "已出库").mapped("amount"))
