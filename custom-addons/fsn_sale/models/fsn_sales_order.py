# -*- coding: utf-8 -*-
import datetime
import logging
import random
import time

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FsnSalesOrder(models.Model):
    _name = 'fsn_sales_order'
    _description = 'FSN销售订单'
    _rec_name = 'name'
    _order = "date desc"


    sale_order_id = fields.Many2one("sale.order", string="销售订单", ondelete="cascade")
    name = fields.Char(string="订单编号")
    date = fields.Date(string="下单日期", required=True)
    employee_name = fields.Char(string="销售姓名")

    fsn_order_category = fields.Selection([("成衣采购", "成衣采购"), ("承揽加工", "承揽加工")], string="订单类别", required=True)

    design_number = fields.Many2one("product_design", string="设计编号", required=True)
    order_type = fields.Selection([('加工', '加工'), ('贴牌', '贴牌'), ('自主品牌', '自主品牌')], string='订单类型', required=True)
    processing_type = fields.Selection([('生产', '生产'), ('现货', '现货')], string='加工类型', required=True)
    product_name = fields.Char(string='品名', required=True)
    attribute = fields.Many2one("order_attribute", string="属性", required=True)

    # liquidated_damage = fields.Integer(string='误期罚款')

    fsn_purchase_order_number = fields.Char(string="合同单号")
    fsn_delivery_date = fields.Date(string="合同截止日期", required=True)

    sale_pro_ids = fields.Many2many("sale_pro.sale_pro", string="生产订单")

    state = fields.Selection([('草稿', '草稿'), ('确认', '确认'), ('已完成', '已完成')], string="订单状态", default="草稿")


    fsn_payment_state = fields.Selection([("未付款", "未付款"), ("已付款", "已付款")], string="付款状态", default="未付款")
    fsn_customer_id = fields.Many2one("fsn_customer", string="客户", required=True)
    description = fields.Text(string="备注")


    fsn_sales_order_line_ids = fields.One2many("fsn_sales_order_line", "fsn_sales_order_id", string="FSN销售订单明细")
    total_order = fields.Float(string="订单总数", compute="set_total_order", store=True)
    @api.depends("fsn_sales_order_line_ids", "fsn_sales_order_line_ids.quantity")
    def set_total_order(self):
        for record in self:
            record.total_order = sum(record.fsn_sales_order_line_ids.mapped("quantity"))


    pre_tax_amount = fields.Float(string="税前合计", compute="set_pre_tax_amount", store=True)
    @api.depends("fsn_sales_order_line_ids", "fsn_sales_order_line_ids.amount")
    def set_pre_tax_amount(self):
        for record in self:
            record.pre_tax_amount = sum(record.fsn_sales_order_line_ids.mapped("amount"))

    tax_amount = fields.Float(string="税费金额", compute="set_tax_amount", store=True)
    @api.depends("fsn_sales_order_line_ids", "fsn_sales_order_line_ids.tax_amount")
    def set_tax_amount(self):
        for record in self:
            record.tax_amount = sum(record.fsn_sales_order_line_ids.mapped("tax_amount"))


    after_tax_total = fields.Float(string="应收账款", compute="set_after_tax_total", store=True)
    @api.depends("tax_amount", "pre_tax_amount")
    def set_after_tax_total(self):
        for record in self:
            record.after_tax_total = record.pre_tax_amount + record.tax_amount


    def set_fsn_payment_state(self):
        ''' 设置付款状态'''

        for record in self:
            if record.state == "草稿":
                raise ValidationError("草稿订单不可以修改付款状态！")
            
            record.fsn_payment_state = self._context.get("type")

    def set_state(self):
        ''' 设置状态'''
        for record in self:
            context_type = self._context.get("type")
            if context_type != "回退":
                record.state = context_type
                self.env['mail.channel'].send_technical_department_daily_report(record)
            else:
                if record.state == "已完成":
                    record.state = "确认"
                elif record.state == "确认":
                    record.state = "草稿"



    @api.model
    def create(self, vals):
        
        vals['name'] = self.env['ir.sequence'].next_by_code('fsn_sales_order')

        return super(FsnSalesOrder,self).create(vals)


    delivery_number = fields.Float(string="出库件数")
    def set_delivery_number(self):
        ''' 设置计算出库件数'''
        for reocrd in self.env['fsn_sales_order'].search([]):
            if reocrd.fsn_sales_order_line_ids:

                style_number_base_id_list = reocrd.fsn_sales_order_line_ids.mapped("style_number.style_number_base_id.id")
                # sale_pro_ids_list = reocrd.sale_pro_ids.ids

                fsn_sales_order_line_objs = self.env['fsn_sales_order_line'].sudo().search([
                    ("fsn_sales_order_id.fsn_customer_id", "=", reocrd.fsn_customer_id.id),
                    ("style_number.style_number_base_id", "in", style_number_base_id_list),
                    ("fsn_sales_order_id.state", "!=", "草稿")
                ])

                # for fsn_sales_order_line_obj in fsn_sales_order_line_objs.mapped("fsn_sales_order_id"):
                #     print(fsn_sales_order_line_obj)
                finished_product_ware_line_objs = self.env['finished_product_ware_line'].sudo().search([
                    # ("order_number", "in", sale_pro_ids_list),  # 生产订单id列表
                    ("style_number.style_number_base_id", "in", style_number_base_id_list),  # 款号前缀id列表
                    ("source_destination", "=", reocrd.fsn_customer_id.id), # 客户id
                    ("state", "=", "确认"),
                    ("type", "=", "出库"),
                    ("quality", "=", "合格"),
                    ("character", "=", "正常")
                ])

                temp_delivery_number = sum(finished_product_ware_line_objs.mapped("number"))
                
                for fsn_sales_order_obj in fsn_sales_order_line_objs.mapped("fsn_sales_order_id"):
                    if fsn_sales_order_obj.total_order >= temp_delivery_number:
                        fsn_sales_order_obj.delivery_number = temp_delivery_number
                        break
                    else:
                        fsn_sales_order_obj.delivery_number = fsn_sales_order_obj.total_order
                        temp_delivery_number -= fsn_sales_order_obj.total_order

    number_of_returned_items = fields.Integer(string='退货件数', compute="set_return_quantity", store=True)
    @api.depends("fsn_sales_order_line_ids", "fsn_sales_order_line_ids.quantity_returned")
    def set_return_quantity(self):
        """设置退货件数"""
        for record in self:
            record.number_of_returned_items = sum(record.fsn_sales_order_line_ids.mapped('quantity_returned'))

    return_amount = fields.Float(string='退货金额', compute="set_refund_amount", store=True)
    @api.depends("fsn_sales_order_line_ids", "fsn_sales_order_line_ids.quantity_returned", "fsn_sales_order_line_ids.unit_price")
    def set_refund_amount(self):
        """设置退款金额"""
        for record in self:
            refund_amount = sum(line.quantity_returned * line.unit_price for line in record.fsn_sales_order_line_ids)
            record.return_amount = refund_amount
    fine = fields.Float(string='误期罚款')


    actual_collection = fields.Float(string="实际收款", compute="set_actual_collection", store=True)
    # @api.depends("after_tax_total", "return_amount", "fine")
    @api.depends("after_tax_total", "fine")
    def set_actual_collection(self):
        """设置实际收款"""
        for record in self:
            # 实际收款 = 应收账款- 退货金额- 罚款(应收账款中已经减去了退货金额，所以这里只需要减去罚款)
            record.actual_collection = (record.after_tax_total - record.fine)

    fsn_approval_status = fields.Selection([("未审批", "未审批"), ("已审批", "已审批")], string="审批状态", required=True, default="未审批")



    used_digits = []
    last_date = None
    def generate_code(self):
        """生产不重复的订单号"""
        now = datetime.datetime.now()
        if FsnSalesOrder.last_date != now.date():
            FsnSalesOrder.last_date = now.date()
            FsnSalesOrder.used_digits = []

        year_last_two = now.year % 100
        month = str(now.month).zfill(2)
        day_of_month = now.day
        code = f"{year_last_two}{month}{day_of_month:02}"

        while True:
            last_digit = random.randint(0, 9)
            if last_digit not in FsnSalesOrder.used_digits:
                break
        FsnSalesOrder.used_digits.append(last_digit)
        code += str(last_digit)
        return int(code)

    def set_fsn_approval_status(self):
        ''' 设置审批状态'''

        for record in self:
            fsn_approval_status = self.env.context.get("fsn_approval_status")
            if fsn_approval_status == "已审批":
                record.sudo().fsn_approval_status = "已审批"
                # 加工类型是生产后续逻辑
                if record.processing_type == '生产':
                    # 检查订单号是否重复
                    while True:
                        code = self.generate_code()
                        existing_sale_pro = self.env['sale_pro.sale_pro'].search([('order_number', '=', code)])
                        if not existing_sale_pro:
                            break
                    # print(record.fsn_sales_order_line_ids.style_number)
                    data = {
                        'date': record.date,
                        'customer_id': record.fsn_customer_id.id,
                        'order_number': code,
                        'processing_type': record.processing_type,
                        'planned_completion_date': record.fsn_delivery_date,
                        'customer_delivery_time': record.fsn_delivery_date,
                        'product_name': record.product_name,
                        'attribute': record.attribute.id
                    }
                    new_sale_pro = self.env['sale_pro.sale_pro'].create(data)
                    # 将新创建的sale_pro记录的id添加到sale_pro_ids字段中
                    record.sale_pro_ids = [(4, new_sale_pro.id, 0)] # 添加关联记录的id

                    data1 = {
                        'style_number': record.fsn_sales_order_line_ids.style_number.id,
                        'fsn_color': record.fsn_sales_order_line_ids.fsn_color_id.id,
                        'unit_price': record.fsn_sales_order_line_ids.unit_price,
                        'sale_pro_id': new_sale_pro.id
                    }

                    line_obj = new_sale_pro.fsn_sales_line.create(data1)
                    # print(new_sale_pro.fsn_sales_line.voucher_details_id)
                    data2 = {
                        'size': record.fsn_sales_order_line_ids.product_size.id,
                        'number': record.fsn_sales_order_line_ids.quantity,
                        'sale_pro_line_id': line_obj.id
                    }
                    new_sale_pro.fsn_sales_line.voucher_details_id.create(data2)

            elif fsn_approval_status == "未审批":
                record.sudo().fsn_approval_status = "未审批"


