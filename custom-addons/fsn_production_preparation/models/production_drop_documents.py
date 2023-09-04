from odoo import api, fields, models

class ProductionDropDocuments(models.Model):
    _name = 'production_drop_documents'
    _description = '生产下料单'
    _rec_name = 'style_number'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    style_number = fields.Many2one("ib.detail", string="款号", required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
    style = fields.Char(string="款式")
    client_id = fields.Many2one("fsn_customer", string="客户")
    outsource_plant_id = fields.Many2one("outsource_plant", string="外发工厂", required=True)
    date_delivery = fields.Date(string="交货日期", required=True)


    production_drop_documents_size_line_ids = fields.One2many("production_drop_documents_size_line", "production_drop_documents_id", string="生产下料单尺码明细")
    total_number = fields.Integer(string="总件数", compute="set_total_number", store=True)
    @api.depends("production_drop_documents_size_line_ids", "production_drop_documents_size_line_ids.number")
    def set_total_number(self):
        for record in self:
            
            record.total_number = sum(record.production_drop_documents_size_line_ids.mapped("number"))


    production_drop_documents_material_line_ids = fields.One2many("production_drop_documents_material_line", "production_drop_documents_id", string="物料明细")




class ProductionDropDocumentsSizeLine(models.Model):
    _name = 'production_drop_documents_size_line'
    _description = '生产下料单尺码明细'


    production_drop_documents_id = fields.Many2one("production_drop_documents", string="生产下料单", ondelete="cascade")
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer(string="件数")



class ProductionDropDocumentsMaterialLine(models.Model):
    _name = 'production_drop_documents_material_line'
    _description = '生产下料单物料明细'


    production_drop_documents_id = fields.Many2one("production_drop_documents", string="生产下料单", ondelete="cascade")
    style_number_base = fields.Char(string="款号前缀", related="production_drop_documents_id.style_number.style_number_base", store=True)
    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
        ], string="物料类型", required=True)

    material_id = fields.Many2one("sheet_materials_line", string="物料选择", required=True)

    @api.onchange('type')
    def onchange_material_id(self):
        self.material_id = False
        if self.type:
            
            return {'domain': {'material_id': [("type", "=", self.type), ("style_number_base", "=", self.style_number_base)]}}
        else:
            return {'domain': {'material_id': []}}

    # , domain="[('sheet_materials_id.style_number_base', '=', production_drop_documents_id.style_number.style_number_base)]"
    color = fields.Char(string="颜色")
    specifications = fields.Char(string="规格", required=True)
    quantity_per_unit = fields.Float(string="单件用量")
    unit_id = fields.Many2one("fsn_unit", string="单位", required=True)

    @api.onchange("material_id")
    def set_material_info(self):
        for record in self:
            if record.material_id:
                record.specifications = record.material_id.material_specifications
                record.quantity_per_unit = record.material_id.single_dosage
                record.unit_id = record.material_id.unit_id.id

            else:
                record.color = False
                record.specifications = False
                record.quantity_per_unit = False
                record.unit_id = False
    planned_dosage = fields.Float(string="计划数量", compute="set_planned_dosage", store=True)
    @api.depends("production_drop_documents_id", 'production_drop_documents_id.total_number', 'quantity_per_unit')
    def set_planned_dosage(self):
        for record in self:
            if record.type == "面料":
                record.planned_dosage = (record.production_drop_documents_id.total_number * record.quantity_per_unit) * 1.05
            else:
                record.planned_dosage = record.production_drop_documents_id.total_number * record.quantity_per_unit
    actual_delivery_quantity = fields.Float(string="实发数量")



