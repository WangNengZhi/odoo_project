from odoo import models, fields, api
import datetime


class FabricIngredientsSummary(models.Model):
    _inherit = 'fabric_ingredients_summary'
    ''' 面辅料采购汇总'''

    surface_accessories_loss_id = fields.Many2one("surface_accessories_loss", string="面辅料损耗表", compute="binding_surface_accessories_loss", store=True)

    @api.depends('material_code')
    def binding_surface_accessories_loss(self):
        for record in self:
            if record.material_code:
                
                surface_accessories_loss_obj = self.env['surface_accessories_loss'].sudo().search([("material_coding", "=", record.material_code.id)])
                if not surface_accessories_loss_obj:
                    surface_accessories_loss_obj = self.env['surface_accessories_loss'].sudo().create({
                        "order_number": record.order_id.id,
                        "style_number": record.style_number.id,
                        "material_coding": record.material_code.id
                    })
                
                record.surface_accessories_loss_id = surface_accessories_loss_obj.id


    @api.model
    def create(self, vals):
        res = super(FabricIngredientsSummary,self).create(vals)

        res.binding_surface_accessories_loss()

        return res



class WarehouseBomOutbound(models.Model):
    _inherit = 'warehouse_bom_outbound'
    ''' 辅料出库'''

    surface_accessories_loss_id = fields.Many2one("surface_accessories_loss", string="面辅料损耗表", compute="binding_surface_accessories_loss", store=True)

    @api.depends('material_coding', 'material_coding.material_code')
    def binding_surface_accessories_loss(self):
        for record in self:
            if record.material_coding.material_code:
                surface_accessories_loss_obj = self.env['surface_accessories_loss'].sudo().search([("material_coding", "=", record.material_coding.material_code.id)])
                if surface_accessories_loss_obj:
                    record.surface_accessories_loss_id = surface_accessories_loss_obj.id


    @api.model
    def create(self, vals):
        res = super(WarehouseBomOutbound,self).create(vals)

        res.binding_surface_accessories_loss()

        return res



class PlusMaterialOutbound(models.Model):
    _inherit = 'plus_material_outbound'
    ''' 面料出库'''

    surface_accessories_loss_id = fields.Many2one("surface_accessories_loss", string="面辅料损耗表", compute="binding_surface_accessories_loss", store=True)

    @api.depends('material_coding', 'material_coding.material_code')
    def binding_surface_accessories_loss(self):
        for record in self:
            if record.material_coding.material_code:
                surface_accessories_loss_obj = self.env['surface_accessories_loss'].sudo().search([("material_coding", "=", record.material_coding.material_code.id)])
                if surface_accessories_loss_obj:
                    record.surface_accessories_loss_id = surface_accessories_loss_obj.id


    @api.model
    def create(self, vals):
        res = super(PlusMaterialOutbound,self).create(vals)

        res.binding_surface_accessories_loss()

        return res


