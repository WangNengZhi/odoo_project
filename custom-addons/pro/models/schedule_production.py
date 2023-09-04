from odoo.exceptions import ValidationError
from odoo import models, fields, api

from datetime import timedelta

''' 尺码明细'''
class VoucherDetails(models.Model):
    _inherit = "voucher_details"


    def set_schedule_production(self):
        for record in self:
            
            schedule_production_obj = self.env['schedule_production'].sudo().search([("voucher_details_id", "=", record.id)])
            if not schedule_production_obj:
                self.env['schedule_production'].sudo().create({"voucher_details_id": record.id})


    @api.model
    def create(self, vals):

        res = super(VoucherDetails, self).create(vals)

        res.sudo().set_schedule_production()

        return res

    def write(self, vals):

        schedule_production_obj = self.env['schedule_production'].sudo().search([("voucher_details_id", "=", self.id)])
        if schedule_production_obj.lock_state == "已审批":
            raise ValidationError(f"{self.sale_pro_line_id.sale_pro_id.order_number}、{self.sale_pro_line_id.style_number.style_number}、{self.size.name}生产进度表已审批，不可对其进行操作！")
        
        res = super(VoucherDetails, self).write(vals)

        return res

    def unlink(self):
        for record in self:
            schedule_production_obj = self.env['schedule_production'].sudo().search([("voucher_details_id", "=", record.id)])
            if schedule_production_obj.lock_state == "已审批":
                raise ValidationError(f"{record.sale_pro_line_id.sale_pro_id.order_number}、{record.sale_pro_line_id.style_number.style_number}、{record.size.name}生产进度表已审批，不可对其进行操作！")
            
        res = super(VoucherDetails, self).unlink()
        return res



''' 裁床产量'''
class CuttingBedProduction(models.Model):
    _inherit = "cutting_bed_production"


    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production", store=True, ondelete='restrict')
    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production(self):
        for record in self:
            if record.order_number and record.style_number and record.product_size:
                schedule_production_obj = self.env['schedule_production'].sudo().search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if schedule_production_obj:
                    record.schedule_production_id = schedule_production_obj.id
                else:
                    raise ValidationError(f"请检查日期：{record.date}，订单号:{record.order_number.order_number}和款号:{record.style_number.style_number}和尺码:{record.product_size.name}是否匹配或正确！")


    @api.model
    def create(self, vals):

        res = super(CuttingBedProduction, self).create(vals)

        res.sudo().set_schedule_production()

        return res

    def write(self, vals):

        if "lock_state" not in vals:
            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", self.order_number.id),
                ("style_number", "=", self.style_number.id),
                ("size", "=", self.product_size.id)
            ])
            if schedule_production_obj.lock_state == "已审批":
                raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")

        res = super(CuttingBedProduction, self).write(vals)

        return res

    def unlink(self):
        for record in self:
            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj.lock_state == "已审批":
                raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
            
        res = super(CuttingBedProduction, self).unlink()
        return res


''' 组产值'''
class ProPro(models.Model):
    _inherit = "pro.pro"

    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production", store=True, ondelete='restrict')
    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production(self):
        for record in self:
            if record.order_number and record.style_number and record.product_size:
                schedule_production_obj = self.env['schedule_production'].sudo().search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if schedule_production_obj:
                    record.schedule_production_id = schedule_production_obj.id
                else:

                    raise ValidationError(f"请检查日期：{record.date}，订单号:{record.order_number.order_number}和款号:{record.style_number.style_number}和尺码:{record.product_size.name}是否匹配或正确！")

    @api.model
    def create(self, vals):

        res = super(ProPro, self).create(vals)

        res.sudo().set_schedule_production()

        return res



    def write(self, vals):

        schedule_production_obj = self.env['schedule_production'].sudo().search([
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("size", "=", self.product_size.id)
        ])
        if schedule_production_obj.lock_state == "已审批":
            raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
        
        res = super(ProPro, self).write(vals)

        return res
    
    def unlink(self):
        for record in self:
            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj.lock_state == "已审批":
                raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
        
        res = super(ProPro, self).unlink()
        return res



