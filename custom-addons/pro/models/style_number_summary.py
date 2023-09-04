from odoo.exceptions import ValidationError
from odoo import models, fields, api

''' 订单'''
class SaleProSalePro(models.Model):
    _inherit = 'sale_pro.sale_pro'

    # 设置实际交货数
    def set_actual_delivered_quantity(self):

        for record in self:
            
            objs = self.env["style_number_summary"].sudo().search([("order_number", "=", record.id)])

            record.actual_delivered_quantity = sum(objs.mapped('delivery_quantity'))


''' 订单明细'''
class SaleProLine(models.Model):
    _inherit = 'sale_pro_line'


    def style_number_summary_sync_sale_pro_line_state(self):
        for record in self:
            style_number_summary_objs = self.env['style_number_summary'].sudo().search([("order_number", "=", record.sale_pro_id.id), ("style_number", "=", record.style_number.id),])
            if all(i == "完成" for i in style_number_summary_objs.mapped("state")):
                record.state = "已完成"
            else:
                record.state = "未完成"



''' 尺码明细'''
class VoucherDetails(models.Model):
    _inherit = "voucher_details"


    def set_style_number_summary(self):
        for record in self:
            
            style_number_summary_obj = self.env['style_number_summary'].sudo().search([("voucher_details_id", "=", record.id)])
            if not style_number_summary_obj:
                self.env['style_number_summary'].sudo().create({"voucher_details_id": record.id})


    @api.model
    def create(self, vals):

        res = super(VoucherDetails, self).create(vals)

        res.sudo().set_style_number_summary()

        return res



class ProPro(models.Model):
    '''组产值'''
    _inherit = "pro.pro"

    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_style_number_summary(self):
        for record in self:
            if record.order_number and record.style_number and record.product_size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:

                    raise ValidationError(f"请检查订单号、款号和尺码是否正确！")


    @api.model
    def create(self, vals):

        res = super(ProPro, self).create(vals)

        res.set_style_number_summary()

        return res


class CuttingBed(models.Model):
    '''裁床产值'''
    _inherit = "cutting_bed"

    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_style_number_summary(self):

        for record in self:
            if record.order_number and record.style_number and record.product_size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:
                    raise ValidationError(f"请检查订单号、款号和尺码是否正确！")


    @api.model
    def create(self, vals):

        res = super(CuttingBed, self).create(vals)

        res.set_style_number_summary()

        return res


class PosteriorPassageOutputValue(models.Model):
    '''后道产值'''
    _inherit = "posterior_passage_output_value"

    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_style_number_summary(self):

        for record in self:
            if record.order_number and record.style_number and record.product_size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:
                    raise ValidationError(f"请检查订单号、款号和尺码是否正确！")


    @api.model
    def create(self, vals):

        res = super(PosteriorPassageOutputValue, self).create(vals)

        res.set_style_number_summary()

        return res


class RepairValue(models.Model):
    '''返修产值'''
    _inherit = "repair_value"

    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number')
    def set_style_number_summary(self):

        for record in self:
            if record.order_number and record.style_number and record.product_size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:
                    raise ValidationError(f"请检查订单号、款号和尺码是否正确！")

    @api.model
    def create(self, vals):

        res = super(RepairValue, self).create(vals)

        # res.set_style_number_summary()

        return res


class InboundOutbound(models.Model):
    '''仓库产值(作废)'''
    _inherit = "inbound.outbound"

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总")



# 出入库
class FinishedProductWareLine(models.Model):
    _inherit = "finished_product_ware_line"


    style_number_summary_id = fields.Many2one("style_number_summary", compute="set_style_number_summary", store=True)



class ChenYiBaoCiLine(models.Model):
    '''报次产值'''
    _inherit = "chen_yi_bao_ci_line"


    def set_style_number_summary(self):
        for record in self:
            style_number_summary_objs = self.env['style_number_summary'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
            ])
            for style_number_summary_obj in style_number_summary_objs:
                style_number_summary_obj.chen_yi_bao_ci_line_ids = [(4, record.id)]

 
    @api.model
    def create(self, vals):

        res = super(ChenYiBaoCiLine, self).create(vals)

        res.sudo().set_style_number_summary()

        return res
    
    def write(self, vals):

        res = super(ChenYiBaoCiLine, self).write(vals)

        self.sudo().set_style_number_summary()

        return res