class SurfaceAccessoriesLoss(models.Model):
    _name = 'surface_accessories_loss'
    _description = '面辅料损耗表'
    _rec_name = 'style_number'
    _order = 'style_number desc'



    fabric_ingredients_summary_ids = fields.One2many("fabric_ingredients_summary", "surface_accessories_loss_id", string="面辅料汇总")

    purchase_quantity = fields.Float(string="采购数量", compute="set_purchase_quantity", store=True)
    @api.depends('fabric_ingredients_summary_ids', 'fabric_ingredients_summary_ids.amount', 'fabric_ingredients_summary_ids.event_type', 'fabric_ingredients_summary_ids.state')
    def set_purchase_quantity(self):
        for record in self:
            buy_quantity = sum(i.amount for i in record.fabric_ingredients_summary_ids if i.event_type == "采购" and i.state == "已采购")

            return_quantity = sum(i.amount for i in record.fabric_ingredients_summary_ids if i.event_type == "退还" and i.state == "已退还")

            record.purchase_quantity = buy_quantity - return_quantity


    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', compute="set_type", store=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related="order_number.processing_type", store=True)
    client_id = fields.Many2one("fsn_customer", string="客户", related="order_number.customer_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', compute="set_type", store=True)


    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    material_coding = fields.Many2one("material_code", string="物料编码", compute="set_type", store=True)
    material_name = fields.Char(string="物料名称", related="material_coding.material_name", store=True)
    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
        ], string="物料类型", compute="set_type", store=True)

    @api.depends('fabric_ingredients_summary_ids', 'fabric_ingredients_summary_ids.type', 'fabric_ingredients_summary_ids.order_id',\
        'fabric_ingredients_summary_ids.style_number', 'fabric_ingredients_summary_ids.material_code')
    def set_type(self):
        for record in self:
            if record.fabric_ingredients_summary_ids:

                record.type = record.fabric_ingredients_summary_ids[0].type
                record.order_number = record.fabric_ingredients_summary_ids[0].order_id.id
                record.style_number = record.fabric_ingredients_summary_ids[0].style_number.id
                record.material_coding = record.fabric_ingredients_summary_ids[0].material_code.id



    warehouse_bom_outbound_ids = fields.One2many("warehouse_bom_outbound", "surface_accessories_loss_id", string="辅料出库")
    plus_material_outbound_ids = fields.One2many("plus_material_outbound", "surface_accessories_loss_id", string="面料出库")

    cutting_machine_out_amount = fields.Float(string="裁床出库数", compute="set_out_amount", store=True)
    cutting_machine = fields.Float(string="裁床", compute="set_loss_data", store=True)

    workshop_out_amount = fields.Float(string="车间出库数", compute="set_out_amount", store=True)
    workshop = fields.Float(string="车间", compute="set_loss_data", store=True)

    posterior_channel_out_amount = fields.Float(string="后道出库数", compute="set_out_amount", store=True)
    posterior_channel = fields.Float(string="后道", compute="set_loss_data", store=True)

    warehouse_amount = fields.Float(string="仓库出库数", compute="set_out_amount", store=True)
    warehouse = fields.Float(string="仓库", compute="set_loss_data", store=True)

    @api.depends('warehouse_bom_outbound_ids', 'warehouse_bom_outbound_ids.amount', 'warehouse_bom_outbound_ids.receive_department',\
        'plus_material_outbound_ids', 'plus_material_outbound_ids.amount', 'plus_material_outbound_ids.receive_department')
    def set_out_amount(self):

        receive_department_domain_list = ["车间", "缝纫", "整件"]
        department_id_list = []

        for i in receive_department_domain_list:
            department_objs = self.env['hr.department'].search([("name", "like", i)])
            department_id_list.extend(department_objs.ids)

        for record in self:
            if record.type == "面料":
                record.cutting_machine_out_amount = sum(i.amount for i in record.plus_material_outbound_ids if i.receive_department.name == "裁床部")
                record.posterior_channel_out_amount = sum(i.amount for i in record.plus_material_outbound_ids if i.receive_department.name == "后道部")
                record.warehouse_amount = sum(i.amount for i in record.plus_material_outbound_ids if i.receive_department.name == "仓储部")
                record.workshop_out_amount = sum(i.amount for i in record.plus_material_outbound_ids if i.receive_department.id in department_id_list)
            else:
                record.cutting_machine_out_amount = sum(i.amount for i in record.warehouse_bom_outbound_ids if i.receive_department.name == "裁床部")  
                record.posterior_channel_out_amount = sum(i.amount for i in record.warehouse_bom_outbound_ids if i.receive_department.name == "后道部") 
                record.warehouse_amount = sum(i.amount for i in record.warehouse_bom_outbound_ids if i.receive_department.name == "仓储部")
                record.workshop_out_amount = sum(i.amount for i in record.warehouse_bom_outbound_ids if i.receive_department.id in department_id_list)

    @api.depends('purchase_quantity','cutting_machine_out_amount', 'posterior_channel_out_amount', 'warehouse_amount', 'workshop_out_amount')
    def set_loss_data(self):
        for record in self:
            if record.cutting_machine_out_amount:
                record.cutting_machine = record.cutting_machine_out_amount - record.purchase_quantity
            else:
                record.cutting_machine = 0
            if record.posterior_channel_out_amount:
                record.posterior_channel = record.posterior_channel_out_amount - record.purchase_quantity
            else:
                record.posterior_channel = 0
            if record.warehouse_amount:
                record.warehouse = record.warehouse_amount - record.purchase_quantity
            else:
                record.warehouse = 0
            if record.workshop_out_amount:
                record.workshop = record.workshop_out_amount - record.purchase_quantity
            else:
                record.workshop = 0


    


