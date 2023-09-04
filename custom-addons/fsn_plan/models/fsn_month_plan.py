from datetime import datetime, date, time, timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FsnMonthPlan(models.Model):
    _name = 'fsn_month_plan'
    _description = 'FSN_月计划'
    _order = "create_date desc"
    _rec_name = 'style_number'

    month = fields.Char(string="月份", required=True)

    fsn_staff_team_id = fields.Many2one("fsn_staff_team", string="组别")
    people_number = fields.Integer(string="人数")

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    order_number_date = fields.Date(string="订单日期", related="order_number.date", store=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related="order_number.processing_type", store=True)
    is_external_clipping = fields.Boolean(string="外部裁剪")
    client_id = fields.Many2one("fsn_customer", string="客户", related="order_number.customer_id", store=True)
    customer_delivery_time = fields.Date(string='客户货期', related="order_number.customer_delivery_time", store=True)
    product_name = fields.Char(string="品名", related="order_number.product_name", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="订单明细", compute="set_sale_pro_line_id", store=True)
    @api.depends("order_number", "style_number")
    def set_sale_pro_line_id(self):
        for record in self:
            sale_pro_line_obj = self.env['sale_pro_line'].sudo().search([("sale_pro_id", "=", record.order_number.id), ("style_number", "=", record.style_number.id)])
            if sale_pro_line_obj:
                record.sale_pro_line_id = sale_pro_line_obj.id
            else:
                record.sale_pro_line_id = False

    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    plan_number = fields.Integer(string="计划数量", compute="set_plan_number", store=True)
    @api.depends("sale_pro_line_id", "sale_pro_line_id.voucher_count")
    def set_plan_number(self):
        for record in self:
            if record.sale_pro_line_id:
                record.plan_number = int(record.sale_pro_line_id.voucher_count)
            else:
                record.plan_number = False



    fabric_item_number = fields.Char(string="面料货号")
    style = fields.Char(string="款式")
    surface_material_expected_date = fields.Date(string="面辅料齐备预计日期")
    surface_material_practical_date = fields.Date(string="面辅料齐备实际日期", related="order_number.face_to_face_time", store=True)
    plan_tailor_date = fields.Date(string="计划开裁日期")
    plan_online_date = fields.Date(string="计划上线日期", required=True)

    ultimately_delivery_time = fields.Date(string="实际交货期", related="order_number.actual_finish_date", store=True)
    production_delivery_time = fields.Date(string="计划交货期", required=True)



    production_batch = fields.Integer(string="生产批次")
    remark = fields.Text(string="备注")


    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")


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
            raise ValidationError(f"{self.order_number.order_number}、{self.style_number.style_number}、月计划已审批，不可对其进行操作！")



    def create_outsource_order(self):
        ''' 自动创建外发订单'''
        for record in self:
            if record.order_number.processing_type == "外发":

                outsource_order_obj = self.env['outsource_order'].sudo().search([("order_id", "=", record.order_number.id)])

                if not outsource_order_obj:


                    lines = []
                    if record.order_number.sale_pro_line_ids:

                        for sale_pro_obj_line in record.order_number.sale_pro_line_ids:

                            for voucher_detail_obj in sale_pro_obj_line.voucher_details:

                                lines.append((0, 0, {
                                    "style_number": sale_pro_obj_line.style_number.id,
                                    "size": voucher_detail_obj.size.id,
                                    "voucher_count": voucher_detail_obj.number,
                                }))

                    outsource_order_obj = self.env['outsource_order'].sudo().create({
                        "order_id": record.order_number.id,
                        "outsource_contract": record.order_number.order_number,
                        "style_number": record.style_number.id,
                        "customer_delivery_time": record.order_number.customer_delivery_time,
                        "outsource_order_line_ids": lines,
                        "attribute": record.order_number.attribute.id,
                        "product_name": record.order_number.product_name,
                        "style_picture": record.order_number.style_picture,
                        "plan_finish_date": record.production_delivery_time
                    })



    @api.model
    def create(self, vals):
        res = super(FsnMonthPlan,self).create(vals)

        res.create_outsource_order()

        return res


    def write(self, vals):

        for record in self:
            record.check_lock_state()

            if "plan_online_date" in vals:
                ''' 修改计划上线日期时，检查并改变生产订单状态'''
                if record.order_number.is_finish == "未完成":
                    
                    if datetime.strptime(vals['plan_online_date'], '%Y-%m-%d').date() >= fields.Date.today():
                        record.order_number.is_finish = "未上线"

        res = super(FsnMonthPlan, self).write(vals)

        return res



    def unlink(self):

        for record in self:
            record.check_lock_state()

        res = super(FsnMonthPlan, self).unlink()

        return res



