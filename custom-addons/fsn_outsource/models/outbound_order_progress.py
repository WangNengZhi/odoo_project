from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OutsourceOrderLine(models.Model):
    _inherit = 'outsource_order_line'
    

    outbound_order_progress_id = fields.Many2one("outbound_order_progress", string="订单进度表", compute="set_outbound_order_progress_id", store=True)
    @api.depends("outsource_order_id", "style_number", "size", "actual_cutting_count")
    def set_outbound_order_progress_id(self):
        for record in self:

            outbound_order_progress_obj = self.env['outbound_order_progress'].sudo().search([
                ("outsource_order_id", "=", record.outsource_order_id.id),
                ("style_number", "=", record.style_number.id)
            ], limit=1, order='date')
            if not outbound_order_progress_obj:
                outbound_order_progress_obj = self.env['outbound_order_progress'].sudo().create({
                    "outsource_order_id": record.outsource_order_id.id,
                    "date": record.outsource_order_id.date,
                    "order_number": record.outsource_order_id.order_id.id,
                    "style_number": record.style_number.id,
                    "contract_goods_time": record.outsource_order_id.customer_delivery_time,
                    "outsource_plant_id": record.outsource_order_id.outsource_plant_id.id,
                    "responsible_person": record.outsource_order_id.responsible_person.id
                })



            outbound_order_progress_line_obj = self.env['outbound_order_progress_line'].sudo().search([
                ("outbound_order_progress_id", "=", outbound_order_progress_obj.id),
                ("size", "=", record.size.id)
            ])
            if not outbound_order_progress_line_obj:
                outbound_order_progress_line_obj = self.env['outbound_order_progress_line'].sudo().create({
                    "outbound_order_progress_id": outbound_order_progress_obj.id,
                    "size": record.size.id,
                })
            
            if outbound_order_progress_line_obj.outsource_order_line_id.id != record.id:
                self.env['outbound_order_progress_line'].sudo().search([("outsource_order_line_id", "=", record.id)]).unlink()

            outbound_order_progress_line_obj.solid_cutting_quantity = record.actual_cutting_count
            outbound_order_progress_line_obj.outsource_order_line_id = record.id


            if record.outbound_order_progress_id.id != outbound_order_progress_obj.id:
                if not record.outbound_order_progress_id.outbound_order_progress_line_ids:
                    record.outbound_order_progress_id.sudo().unlink()
            record.outbound_order_progress_id = outbound_order_progress_obj.id