''' 外发产值'''
class OutgoingOutput(models.Model):
    _inherit = "outgoing_output"

    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production", store=True, ondelete='restrict')
    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production(self):
        for record in self:
            if record.order_number and record.style_number and record.product_size:
                schedule_production_obj = self.env['schedule_production'].sudo().search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.product_size.id)
                ])
                if schedule_production_obj:
                    record.schedule_production_id = schedule_production_obj.id
                else:

                    raise ValidationError(f"请检查日期：{record.date}，订单号:{record.order_number.order_number}和款号:{record.style_number.style_number}和尺码:{record.product_size.name}是否匹配或正确！")

    @api.model
    def create(self, vals):

        res = super(OutgoingOutput, self).create(vals)

        res.sudo().set_schedule_production()

        return res



    def write(self, vals):

        schedule_production_obj = self.env['schedule_production'].sudo().search([
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("size", "=", self.product_size.id)
        ])
        if schedule_production_obj.lock_state == "已审批":
            raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
        
        res = super(OutgoingOutput, self).write(vals)

        return res


    def unlink(self):
        for record in self:
            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj.lock_state == "已审批":
                 raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
        
        res = super(OutgoingOutput, self).unlink()
        return res

''' 库存'''
class FinishedInventory(models.Model):
    _inherit = "finished_inventory"

    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_style_number_summary", store=True, ondelete='restrict')
    @api.depends('order_number', 'style_number', 'size')
    def set_schedule_production(self):
        for record in self:
            if record.order_number and record.style_number and record.size:
                schedule_production_obj = self.env['schedule_production'].sudo().search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.size.id)
                ])
                if schedule_production_obj:
                    record.schedule_production_id = schedule_production_obj.id
                else:
                    raise ValidationError(f"{record.order_number.order_number}, {record.style_number.style_number}, {record.size.name}请检查订单号、款号和尺码是否正确！")


    @api.model
    def create(self, vals):

        res = super(FinishedInventory, self).create(vals)

        res.sudo().set_schedule_production()

        return res


# 库存明细
class FinishedProductWareLine(models.Model):
    _inherit = "finished_product_ware_line"


    def write(self, vals):

        if self.source_destination.type != "外部":

            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", self.order_number.id),
                ("style_number", "=", self.style_number.id),
                ("size", "=", self.size.id)
            ])
            if schedule_production_obj.lock_state == "已审批":
                raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
            

        res = super(FinishedProductWareLine, self).write(vals)

        return res

    def unlink(self):
        for record in self:

            if record.source_destination.type != "外部":

                schedule_production_obj = self.env['schedule_production'].sudo().search([
                    ("order_number", "=", record.order_number.id),
                    ("style_number", "=", record.style_number.id),
                    ("size", "=", record.size.id)
                ])
                if schedule_production_obj.lock_state == "已审批":
                    raise ValidationError(f"{schedule_production_obj.order_number.order_number}、{schedule_production_obj.style_number.style_number}、{schedule_production_obj.size.name}生产进度表已审批，不可对其进行操作！")
            
        res = super(FinishedProductWareLine, self).unlink()
        return res


class SuspensionSystemSummary(models.Model):
    '''吊挂'''
    _inherit = "suspension_system_summary"


    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production_id", store=True, ondelete='restrict')

    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production_id(self):
        for record in self:
            schedule_production_obj = record.schedule_production_id.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj:
                record.schedule_production_id = schedule_production_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemSummary, self).create(vals)

        res.set_schedule_production_id()

        return res


class SuspensionSystemRework(models.Model):
    '''吊挂返修'''
    _inherit = "suspension_system_rework"


    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production_id", store=True, ondelete='restrict')
    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production_id(self):
        for record in self:
            schedule_production_obj = record.schedule_production_id.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj:
                record.schedule_production_id = schedule_production_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemRework, self).create(vals)

        res.set_schedule_production_id()

        return res