class LoseRecord(models.Model):
    '''丢失记录'''
    _inherit = "lose_record"

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_style_number_summary(self):
        for record in self:

            if record.order_number and record.style_number and record.product_size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:
                    raise ValidationError(f"请检查订单号、款号和尺码是否正确！")



    @api.model
    def create(self, vals):

        res = super(LoseRecord, self).create(vals)

        res.set_style_number_summary()

        return res



class SuspensionSystemSummary(models.Model):
    '''吊挂'''
    _inherit = "suspension_system_summary"


    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_style_number_summary(self):
        for record in self:

            if record.order_number and record.style_number and record.product_size and record.group.department_id == "车间":
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemSummary, self).create(vals)

        res.set_style_number_summary()

        return res


class FinishedInventory(models.Model):
    '''成衣库存'''
    _inherit = "finished_inventory"

    style_number_summary_id = fields.Many2one("style_number_summary", string="款汇总", compute="set_style_number_summary", store=True, ondelete='restrict')


    @api.depends('order_number', 'style_number', 'size')
    def set_style_number_summary(self):
        for record in self:

            if record.order_number and record.style_number and record.size:
                style_number_summary_obj = record.style_number_summary_id.search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.size.id)
                ])
                if style_number_summary_obj:
                    record.style_number_summary_id = style_number_summary_obj.id
                else:
                    raise ValidationError(f"{record.order_number.order_number}, {record.style_number.style_number}, {record.size.name}请检查订单号、款号和尺码是否正确！")

    @api.model
    def create(self, vals):

        res = super(FinishedInventory, self).create(vals)

        res.set_style_number_summary()

        return res