class FsnSalesOrderLine(models.Model):
    _name = 'fsn_sales_order_line'
    _description = 'FSN销售订单明细'
    # _rec_name = 'fsn_purchase_order_number'
    _order = "create_date desc"


    fsn_sales_order_id = fields.Many2one("fsn_sales_order", string="FSN销售订单", ondelete="cascade")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    # style_number_base = fields.Many2one("style_number_base", string="产品", required=True)
    fsn_color_id = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    # @api.onchange('style_number_base')
    # def _onchange_fsn_color_id_value(self):
    #     self.fsn_color_id = False
    #     if self.style_number_base:

    #         ib_detail_objs = self.env['ib.detail'].sudo().search([("style_number_base_id", "=", self.style_number_base.id)])

    #         fsn_color_id_list = ib_detail_objs.mapped("fsn_color.id")

    #         return {'domain': {'fsn_color_id': [('id', 'in', fsn_color_id_list)]}}
    #     else:
    #         return {'domain': {'fsn_color_id': []}}
        
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    quantity = fields.Integer(string="购买量")
    unit_price = fields.Float(string="单价")

    pre_tax_amount = fields.Float(string="税前小计", compute="set_pre_tax_amount", store=True)
    @api.depends("quantity", "unit_price", "quantity_returned")
    def set_pre_tax_amount(self):
        for record in self:
            # record.pre_tax_amount = record.unit_price * record.quantity
            quantity_to_subtract = record.quantity_returned or 0.0
            pre_tax_amount = record.unit_price * (record.quantity - quantity_to_subtract)
            record.pre_tax_amount = pre_tax_amount

    account_tax_ids = fields.Many2many("account.tax", string="税金设置")
    tax_amount = fields.Float(string="税费金额", compute="set_tax_amount", store=True)
    @api.depends("quantity", "unit_price", "account_tax_ids", 'quantity_returned')
    def set_tax_amount(self):
        for record in self:
            # total_tax = sum(record.account_tax_ids.filtered(lambda x: x.price_include == True).mapped("amount"))
            # record.tax_amount = (record.pre_tax_amount / (100 + total_tax)) * total_tax
            quantity_to_subtract = record.quantity_returned or 0.0
            quantity_for_tax = record.quantity - quantity_to_subtract
            total_tax = sum(record.account_tax_ids.filtered(lambda x: x.price_include == True).mapped("amount"))
            tax_amount = (record.unit_price * quantity_for_tax / (100 + total_tax)) * total_tax
            record.tax_amount = tax_amount


    amount = fields.Float(string="小计", compute="set_amount", store=True)
    @api.depends("pre_tax_amount", "tax_amount")
    def set_amount(self):
        for record in self:
            record.amount = record.pre_tax_amount - record.tax_amount


    quantity_returned = fields.Float(string="退货数量")
    completion_date = fields.Date(string="完成日期", required=True)

