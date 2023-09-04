from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import timedelta

class OutsourceOrder(models.Model):
    _name = 'outsource_order'
    _description = 'FSN外发订单'
    _rec_name = 'outsource_contract'
    _order = "date desc"


    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.order_id.order_number}({record.outsource_plant_id.name})"
            result.append((record.id, rec_name))
        return result


    date = fields.Date(string="订单日期", related="order_id.date", store=True)

    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)


    outsource_contract = fields.Char(string="合同号", required=True)

    style_number = fields.Many2one('ib.detail', string='款号')

    @api.onchange('order_id')
    def style_number_domain(self):
        self.style_number = False
        if self.order_id:
            
            return {'domain': {'style_number': [("id", "in", self.order_id.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}

    contract_attachment = fields.Many2many(
        'ir.attachment',
        relation='contract_attachment_att_rel',
        column1='contract_attachment_id',
        column2='att_id',
        string="合同附件"
    )

    outsource_plant_id = fields.Many2one("outsource_plant", string="加工厂", ondelete="restrict")
    rating = fields.Char(string="工厂评级", compute="set_rating", store=True)
    @api.depends('outsource_plant_id')
    def set_rating(self):
        for record in self:
            record.rating = record.outsource_plant_id.rating

    responsible_person = fields.Many2one("hr.employee", string="负责人")

    # 检查数据唯一性
    @api.constrains('order_id', 'outsource_plant_id')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('order_id', '=', self.order_id.id),
            ('outsource_plant_id', '=', self.outsource_plant_id.id),
        ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在该销售订单和该加工厂的外发订单了！")

    style_picture = fields.Image(string='款式图片')

    outsource_price = fields.Float(string='外发单价', digits=(16, 5))

    contract_price = fields.Float(string="合同价格", digits=(16, 5), groups='fsn_base.fsn_insiders_group')

    IE_working_hours = fields.Float(string='IE工时(秒)', digits=(16, 5))

    tailor_ie_price = fields.Float(string="裁剪IE工价", digits=(16, 5))

    def set_ie_info(self):
        for record in self:
            
            mhp_mhp_obj = self.env['mhp.mhp'].sudo().search([("style_number", "=", record.order_id.id), ("order_number", "=", record.style_number.id)])
            if mhp_mhp_obj:
                
                record.IE_working_hours = mhp_mhp_obj.totle_time + mhp_mhp_obj.cc_totle_time + mhp_mhp_obj.hd_totle_time

                record.tailor_ie_price = mhp_mhp_obj.cc_totle_price
            
            else:
                raise ValidationError(f"没有查询到相关的工时单！")
            
    workshop_unit_price = fields.Float(string='车间单价')

    product_name = fields.Char(string='品名')

    attribute = fields.Many2one("order_attribute", string="属性")

    customer_delivery_time = fields.Date(string='客户货期', related="order_id.customer_delivery_time", store=True)

    face_to_face_time = fields.Date(string='面辅齐套时间')

    order_category = fields.Char(string='订单类别')

    production_group = fields.Char(string='生产组别')

    special_craft = fields.Char(string='特种工艺')

    is_tailor = fields.Boolean(string="是否裁剪")

    tailor_ie_total_price = fields.Float(string="裁剪总工价", compute="set_tailor_ie_total_price", store=True)
    # 设置裁剪总工价
    @api.depends('tailor_ie_price', 'outsource_order_line_ids', 'outsource_order_line_ids.actual_cutting_count')
    def set_tailor_ie_total_price(self):
        for record in self:
            record.tailor_ie_total_price = record.tailor_ie_price * sum(record.outsource_order_line_ids.mapped("actual_cutting_count"))


    deduct_money = fields.Float(string="退货扣款")
    other_deductions = fields.Float(string="其他扣款")


    total_price = fields.Float(string="总价格", compute="_value_total_price", store=True)

    @api.depends('outsource_order_line_ids', 'outsource_order_line_ids.actual_cutting_price')
    def _value_total_price(self):
        for record in self:
            record.total_price = sum(record.outsource_order_line_ids.mapped("actual_cutting_price"))


    state = fields.Selection([
        ('未上线', '未上线'),
        ('未完成', '未完成'),
        ('已完成', '已完成'),
        ('退单', '退单')
        ], string="订单状态", default="未上线")



    def change_state(self):
        for record in self:
            if record.state == "未上线":
                record.state = "未完成"
            elif record.state == "未完成":
                record.state = "已完成"
    

    def action_chargeback(self):
        for record in self:
            record.state = "退单"

    
    def state_back(self):
        for record in self:
            if record.state == "未完成":
                record.state = "未上线"
            elif record.state == "已完成":
                record.state = "未完成"
            elif record.state == "退单":
                record.state = "未上线"
    

    customer_payment_amount = fields.Float(string="客户付款金额", compute="set_customer_payment_amount", store=True)
    @api.depends("actual_delivered_quantity", "outsource_price", "deduct_money")
    def set_customer_payment_amount(self):
        for record in self:
            record.customer_payment_amount = (record.actual_delivered_quantity * record.outsource_price) - record.deduct_money
            
    actual_line_date = fields.Date(string="实际上线日期")
    plan_finish_date = fields.Date(string="计划完成日期")
    actual_finish_date = fields.Date(string="实际完成日期")

    outbound_order_progress_id = fields.One2many("outbound_order_progress", "outsource_order_id", string="外发进度")
    actual_delivered_quantity = fields.Float(string="实际交货数", compute="set_actual_delivered_quantity", store=True)
    @api.depends("outbound_order_progress_id", "outbound_order_progress_id.quantity_delivered")
    def set_actual_delivered_quantity(self):
        for record in self:
            record.actual_delivered_quantity = sum(record.outbound_order_progress_id.mapped("quantity_delivered"))

    remarks = fields.Char(string="备注")

    outsource_order_line_ids = fields.One2many("outsource_order_line", "outsource_order_id", string="外发订单明细")



    order_quantity = fields.Integer(string="订单总数", compute="set_order_quantity", store=True)
    @api.depends("outsource_order_line_ids", "outsource_order_line_ids.voucher_count")
    def set_order_quantity(self):
        for record in self:
            record.order_quantity = sum(record.outsource_order_line_ids.mapped("voucher_count"))

    approval_state = fields.Selection([
        ('待审批', '待审批'),
        ('已审批', '已审批'),
    ], string="状态", default="待审批")


    def auto_set_approval_state(self, today):
        ''' 定时任务，自动设置审批状态'''
        query_date = today + timedelta(days=1)
        outsource_order_objs = self.env['outsource_order'].sudo().search([("customer_delivery_time", "<", query_date), ("approval_state", "=", "待审批")])
        for outsource_order_obj in outsource_order_objs:
            if outsource_order_obj.order_quantity and abs(outsource_order_obj.order_quantity - outsource_order_obj.stock) < 5:
                
                outsource_order_obj.approval_state = "已审批"


    payment_state = fields.Selection([
        ("未付款", "未付款"),
        ("部分付款", "部分付款"),
        ("已付款", "已付款"),
    ], string="付款状态", default="未付款")

    bill_state = fields.Selection([
        ("未开票", "未开票"),
        ("已开票", "已开票"),
    ], string="是否开票", default="未开票")


    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"
        elif button_type == "设为已付款":
            name = "确认设为已付款吗？"
        elif button_type == "设为未付款":
            name = "确认设为未付款吗？"
        elif button_type == "修改付款状态":
            name = "请选择要设置为的状态！"
        elif button_type == "设为已开票":
            name = "确认设为已开票吗？"
        elif button_type == "设为未开票":
            name = "确认设为未开票吗？"
        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'outsource_order',
            'view_id': self.env.ref('fsn_outsource.outsource_order_approval_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.approval_state = "待审批"

        elif button_type == "through":
            self.approval_state = "已审批"

        elif button_type == "设为已付款":
            self.payment_state = "已付款"
        elif button_type == "设为未付款":
            self.payment_state = "未付款"
        elif button_type == "设为部分付款":
            self.payment_state = "部分付款"

        elif button_type == "设为已开票":
            self.bill_state = "已开票"
        elif button_type == "设为未开票":
            self.bill_state = "未开票"




    def write(self, vals):

        for record in self:

            if record.approval_state == "已审批":

                if ("approval_state" in vals or "payment_state" in vals or "bill_state" in vals or "state" in vals) and len(vals) == 1:
                    pass
                else:
                    raise ValidationError(f"外发订单已经审批，不可操作！")
            

        res = super(OutsourceOrder, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.approval_state == "已审批":

                raise ValidationError(f"外发订单已经审批，不可删除！")

        res = super(OutsourceOrder, self).unlink()

        return res
    


class OutsourceOrderLine(models.Model):
    _name = 'outsource_order_line'
    _description = 'FSN外发订单明细'
    _rec_name = 'style_number'
    # _order = "date desc"

    outsource_order_id = fields.Many2one("outsource_order", string="外发订单", ondelete="cascade")

    style_number = fields.Many2one('ib.detail', string='款号', required=True)

    unit_price = fields.Float(string="外发单价", related="outsource_order_id.outsource_price", store=True)

    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)

    size = fields.Many2one("fsn_size", string="尺码", required=True)
    
    voucher_count = fields.Float(string="制单数")

    actual_cutting_count = fields.Float(string="实裁数")

    actual_cutting_price = fields.Float(string="价格", compute="_value_actual_cutting_price", store=True)

    @api.depends('unit_price', 'voucher_count')
    def _value_actual_cutting_price(self):
        for record in self:
            record.actual_cutting_price = record.unit_price * record.voucher_count