class StyleNumberSummary(models.Model):
    _name = "style_number_summary"
    _description = '款号件数汇总'
    _rec_name = "style_number"
    _order = "date desc"



    voucher_details_id = fields.Many2one("voucher_details", string="尺码明细", ondelete='cascade')

    date = fields.Date(string="日期", related="style_number.date", store=True)
    start_production_date = fields.Date(string="开始生产日期")

    def set_start_production_date(self):

        for record in self.env["style_number_summary"].search([("start_production_date", "=", False)]):
            
            planning_slot_objs = self.env['planning.slot'].search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("plan_stage", "=", "开款第一天"),
            ], order="dDate")


            if planning_slot_objs:
                record.start_production_date = planning_slot_objs[0].dDate

    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", related="sale_pro_line_id.sale_pro_id", store=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related="order_number.processing_type", store=True)
    sale_pro_line_id = fields.Many2one("sale_pro_line", string="订单明细", related="voucher_details_id.sale_pro_line_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="sale_pro_line_id.style_number", store=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", related="voucher_details_id.size", store=True)
    order_number_value = fields.Integer(string="订单数量", related="voucher_details_id.number", store=True)

    pro_pro = fields.One2many("pro.pro", "style_number_summary_id", string="组产值")
    workshop = fields.Float(string="车间", compute="_set_workshop", store=True)
    @api.depends('pro_pro')
    def _set_workshop(self):
        for record in self:
            
            record.workshop = sum(record.pro_pro.mapped('number'))
    
    suspension_system_summary_ids = fields.One2many("suspension_system_summary", "style_number_summary_id", string="吊挂产量")
    suspension_system_summary_number = fields.Float(string="吊挂", compute="set_suspension_system_summary_number", store=True)
    @api.depends('suspension_system_summary_ids')
    def set_suspension_system_summary_number(self):
        for record in self:
            
            record.suspension_system_summary_number = sum(record.suspension_system_summary_ids.mapped('total_quantity'))


    cutting_bed_ids = fields.One2many("cutting_bed", "style_number_summary_id", string="裁床产值")
    cutting_bed = fields.Float(string="裁床", compute="set_cutting_bed", store=True)
    @api.depends('cutting_bed_ids', 'cutting_bed_ids.number')
    def set_cutting_bed(self):
        for record in self:
            
            record.cutting_bed = sum(record.cutting_bed_ids.mapped('number'))


    posterior_passage_ids = fields.One2many("posterior_passage_output_value", "style_number_summary_id", string="后道产值")
    repair_value_ids = fields.One2many("repair_value", "style_number_summary_id", string="返修产值")
    posterior_passage = fields.Float(string="后道", compute="_set_posterior_passage", store=True)
    @api.depends('posterior_passage_ids', 'repair_value_ids')
    def _set_posterior_passage(self):
        for record in self:
        
            record.posterior_passage = sum(record.posterior_passage_ids.mapped('number')) - sum(record.repair_value_ids.mapped('number'))


    inbound_outbound_ids = fields.One2many("inbound.outbound", "style_number_summary_id", string="出库入库明细")
    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "style_number_summary_id", string="出入库明细")

    finished_inventory_ids = fields.One2many("finished_inventory", "style_number_summary_id", string="成衣库存")

    finished_inventory_number = fields.Float(string="总库存件数", compute="set_finished_inventory_info", store=True)
    enter_warehouse = fields.Float(string="仓库(总入库)", compute="set_finished_inventory_info", store=True)
    out_of_warehouse = fields.Float(string="仓库(总出库)", compute="set_finished_inventory_info", store=True)

    normal_number = fields.Integer(string="正常库存件数", compute="set_finished_inventory_info", store=True)
    normal_put_number = fields.Integer(string="正常入库件数", compute="set_finished_inventory_info", store=True)
    normal_out_number = fields.Integer(string="正常出库件数", compute="set_finished_inventory_info", store=True)

    defective_number = fields.Integer(string="报次库存件数", compute="set_finished_inventory_info", store=True)
    defective_put_number = fields.Integer(string="报次入库件数", compute="set_finished_inventory_info", store=True)
    defective_out_number = fields.Integer(string="报次出库件数", compute="set_finished_inventory_info", store=True)

    no_accomplish_number = fields.Integer(string="半成品库存件数", compute="set_finished_inventory_info", store=True)
    no_accomplish_put_number = fields.Integer(string="半成品入库件数", compute="set_finished_inventory_info", store=True)
    no_accomplish_out_number = fields.Integer(string="半成品出库件数", compute="set_finished_inventory_info", store=True)

    cutting_number = fields.Integer(string="裁片库存件数", compute="set_finished_inventory_info", store=True)
    cutting_put_number = fields.Integer(string="裁片入库件数", compute="set_finished_inventory_info", store=True)
    cutting_out_number = fields.Integer(string="裁片出库件数", compute="set_finished_inventory_info", store=True)

    no_normal_number = fields.Integer(string="非正常库存件数", compute="set_finished_inventory_info", store=True)
    no_normal_put_number = fields.Integer(string="非正常入库件数", compute="set_finished_inventory_info", store=True)
    no_normal_out_number = fields.Integer(string="非正常出库件数", compute="set_finished_inventory_info", store=True)

    @api.depends("finished_inventory_ids", "finished_inventory_ids.number", "finished_inventory_ids.finished_product_ware_line_ids.state")
    def set_finished_inventory_info(self):
        for record in self:
            
            record.finished_inventory_number = sum(record.finished_inventory_ids.mapped("number"))
            record.enter_warehouse = sum(record.finished_inventory_ids.mapped("put_number"))
            record.out_of_warehouse = sum(record.finished_inventory_ids.mapped("out_number"))

            record.normal_number = sum(record.finished_inventory_ids.mapped("normal_number"))
            record.normal_put_number = sum(record.finished_inventory_ids.mapped("normal_put_number"))
            record.normal_out_number = sum(record.finished_inventory_ids.mapped("normal_out_number"))

            record.defective_number = sum(record.finished_inventory_ids.mapped("defective_number"))
            record.defective_put_number = sum(record.finished_inventory_ids.mapped("defective_put_number"))
            record.defective_out_number = sum(record.finished_inventory_ids.mapped("defective_out_number"))

            record.no_accomplish_number = sum(record.finished_inventory_ids.mapped("no_accomplish_number"))
            record.no_accomplish_put_number = sum(record.finished_inventory_ids.mapped("no_accomplish_put_number"))
            record.no_accomplish_out_number = sum(record.finished_inventory_ids.mapped("no_accomplish_out_number"))

            record.cutting_number = sum(record.finished_inventory_ids.mapped("cutting_number"))
            record.cutting_put_number = sum(record.finished_inventory_ids.mapped("cutting_put_number"))
            record.cutting_out_number = sum(record.finished_inventory_ids.mapped("cutting_out_number"))

            record.no_normal_number = sum(record.finished_inventory_ids.mapped("no_normal_number"))
            record.no_normal_put_number = sum(record.finished_inventory_ids.mapped("no_normal_put_number"))
            record.no_normal_out_number = sum(record.finished_inventory_ids.mapped("no_normal_out_number"))



    chen_yi_bao_ci_line_ids = fields.Many2many("chen_yi_bao_ci_line", string="成衣报次明细")
    defective_good_number = fields.Float(string="报次件数", compute="_set_defective_good_number", store=True)

    @api.depends("chen_yi_bao_ci_line_ids", "chen_yi_bao_ci_line_ids.size_xs", "chen_yi_bao_ci_line_ids.size_s", "chen_yi_bao_ci_line_ids.size_m",\
            "chen_yi_bao_ci_line_ids.size_l",\
            "chen_yi_bao_ci_line_ids.size_xxl",\
            "chen_yi_bao_ci_line_ids.size_xs",\
            "chen_yi_bao_ci_line_ids.size_xxxl",\
        )
    def _set_defective_good_number(self):
        for record in self:
            if record.size.name == "XS":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_xs'))
            elif record.size.name == "S":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_s'))
            elif record.size.name == "M":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_m'))
            elif record.size.name == "L":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_l'))
            elif record.size.name == "XL":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_xl'))
            elif record.size.name == "XXL":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_xxl'))
            elif record.size.name == "XXXL":
                record.defective_good_number = sum(record.chen_yi_bao_ci_line_ids.mapped('size_xxxl'))




    lose_record_ids = fields.One2many("lose_record", "style_number_summary_id", string="丢失记录")
    lose_quantity = fields.Float(string="丢失", compute="_set_lose_quantity", store=True)
    @api.depends('lose_record_ids')
    def _set_lose_quantity(self):
        for record in self:

            record.lose_quantity = sum(record.lose_record_ids.mapped('number'))

    customer_enter = fields.Integer(string="客户入库数", compute="set_qualified_stock", store=True)
    customer_out = fields.Integer(string="客户出库数", compute="set_qualified_stock", store=True)
    qualified_stock = fields.Integer(string="存量", compute="set_qualified_stock", store=True)
    delivery_quantity = fields.Integer(string="客户交付数量", compute="set_qualified_stock", store=True)
    @api.depends("finished_inventory_ids", "finished_inventory_ids.customer_enter", "finished_inventory_ids.customer_out")
    def set_qualified_stock(self):
        for record in self:

            record.customer_out = record.finished_inventory_ids.customer_out
            record.customer_enter = record.finished_inventory_ids.customer_enter
            record.qualified_stock = record.finished_inventory_ids.stock
            record.delivery_quantity = record.customer_out - record.delivery_quantity

            record.order_number.sudo().set_actual_delivered_quantity()

    factory_delivery_variance = fields.Integer(string="工厂交付差异", compute="set_factory_delivery_variance", store=True)
    @api.depends("cutting_bed", "order_number_value", "qualified_stock")
    def set_factory_delivery_variance(self):
        for record in self:
            if record.cutting_bed:
                record.factory_delivery_variance = record.cutting_bed - record.qualified_stock
            else:
                record.factory_delivery_variance = record.order_number_value - record.qualified_stock

    cashmere_filling_room = fields.Float(string="充绒房")

    finish_plan_date = fields.Date(string="计划完成日期")
    # 设置计划完成日期
    def _set_finish_plan_date(self):
        for record in self:

            objs = self.env["production_preparation"].sudo().search([
                ("style_number", "=", record.style_number.id),  # 款号
                ("order_number", "=", record.order_number.id)   # 订单号
            ])

            record.finish_plan_date = objs.finish_plan_date

    actual_finish_date = fields.Date(string="实际完成日期")

    attrition_rate = fields.Float(string="损耗率", compute="set_attrition_rate", store=True, group_operator='avg')
    @api.depends('qualified_stock', 'cutting_bed')
    def set_attrition_rate(self):
        for record in self:
            if record.cutting_bed:
                # 损耗率 = （裁床数量 - 存量）/ 裁床数量
                record.attrition_rate = (record.cutting_bed - record.qualified_stock) / record.cutting_bed
            else:
                record.attrition_rate = 0


    is_abnormal = fields.Boolean(string="是否异常")

    state = fields.Selection([
        ('退单', '退单'),
        ('未完成', '未完成'),
        ('完成', '完成'),
        ('未开始', '未开始')
        ], string="状态", default="未开始", compute="compute_is_abnormal", store=True)


    # 设置完成状态
    @api.depends('order_number_value', 'qualified_stock', 'cutting_bed')
    def compute_is_abnormal(self):
        for record in self:


            # 订单数为0，则未开始
            if record.order_number_value == 0:
                record.state = "未开始"
            else:
                # 存量 + 报次 = 裁床  完成
                if record.qualified_stock and record.cutting_bed and record.qualified_stock >= record.cutting_bed:
                    record.state = "完成"
                else:
                    record.state = "未完成"
                
                record.sale_pro_line_id.style_number_summary_sync_sale_pro_line_state()