class OutboundOrderProgress(models.Model):
    _name = 'outbound_order_progress'
    _description = 'FSN外发订单进度表'

    _rec_name = 'style_number'
    _order = "date desc"


    outsource_order_id = fields.Many2one("outsource_order", string="外发订单", required=True)

    @api.onchange('outsource_order_id')
    def _onchange_outsource_order_id_info(self):
        self.order_number = self.outsource_order_id.order_id.id
        self.style_number = self.outsource_order_id.style_number.id

    outbound_order_progress_id = fields.Many2one("outbound_order_progress", string="前一天进度")
    date = fields.Date(string="日期", required=True)
    responsible_person = fields.Many2one("hr.employee", string="负责人", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('outbound_order_progress_id')
    def set_outbound_order_progress_info(self):
        if self.outbound_order_progress_id:
            self.outsource_order_id = self.outbound_order_progress_id.outsource_order_id.id
            self.order_number = self.outbound_order_progress_id.order_number.id
            self.style_number = self.outbound_order_progress_id.style_number.id
            self.actual_line_date = self.outbound_order_progress_id.actual_line_date
        else:
            self.outsource_order_id = False
            self.order_number = False
            self.style_number = False
            self.actual_line_date = False


    @api.onchange('order_number')
    def style_number_domain(self):

        if not self.outbound_order_progress_id:

            self.style_number = False
            if self.order_number and not self.outbound_order_progress_id:
                
                return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
            else:
                return {'domain': {'style_number': []}}

    style = fields.Char(string="款式", compute="set_style", store=True)
    @api.depends("outsource_order_id", "outsource_order_id.attribute", "outsource_order_id.attribute.name")
    def set_style(self):
        for record in self:
            record.style = record.outsource_order_id.attribute.name


    voucher_quantity = fields.Integer(string="订单数量", compute="set_voucher_quantity", store=True)
    @api.depends("outsource_order_id", "style_number", "outsource_order_id.order_quantity")
    def set_voucher_quantity(self):
        for record in self:
            outsource_order_line_objs = self.env['outsource_order_line'].sudo().search([("outsource_order_id", "=", record.outsource_order_id.id), ("style_number", "=", record.style_number.id)])
            record.voucher_quantity = sum(outsource_order_line_objs.mapped("voucher_count"))
            

    cutting_bed_quantity = fields.Integer(string="总裁床数量", compute="set_total_quantity", store=True)
    solid_cutting_quantity = fields.Integer(string="裁床数量", compute="set_complete_number", store=True)
    total_number_completed = fields.Integer(string="总完成数量", compute="set_total_quantity", store=True)
    complete_number = fields.Integer(string="完成数量", compute="set_complete_number", store=True)
    @api.depends('complete_number', 'solid_cutting_quantity', 'outbound_order_progress_id', 'outbound_order_progress_id.cutting_bed_quantity', 'outbound_order_progress_id.total_number_completed')
    def set_total_quantity(self):
        for record in self:
            record.cutting_bed_quantity = record.solid_cutting_quantity + record.outbound_order_progress_id.cutting_bed_quantity

            record.total_number_completed = record.complete_number + record.outbound_order_progress_id.total_number_completed
    
    remaining_number = fields.Integer(string="剩余数量", compute="set_remaining_number", store=True)
    @api.depends('cutting_bed_quantity', 'total_number_completed')
    def set_remaining_number(self):
        for record in self:
            record.remaining_number = record.cutting_bed_quantity - record.total_number_completed

    quantity_delivered = fields.Integer(string="交货数量", compute="set_quantity_delivered", store=True)
    @api.depends('outbound_order_progress_line_ids', 'outbound_order_progress_line_ids.quantity_delivered')
    def set_quantity_delivered(self):
        for record in self:
            record.quantity_delivered = sum(record.outbound_order_progress_line_ids.mapped("quantity_delivered"))

    contract_goods_time = fields.Date(string="合同货期", compute="set_outsource_order_info", store=True)
    outsource_plant_id = fields.Many2one("outsource_plant", string="生产厂商", compute="set_outsource_order_info", store=True)
    outsource_plant_contact = fields.Char(string="生产厂商联系方式", compute="set_outsource_order_info", store=True)
    actual_line_date = fields.Date(string="实际上线日期", compute="set_outsource_order_info", store=True)
    estimated_completion_date = fields.Date(string="预计完成日期", compute="set_outsource_order_info", store=True)
    @api.depends("outsource_order_id", "outsource_order_id.outsource_plant_id", "outsource_order_id.outsource_plant_id", "outsource_order_id.plan_finish_date", "outsource_order_id.actual_line_date")
    def set_outsource_order_info(self):
        for record in self:
            if record.outsource_order_id:
                record.outsource_plant_id = record.outsource_order_id.outsource_plant_id.id
                record.outsource_plant_contact = record.outsource_order_id.outsource_plant_id.plant_boss_phone
                record.estimated_completion_date = record.outsource_order_id.plan_finish_date
                record.actual_line_date = record.outsource_order_id.actual_line_date
                record.contract_goods_time = record.outsource_order_id.customer_delivery_time
            else:
                record.outsource_plant_id = False
                record.outsource_plant_contact = False
                record.estimated_completion_date = False
                record.actual_line_date = False
                record.contract_goods_time = False

    outbound_order_progress_line_ids = fields.One2many("outbound_order_progress_line", "outbound_order_progress_id", string="订单进度表明细")

    @api.depends('outbound_order_progress_line_ids', 'outbound_order_progress_line_ids.complete_number', 'outbound_order_progress_line_ids.solid_cutting_quantity')
    def set_complete_number(self):
        for record in self:
            record.solid_cutting_quantity = sum(record.outbound_order_progress_line_ids.mapped("solid_cutting_quantity"))
            record.complete_number = sum(record.outbound_order_progress_line_ids.mapped("complete_number"))


    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.date}，{record.order_number.order_number}，{record.style_number.style_number}"
            result.append((record.id, rec_name))
        return result






class OutboundOrderProgressLine(models.Model):
    _name = 'outbound_order_progress_line'
    _description = 'FSN外发订单进度表明细'

    outsource_order_line_id = fields.Many2one("outsource_order_line", string="外发订单明细", ondelete="cascade")
    outbound_order_progress_id = fields.Many2one("outbound_order_progress", string="订单进度表", ondelete="cascade")
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    solid_cutting_quantity = fields.Integer(string="裁床数量")
    complete_number = fields.Integer(string="完成数量")
    remaining_number = fields.Integer(string="剩余数量", compute="set_remaining_number", store=True)


    quantity_delivered = fields.Integer(string="交货数量")

    # 检查数据唯一性
    @api.constrains('outbound_order_progress_id', 'size')
    def _check_unique(self):
        for record in self:
            demo = self.env[self._name].sudo().search([
                ('outbound_order_progress_id', '=', record.outbound_order_progress_id.id),
                ('size', '=', record.size.id),
            ])

            if len(demo) > 1:
                raise ValidationError(f"尺码不可重复！")

    @api.depends('solid_cutting_quantity', 'complete_number')
    def set_remaining_number(self):
        for record in self:
            record.remaining_number = record.solid_cutting_quantity - record.complete_number