class SuspensionSystemRepair(models.Model):
    '''吊挂修复'''
    _inherit = "suspension_system_repair"


    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production_id", store=True, ondelete='restrict')


    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production_id(self):
        for record in self:
            schedule_production_obj = record.schedule_production_id.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj:
                record.schedule_production_id = schedule_production_obj.id


    @api.model
    def create(self, vals):

        res = super(SuspensionSystemRepair, self).create(vals)

        res.set_schedule_production_id()

        return res




class PrenatalPreparationProgress(models.Model):
    '''产前准备进度表'''
    _inherit = "prenatal_preparation_progress"



    schedule_production_ids = fields.One2many("schedule_production", "prenatal_preparation_progress_id", string="生产进度")


    def set_schedule_production_id(self):
        for record in self:
            schedule_production_objs = record.schedule_production_ids.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
            ])
            for schedule_production_obj in schedule_production_objs:
                schedule_production_obj.prenatal_preparation_progress_id = record.id


    @api.model
    def create(self, vals):

        res = super(PrenatalPreparationProgress, self).create(vals)

        res.set_schedule_production_id()


        return res


class FsnMonthPlan(models.Model):
    '''FSN_月计划'''
    _inherit = "fsn_month_plan"

    schedule_production_ids = fields.One2many("schedule_production", "fsn_month_plan_id", string="生产进度")


    def set_schedule_production_id(self):
        for record in self:
            schedule_production_objs = record.schedule_production_ids.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
            ])
            for schedule_production_obj in schedule_production_objs:
                schedule_production_obj.fsn_month_plan_id = record.id


    @api.model
    def create(self, vals):

        res = super(FsnMonthPlan, self).create(vals)

        res.set_schedule_production_id()

        return res

    def write(self, vals):

        for record in self:

            if "order_number" in vals or "style_number" in vals:
                record.set_schedule_production_id()

        res = super(FsnMonthPlan, self).write(vals)
        return res



class OutsourceOrderLine(models.Model):
    '''外发订单明细'''
    _inherit = "outsource_order_line"

    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production_id", store=True)


    @api.depends('outsource_order_id', 'outsource_order_id.order_id', 'style_number', 'size')
    def set_schedule_production_id(self):
        for record in self:
            schedule_production_obj = record.schedule_production_id.sudo().search([
                ("order_number", "=", record.outsource_order_id.order_id.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.size.id)
            ])
            if schedule_production_obj:
                record.schedule_production_id = schedule_production_obj.id


    @api.model
    def create(self, vals):

        res = super(OutsourceOrderLine, self).create(vals)

        res.set_schedule_production_id()

        return res


class LoseRecord(models.Model):
    '''丢失记录'''
    _inherit = "lose_record"


    schedule_production_id = fields.Many2one("schedule_production", string="生产进度", compute="set_schedule_production_id", store=True)



    @api.depends('order_number', 'style_number', 'product_size')
    def set_schedule_production_id(self):
        for record in self:
            schedule_production_obj = record.schedule_production_id.sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])
            if schedule_production_obj:
                record.schedule_production_id = schedule_production_obj.id


    @api.model
    def create(self, vals):

        res = super(LoseRecord, self).create(vals)

        res.set_schedule_production_id()

        return res



