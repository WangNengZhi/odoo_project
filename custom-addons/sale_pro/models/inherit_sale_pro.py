from odoo import fields, models, api
from odoo.exceptions import ValidationError



class InheritSalePro(models.Model):
    _inherit = "sale_pro.sale_pro"


    sale_pro_line_ids = fields.One2many("sale_pro_line", "sale_pro_id", string="销售订单明细")

    sum_voucher_count = fields.Integer(string="总制单数", compute="set_sum_voucher_count", store=True)
    @api.depends("sale_pro_line_ids", "sale_pro_line_ids.voucher_count")
    def set_sum_voucher_count(self):
        for record in self:
            record.sum_voucher_count = sum(record.sale_pro_line_ids.mapped("voucher_count"))


class SaleProLine(models.Model):
    _name = 'sale_pro_line'
    _description = '销售订单明细'
    _rec_name = 'style_number'


    sale_pro_id = fields.Many2one("sale_pro.sale_pro", string="销售订单", ondelete="cascade")

    # 新加
    voucher_details_id = fields.Many2one("voucher_details", string="销售制单详情", ondelete="cascade")

    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    style_number_base = fields.Char(string="款号前缀", related="style_number.style_number_base", store=True)

    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)

    unit_price = fields.Float(string="单价", compute="_value_unit_price", store=True)


    @api.depends('sale_pro_id', 'sale_pro_id.order_price')
    def _value_unit_price(self):
        for record in self:
            record.unit_price = float(record.sale_pro_id.order_price)

    state = fields.Selection([
        ('未上线', '未上线'),
        ('未完成', '未完成'),
        ('已完成', '已完成'),
        ('退单', '退单')
        ], string="状态", default="未完成")
    
    voucher_count = fields.Float(string="制单合计", compute="_set_voucher_count", store=True)

    actual_cutting_count = fields.Float(string="实裁合计", compute="_set_actual_cutting_count", store=True)

    plan_actual_cutting_count = fields.Float(string="计划实裁合计", compute="_set_plan_actual_cutting_count", store=True)


    actual_cutting_price = fields.Float(string="价格", compute="_set_actual_cutting_price", store=True)


    voucher_details = fields.One2many("voucher_details", "sale_pro_line_id", string="制单详情")


    actual_cutting_details = fields.One2many("actual_cutting_details", "sale_pro_line_id", string="实裁详情")

    plan_actual_cutting_details = fields.One2many("plan_actual_cutting_details", "sale_pro_line_id", string="计划实裁详情")

    sale_pro_bar_code_ids = fields.One2many("sale_pro_bar_code", "sale_pro_line_id", string="条码详情")


    @api.constrains('sale_pro_id', 'style_number')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('sale_pro_id', '=', record.sale_pro_id.id), ('style_number', '=', record.style_number.id)])
            if len(demo) > 1:
                raise ValidationError(f"订单明细中存在重复款号！")


    # 设置制单合计
    @api.depends('voucher_details', 'voucher_details.number')
    def _set_voucher_count(self):
        for record in self:
            record.voucher_count = sum(record.voucher_details.mapped('number'))

    
    # 设置实裁合计
    @api.depends('actual_cutting_details', 'actual_cutting_details.number')
    def _set_actual_cutting_count(self):
        for record in self:
            record.actual_cutting_count = sum(record.actual_cutting_details.mapped('number'))

    # 设置计划实裁合计
    @api.depends('plan_actual_cutting_details', 'plan_actual_cutting_details.number')
    def _set_plan_actual_cutting_count(self):
        for record in self:
            record.plan_actual_cutting_count = sum(record.plan_actual_cutting_details.mapped('number'))

    # 设置价格
    @api.depends('unit_price', 'actual_cutting_count')
    def _set_actual_cutting_price(self):
        for record in self:
            record.actual_cutting_price = record.unit_price * record.actual_cutting_count


    def action_chargeback(self):
        ''' 退单'''
        for record in self:
            record.state = "退单"

    def action_cancel_chargeback(self):
        ''' 取消退单'''
        for record in self:
            record.state = "未完成"




class VoucherDetails(models.Model):
    _name = 'voucher_details'
    _description = '销售制单详情'

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="销售订单明细", ondelete="cascade")


    size = fields.Many2one("fsn_size", string="尺码", required=True)

    number = fields.Integer(string="件数")


    @api.constrains('size', 'sale_pro_line_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('sale_pro_line_id', '=', record.sale_pro_line_id.id), ('size', '=', record.size.id)])
            if len(demo) > 1:
                raise ValidationError(f"尺码为：{record.size.name}的记录重复！")


class ActualCuttingDetails(models.Model):
    _name = 'actual_cutting_details'
    _description = '销售实裁详情'

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="销售订单明细", ondelete="cascade")

    size = fields.Many2one("fsn_size", string="尺码", required=True)

    number = fields.Integer(string="件数")

    @api.constrains('size', 'sale_pro_line_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('sale_pro_line_id', '=', record.sale_pro_line_id.id), ('size', '=', record.size.id)])
            if len(demo) > 1:
                raise ValidationError(f"尺码为：{record.size.name}的记录重复！")



class PlanActualCuttingDetails(models.Model):
    _name = 'plan_actual_cutting_details'
    _description = '销售计划实裁详情'

    sale_pro_line_id = fields.Many2one("sale_pro_line", string="销售订单明细", ondelete="cascade")

    size = fields.Many2one("fsn_size", string="尺码", required=True)

    number = fields.Integer(string="件数")


    @api.constrains('size', 'sale_pro_line_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('sale_pro_line_id', '=', record.sale_pro_line_id.id), ('size', '=', record.size.id)])
            if len(demo) > 1:
                raise ValidationError(f"尺码为：{record.size.name}的记录重复！")



class SaleProBarCode(models.Model):
    _name = 'sale_pro_bar_code'
    _description = '销售条码详情'
    _order = "create_date desc"


    sale_pro_id = fields.Many2one("sale_pro.sale_pro", string="销售订单")
    sale_pro_line_id = fields.Many2one("sale_pro_line", string="销售订单明细")
    style_number = fields.Many2one('ib.detail', string='款号')
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    barcode_data = fields.Text(string="条形码数据")


    @api.constrains('sale_pro_id', 'style_number', 'size')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('sale_pro_id', '=', record.sale_pro_id.id), ('style_number', '=', record.style_number.id), ('size', '=', record.size.id)])
            if len(demo) > 1:
                raise ValidationError(f"记录重复！")


    def crete_goods_info(self):
        # 柜台销售创建商品信息
        if "goods_info" in self.env:

            goods_info_obj = self.env["goods_info"].sudo().search([("product_barcode", "=", self.barcode_data)])
            if not goods_info_obj:
                goods_info_obj = self.env["goods_info"].sudo().create({
                    "style_number": self.style_number.id,   # 款号
                    "fsn_color": self.fsn_color.id,     # 颜色
                    "size": self.size.id,   # 尺码
                })
                goods_info_obj.product_barcode = self.barcode_data    # 条码数据


    def set_barcode_data(self):
        for record in self:
        
            if record.sale_pro_id and record.style_number and record.size:
                region = "693"  # 地区
                client_number = record.sale_pro_id.customer_id.customer_number     # 客户代码
                style_number = record.style_number.style_number    # 款号
                size = '%6s' % record.size.name
                size = size.replace(" ", "0")   # 尺码


                record.barcode_data = f"{region}{client_number}{style_number}{size}0"

                if record.barcode_data:
                    record.crete_goods_info()
            else:
                raise ValidationError(f"缺少关键信息，不可生成条码数据！")
            


