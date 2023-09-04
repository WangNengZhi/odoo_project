from odoo import api, fields, models


class SaleProLine(models.Model):
    """ 继承销售订单明细"""
    _inherit = 'sale_pro_line'


    def generate_prenatal_preparation_progress(self):
        for record in self:
            prenatal_preparation_progress_obj = self.env['prenatal_preparation_progress'].sudo().search([("sale_pro_line_id", "=", record.id)])
            if not prenatal_preparation_progress_obj:
                self.env['prenatal_preparation_progress'].sudo().create({"sale_pro_line_id": record.id})


    @api.model
    def create(self, vals):

        res = super(SaleProLine, self).create(vals)

        res.sudo().generate_prenatal_preparation_progress()

        return res


class PrenatalPreparationProgress(models.Model):
    _name = 'prenatal_preparation_progress'
    _description = '产前准备进度表'
    _rec_name = 'order_date'
    _order = "order_date desc"

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="销售订单明细", ondelete='cascade')

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', related="sale_pro_line_id.sale_pro_id", store=True)
    client_id = fields.Many2one("fsn_customer", string="客户", related="order_number.customer_id", store=True)
    order_date = fields.Date(string="下单日期", related="order_number.date", store=True)
    contract_date = fields.Date(string="合同日期", related="order_number.customer_delivery_time", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="sale_pro_line_id.style_number", store=True)
    is_sample_dress = fields.Boolean(string="样衣")
    is_platemaking = fields.Boolean(string="样板")
    is_process = fields.Boolean(string="工时工序")
    is_template = fields.Boolean(string="模板")
    is_process_sheet = fields.Boolean(string="工艺单")
    is_unit_consumption = fields.Boolean(string="单件用量")
    is_surface_material = fields.Boolean(string="面料采购")
    is_auxiliary_material = fields.Boolean(string="辅料采购")
    is_cutting_bed = fields.Boolean(string="裁床")
    is_all_complete = fields.Boolean(string="是否全部完成", compute="set_is_all_complete", store=True)
    @api.depends("is_sample_dress", "is_platemaking", "is_process", "is_template", "is_process_sheet", "is_unit_consumption", "is_surface_material", "is_cutting_bed")
    def set_is_all_complete(self):
        for record in self:
            if record.is_sample_dress and\
                record.is_platemaking and\
                    record.is_process and \
                        record.is_template and\
                            record.is_process_sheet and \
                                record.is_unit_consumption and \
                                    record.is_surface_material and\
                                        record.is_cutting_bed:
                record.is_all_complete = True
            else:
                record.is_all_complete = False


    def examine_is_sample_dress(self):
        ''' 检查样衣'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_sample_dress", "=", False)])
        for obj in objs:
            th_per_management_objs = self.env['th_per_management'].sudo().search([
                ("style_number.style_number_base_id", "=", obj.style_number.style_number_base_id.id),   # 款号前缀
                ("is_supervisor_approval", "=", True),   # 已审批
                ("is_quality_control_approval", "=", True),   # 已审批
                ("actual_production", ">=", 1),     # 件数大于等于1
                ("sample_image", "!=", False)   # 有图片
            ])
            if th_per_management_objs:
                obj.is_sample_dress = True


    def examine_is_platemaking(self):
        ''' 检查样板'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_platemaking", "=", False)])
        for obj in objs:
            fsn_platemaking_record_objs = self.env['fsn_platemaking_record'].sudo().search([
                ("style_number_id.style_number_base_id", "=", obj.style_number.style_number_base_id.id),   # 款号前缀
                ("is_supervisor_approval", "=", True),   # 已审批
                ("is_quality_control_approval", "=", True),   # 已审批
                ("actual_production", ">=", 1),     # 件数大于等于1
                ("version_sample_image", "!=", False),  # 有图片
                ("plate_number", "!=", False),  # 有版号
                ("version_sample_attachment_ids", "!=", False)  # 有附件
            ])
            if fsn_platemaking_record_objs:
                obj.is_platemaking = True


    def examine_is_process(self):
        ''' 检查工时工序'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_process", "=", False)])
        for obj in objs:
            mhp_mhp_objs = self.env['mhp.mhp'].sudo().search([
                # ("style_number", "=", obj.order_number.id),
                ("order_number", "=", obj.style_number.id),
                ("state", "=", "已审批")
            ])
            if mhp_mhp_objs:
                obj.is_process = True


    def examine_is_template(self):
        ''' 检查模板'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_template", "=", False)])
        for obj in objs:
            fsn_template_record_objs = self.env['fsn_template_record'].sudo().search([
                ("style_number_id.style_number_base_id", "=", obj.style_number.style_number_base_id.id),   # 款号前缀
                ("actual_production", ">=", 1),     # 件数大于等于1
                ("version_sample_image", "!=", False),  # 有图片
            ])
            if fsn_template_record_objs:
                obj.is_template = True


    def examine_is_process_sheet(self):
        ''' 检查工艺单'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_process_sheet", "=", False)])
        for obj in objs:
            production_preparation_objs = self.env['production_preparation'].sudo().search([
                ("order_number", "=", obj.order_number.id),     # 订单号
                ("style_number.style_number_base_id", "=", obj.style_number.style_number_base_id.id),   # 款号前缀
                ("process_sheet", "!=", False),     # 有工艺单
            ])
            if production_preparation_objs:
                obj.is_process_sheet = True
            else:
                fsn_process_sheet_objs = self.env['fsn_process_sheet'].sudo().search([
                    ("order_number", "=", obj.order_number.id),     # 订单号
                    ("style_number.style_number_base_id", "=", obj.style_number.style_number_base_id.id),   # 款号前缀
                ])
                if fsn_process_sheet_objs:
                    obj.is_process_sheet = True


    def examine_is_unit_consumption(self):
        ''' 检测单件用量'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_unit_consumption", "=", False)])
        for obj in objs:
            if self.env['sheet_materials'].sudo().search([("style_number.style_number_base_id", "=", obj.style_number.style_number_base_id.id)]):
                obj.is_unit_consumption = True


    def examine_is_surface_material(self):
        ''' 检查面料采购'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_surface_material", "=", False)])
        for obj in objs:
            fabric_ingredients_procurement_objs = self.env['fabric_ingredients_procurement'].sudo().search([("type", "=", "面料"), ("order_id", "=", obj.order_number.id), ("style_number", "=", obj.style_number.id)])
            obj.is_surface_material = all(True if i.state == "已采购" else False for i in fabric_ingredients_procurement_objs)


    def examine_is_auxiliary_material(self):
        ''' 检测辅料采购'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_auxiliary_material", "=", False)])
        for obj in objs:
            fabric_ingredients_procurement_objs = self.env['fabric_ingredients_procurement'].sudo().search([("type", "!=", "面料"), ("order_id", "=", obj.order_number.id), ("style_number", "=", obj.style_number.id)])
            obj.is_auxiliary_material = all(True if i.state == "已采购" else False for i in fabric_ingredients_procurement_objs)



    def examine_is_cutting_bed(self):
        ''' 检查裁床'''
        objs = self.env['prenatal_preparation_progress'].sudo().search([("is_cutting_bed", "=", False)])
        for obj in objs:
            
            cutting_bed_production_objs = self.env['cutting_bed_production'].sudo().search([("order_number", "=", obj.order_number.id), ("style_number", "=", obj.style_number.id)])

            if obj.sale_pro_line_id.voucher_count and sum(cutting_bed_production_objs.mapped("complete_productionp")) >= obj.sale_pro_line_id.voucher_count:
                obj.is_cutting_bed = True


    def refresh_prenatal_preparation_progress_info(self):

        self.examine_is_sample_dress()
        self.examine_is_platemaking()
        self.examine_is_process()
        self.examine_is_template()
        self.examine_is_process_sheet()
        self.examine_is_surface_material()
        self.examine_is_auxiliary_material()
        self.examine_is_cutting_bed()
        self.examine_is_unit_consumption()