class ScheduleProduction(models.Model):
    _name = "schedule_production"
    _description = '生产进度'
    # _rec_name = "date"
    _order = "date_order desc"

    voucher_details_id = fields.Many2one("voucher_details", string="尺码明细", ondelete='cascade')

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="订单明细", related="voucher_details_id.sale_pro_line_id", store=True)

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', related="sale_pro_line_id.sale_pro_id", store=True)

    customer_id = fields.Many2one("fsn_customer", string="客户", related="order_number.customer_id", store=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related="order_number.processing_type", store=True)
    order_attribute_id = fields.Many2one("order_attribute", string="品类", related="order_number.attribute", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="sale_pro_line_id.style_number", store=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", related="voucher_details_id.size", store=True)

    quantity_order = fields.Integer(string="订单数量", related="voucher_details_id.number", store=True)
    cutting_bed_production_ids = fields.One2many("cutting_bed_production", "schedule_production_id", string="裁床产量")
    outsource_order_line_ids = fields.One2many("outsource_order_line", "schedule_production_id", string="外发明细")
    quantity_cutting = fields.Integer(string="实裁数量", compute="set_quantity_cutting", store=True)
    @api.depends("cutting_bed_production_ids", "cutting_bed_production_ids.complete_productionp", "is_external_clipping", "outsource_order_line_ids", "outsource_order_line_ids.actual_cutting_count")
    def set_quantity_cutting(self):
        for record in self:
            if record.is_external_clipping:
                record.quantity_cutting = sum(record.outsource_order_line_ids.mapped("actual_cutting_count"))
            else:
                record.quantity_cutting = sum(record.cutting_bed_production_ids.mapped("complete_productionp"))

    fsn_month_plan_id = fields.Many2one("fsn_month_plan", string="月计划")
    is_external_clipping = fields.Boolean(string="外部裁剪", related="fsn_month_plan_id.is_external_clipping", store=True)


    prenatal_preparation_progress_id = fields.Many2one("prenatal_preparation_progress", string="产前准备进度")
    is_prenatal_preparation_progress = fields.Boolean(string="产前准备", related="prenatal_preparation_progress_id.is_all_complete", store=True)

    
    pro_pro_ids = fields.One2many("pro.pro", "schedule_production_id", string="组产值")
    outgoing_output_ids = fields.One2many("outgoing_output", "schedule_production_id", string="外发产值")
    quantity_goods = fields.Integer(string="实际收货数", compute="set_quantity_goods", store=True)
    @api.depends("pro_pro_ids", "pro_pro_ids.number", "outgoing_output_ids", "outgoing_output_ids.number")
    def set_quantity_goods(self):
        for record in self:

            record.quantity_goods = sum(record.pro_pro_ids.mapped("number")) + sum(record.outgoing_output_ids.mapped("number"))

    suspension_system_summary_ids = fields.One2many("suspension_system_summary", "schedule_production_id", string="吊挂")
    workshop_dg_number = fields.Integer(string="车间吊挂数", compute="set_suspension_system_summary_info", store=True)
    houdao_dg_number = fields.Integer(string="后道吊挂数", compute="set_suspension_system_summary_info", store=True)
    @api.depends("suspension_system_summary_ids", "suspension_system_summary_ids.total_quantity")
    def set_suspension_system_summary_info(self):
        for record in self:
            record.workshop_dg_number =  sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "车间").mapped("total_quantity"))
            record.houdao_dg_number =  sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "后道").mapped("total_quantity"))
    def text(self):
        for record in self:
            suspension_system_summary_objs = self.env['suspension_system_summary'].sudo().search([('MONo', '=', record.style_number.style_number),('product_size', '=', record.size.id)])
            #print(sum(suspension_system_summary_objs.mapped('total_quantity')))
            record.workshop_dg_number = sum(suspension_system_summary_objs.mapped('total_quantity'))
            # record.workshop_dg_number =  sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "车间").mapped("total_quantity"))
            # record.houdao_dg_number =  sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "后道").mapped("total_quantity"))
            #print(record.order_attribute_id.name,record.suspension_system_summary_ids.mapped('MONo'),record.suspension_system_summary_ids.mapped('style_number.style_number'), sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "车间").mapped("total_quantity")),sum(record.suspension_system_summary_ids.filtered(lambda x: x.group.department_id == "后道").mapped("total_quantity")))
    suspension_system_rework_ids = fields.One2many("suspension_system_rework", "schedule_production_id", string="吊挂返修")
    dg_rework_number = fields.Integer(string="吊挂返修数", compute="set_suspension_system_rework_info", store=True)
    dg_rework_few_number = fields.Integer(string="吊挂返修次数", compute="set_suspension_system_rework_info", store=True)
    @api.depends("suspension_system_rework_ids", "suspension_system_rework_ids.number")
    def set_suspension_system_rework_info(self):
        for record in self:
            record.dg_rework_number = sum(record.suspension_system_rework_ids.mapped("number"))
            record.dg_rework_few_number = sum(record.suspension_system_rework_ids.mapped("few_number"))





    suspension_system_repair_ids = fields.One2many("suspension_system_repair", "schedule_production_id", string="吊挂修复")
    dg_repair_number = fields.Integer(string="吊挂修复数", compute="set_dg_repair_number", store=True)
    @api.depends("suspension_system_repair_ids", "suspension_system_repair_ids.number")
    def set_dg_repair_number(self):
        for record in self:
            record.dg_repair_number = sum(record.suspension_system_repair_ids.mapped("number"))

    difference_delivery = fields.Integer(string="交货差异", compute="set_difference_delivery", store=True)
    @api.depends("quantity_cutting", "quantity_goods")
    def set_difference_delivery(self):
        for record in self:

            record.difference_delivery = record.quantity_cutting - record.quantity_goods
    


    finished_inventory_id = fields.One2many("finished_inventory", "schedule_production_id", string="成衣库存")

    quality_department_inventory = fields.Integer(string="总库存件数", compute="set_finished_inventory_info", store=True)
    quantity_storage = fields.Integer(string="仓库(总入库)", compute="set_finished_inventory_info", store=True)
    quantity_delivery = fields.Integer(string="仓库(总出仓)", compute="set_finished_inventory_info", store=True)

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

    @api.depends("finished_inventory_id", "finished_inventory_id.number", "finished_inventory_id.finished_product_ware_line_ids.state")
    def set_finished_inventory_info(self):
        for record in self:

            record.quality_department_inventory = sum(record.finished_inventory_id.mapped("number"))
            record.quantity_storage = sum(record.finished_inventory_id.mapped("put_number"))
            record.quantity_delivery = sum(record.finished_inventory_id.mapped("out_number"))

            record.normal_number = sum(record.finished_inventory_id.mapped("number"))
            record.normal_number = sum(record.finished_inventory_id.mapped("normal_number"))
            record.normal_put_number = sum(record.finished_inventory_id.mapped("normal_put_number"))
            record.normal_out_number = sum(record.finished_inventory_id.mapped("normal_out_number"))

            record.defective_number = sum(record.finished_inventory_id.mapped("defective_number"))
            record.defective_put_number = sum(record.finished_inventory_id.mapped("defective_put_number"))
            record.defective_out_number = sum(record.finished_inventory_id.mapped("defective_out_number"))

            record.no_accomplish_number = sum(record.finished_inventory_id.mapped("no_accomplish_number"))
            record.no_accomplish_put_number = sum(record.finished_inventory_id.mapped("no_accomplish_put_number"))
            record.no_accomplish_out_number = sum(record.finished_inventory_id.mapped("no_accomplish_out_number"))

            record.cutting_number = sum(record.finished_inventory_id.mapped("cutting_number"))
            record.cutting_put_number = sum(record.finished_inventory_id.mapped("cutting_put_number"))
            record.cutting_out_number = sum(record.finished_inventory_id.mapped("cutting_out_number"))

            record.no_normal_number = sum(record.finished_inventory_id.mapped("no_normal_number"))
            record.no_normal_put_number = sum(record.finished_inventory_id.mapped("no_normal_put_number"))
            record.no_normal_out_number = sum(record.finished_inventory_id.mapped("no_normal_out_number"))


    qualified_stock = fields.Integer(string="存量", related="finished_inventory_id.stock", store=True)
    delivery_quantity = fields.Integer(string="客户交付数量", related="finished_inventory_id.delivery_quantity", store=True)
    customer_enter = fields.Integer(string="客户入库数", related="finished_inventory_id.customer_enter", store=True)
    customer_out = fields.Integer(string="客户出库数", related="finished_inventory_id.customer_out", store=True)


    factory_delivery_variance = fields.Integer(string="工厂交付差异", compute="set_factory_delivery_variance", store=True)
    @api.depends("quantity_cutting", "quantity_order", "qualified_stock")
    def set_factory_delivery_variance(self):
        for record in self:

            if record.quantity_cutting:
                record.factory_delivery_variance = record.quantity_cutting - record.qualified_stock
            else:
                record.factory_delivery_variance = record.quantity_order - record.qualified_stock

    state = fields.Selection([
        ('退单', '退单'),
        ('未完成', '未完成'),
        ('已完成', '已完成'),
        ], string="状态", default="未完成", compute="set_state", store=True)

    @api.depends("qualified_stock", "quantity_cutting", "sale_pro_line_id", 'sale_pro_line_id.state')
    def set_state(self):
        for record in self:
            if record.sale_pro_line_id.state == "退单":
                record.state = "退单"
            elif record.quantity_cutting and record.qualified_stock and record.quantity_cutting == record.qualified_stock:
                record.state = "已完成"
            else:
                record.state = "未完成"
                
    lose_record_ids = fields.One2many("lose_record", "schedule_production_id", string="丢失")
    lose_quantity = fields.Integer(string="丢失数量", compute="set_lose_quantity", store=True)
    @api.depends("lose_record_ids", "lose_record_ids.number")
    def set_lose_quantity(self):
        for record in self:
            record.lose_quantity = sum(record.lose_record_ids.mapped("number"))

    factory_repair = fields.Integer(string="工厂返修")
    date_order = fields.Date(string="下单日期", related="order_number.date", store=True)
    date_contract = fields.Date(string="合同日期", related="order_number.customer_delivery_time", store=True)
    cycle_production = fields.Integer(string="生产周期", compute="set_cycle_production", store=True)

    @api.depends("date_order", "date_contract")
    def set_cycle_production(self):
        for record in self:
            if record.date_order and record.date_contract:

                record.cycle_production = (record.date_contract - record.date_order).days



    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")


    def auto_set_lock_state(self, today):
        ''' 定时任务，自动设置审批状态'''
        query_date = today + timedelta(days=1)

        temp_schedule_production_objs = self.env['schedule_production'].sudo().search([("date_contract", "<", query_date), ("lock_state", "=", "未审批")])

        schedule_production_objs = self.env['schedule_production'].sudo().read_group(
            domain=[("order_number", "in", temp_schedule_production_objs.mapped("order_number").ids)],
            fields=['ids:array_agg(id)', "factory_delivery_variance", "order_number", "quantity_order"],
            groupby="order_number"
        )

        for schedule_production_obj in schedule_production_objs:

            if schedule_production_obj['quantity_order'] and abs(schedule_production_obj['factory_delivery_variance']) < 10:

                self.env['schedule_production'].browse(schedule_production_obj['ids']).lock_state = "已审批"



    def set_lock_state(self):
        ''' 设置审批状态'''

        for record in self:
            lock_state = self.env.context.get("lock_state")
            if lock_state == "已审批":
                record.sudo().lock_state = "已审批"
            elif lock_state == "未审批":
                record.sudo().lock_state = "未审批"


    def check_lock_state(self):
        ''' 检查审批状态'''
        if self.lock_state == "已审批":
            raise ValidationError(f"{self.order_number.order_number}、{self.style_number.style_number}、{self.size.name}生产进度表已审批，不可对其进行操作！")


    def unlink(self):

        for record in self:
            record.check_lock_state()

        res = super(ScheduleProduction, self).unlink()

        return res