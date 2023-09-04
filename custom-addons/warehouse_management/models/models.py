# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api


class warehouse_management(models.Model):
    _name = 'warehouse_management'
    _description = '仓库管理'
    _rec_name = 'number_no'
    _order = "date desc"

    date = fields.Date('日期', required=True)
    type = fields.Selection([('扫码', '扫码'), ('人工', '人工')], string="类型", default="人工")
    number_delivery = fields.Char('出库单号')
    inbound_order_number = fields.Char('入库单号')
    client_name = fields.Char('客户名称', store=True)
    number_no = fields.Many2one('sale_pro.sale_pro', string='订单', required=True)
    customer_id = fields.Many2one("fsn_customer", string='客户名称', related="number_no.customer_id", store=True)
    color = fields.Char('颜色')
    arrival_time = fields.Date('到仓时间')
    out_of_warehouse_time = fields.Date('出仓时间')
    arrival_number = fields.Integer('到仓件数', compute="_set_inventory_number", store=True)
    out_of_warehouse_number = fields.Integer('出仓件数', compute="_set_inventory_number", store=True)
    number_of_inventory = fields.Integer('库存件数', compute="_set_inventory_number", store=True)
    inbound_sender = fields.Char('入库送件人')
    inbound_recipient = fields.Char('入库收件人')
    outgoer = fields.Char('出库人')
    receiving_customers = fields.Char('接收客户')
    remark = fields.Char('备注')

    inbound_and_outbound = fields.Many2many('inbound.outbound', string='入库与出库数量')

    inbound_outbound_ids = fields.One2many("inbound.outbound", "warehouse_management_id", string="仓库管理明细")



    @api.constrains('inbound_and_outbound')
    def _check_unique(self):

        for record in self:

            for inbound_outbound_id in record.inbound_and_outbound:

                if record.number_no != inbound_outbound_id.style_number:
                    raise ValidationError(f"不允许填写不相同订单的明细记录！")


    # # 设置订单和客户名称
    # @api.depends("inbound_and_outbound")
    # def _set_client_name(self):

    #     for record in self:

    #         for inbound_outbound_id in record.inbound_and_outbound:

    #             record.number_no = inbound_outbound_id.style_number

    #             record.client_name = inbound_outbound_id.style_number.name


    # 计算到仓库明细的出仓价格（款号价格*出仓件数）
    def compute_out_of_warehouse_number_price(self):
        total_price = 0
        for inbound_and_outbound_obj in self.inbound_and_outbound:

            unit_price = inbound_and_outbound_obj.item_number.price * inbound_and_outbound_obj.out_of_total

            total_price = total_price + unit_price

        return total_price



    # 计算到仓库明细的到仓价格（款号价格*到仓件数）
    def compute_arrival_number_price(self):
        total_price = 0
        for inbound_and_outbound_obj in self.inbound_and_outbound:

            unit_price = inbound_and_outbound_obj.item_number.price * inbound_and_outbound_obj.warehousing_total

            total_price = total_price + unit_price

        return total_price


    # 设置盘点模块的运营数据(创建和写入时使用)
    def set_operate_data(self):

        date = str(self.date)
        date = date[0:7]

        fsn_operate_objs = self.env["fsn_operate"].sudo().search([
            ("month", "=", date)
        ])

        if fsn_operate_objs:
            fsn_operate_objs.sudo().set_enter_warehouse()
            fsn_operate_objs.sudo().set_out_of_warehouse()
        else:
            new_obj = fsn_operate_objs.sudo().create({
                "month": date,
            })
            new_obj.sudo().set_enter_warehouse()
            new_obj.sudo().set_out_of_warehouse()


    # 减少盘点模块的运营数据(删除时使用)
    def reduce_operate_data(self):

        date = str(self.date)
        date = date[0:7]

        fsn_operate_objs = self.env["fsn_operate"].sudo().search([
            ("month", "=", date)
        ])
        fsn_operate_objs.write({
            "enter_warehouse": fsn_operate_objs.enter_warehouse - self.compute_arrival_number_price(),
            "out_of_warehouse": fsn_operate_objs.out_of_warehouse - self.compute_out_of_warehouse_number_price()
        })



    def write(self, vals):
        res = super(warehouse_management, self).write(vals)
        if 'inbound_and_outbound' in vals:

            # 修改同步运营数据
            self.set_operate_data()
        return res


    @api.model
    def create(self, vals):

        res = super(warehouse_management, self).create(vals)

        # 创建完成后同步运营数据
        res.set_operate_data()

        return res


    def unlink(self):
        for record in self:

            # 删除时同步盘点模块的运营数据
            record.reduce_operate_data()

        return super(warehouse_management, self).unlink()


    @api.onchange("date", "number_no")
    def set_inbound_and_outbound(self):
        if self.number_no and self.date:

            return {'domain': {'inbound_and_outbound': [("date", "=", self.date), ("style_number", "=", self.number_no.id)]}}




    # 设置到仓件数/出仓件数/库存件数
    @api.depends("inbound_and_outbound")
    def _set_inventory_number(self):
        for record in self:

            # 临时到仓件数
            tem_arrival_number = 0
            # 临时出仓件数
            tem_out_of_warehouse_number = 0
            # 临时库存件数
            tem_number_of_inventory = 0

            if record.inbound_and_outbound:

                for line in record.inbound_and_outbound:

                    tem_arrival_number = tem_arrival_number + line.warehousing_total

                    tem_out_of_warehouse_number = tem_out_of_warehouse_number + line.out_of_total

                tem_number_of_inventory = tem_arrival_number - tem_out_of_warehouse_number

                record.write({
                    "arrival_number": tem_arrival_number,
                    "out_of_warehouse_number": tem_out_of_warehouse_number,
                    "number_of_inventory": tem_number_of_inventory
                })

            else:
                record.write({
                    "arrival_number": tem_arrival_number,
                    "out_of_warehouse_number": tem_out_of_warehouse_number,
                    "number_of_inventory": tem_number_of_inventory
                })



class inbound_and_outbound_quantity(models.Model):
    _name = 'inbound.outbound'
    _description = '入库与出库数量'
    _rec_name = 'item_number'
    _order = "date desc"


    warehouse_management_id = fields.Many2one("warehouse_management", string="仓库管理id")
    date = fields.Date('日期', required=True)
    style_number = fields.Many2one('sale_pro.sale_pro', string="订单", required=True)
    item_number = fields.Many2one('ib.detail', string="款号", required=True)
    color = fields.Char('颜色', related="item_number.color", store=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="item_number.fsn_color", store=True)
    manage = fields.Char('管理员')
    inspector = fields.Char('验布员')
    customer_id = fields.Many2one("fsn_customer", string='客户名称', related="style_number.customer_id", store=True)
    # coustm = fields.Char(string="客户", related="warehouse_management_id.client_name", store=True)
    warehousing_xs = fields.Integer('入库XS')
    warehousing_s = fields.Integer('入库S')
    warehousing_m = fields.Integer('入库M')
    warehousing_l = fields.Integer('入库L')
    warehousing_xl = fields.Integer('入库XL')
    warehousing_two_xl = fields.Integer('入库2XL')
    warehousing_three_xl = fields.Integer('入库3XL')
    warehousing_four_xl = fields.Integer('入库4XL')
    warehousing_repair_parts = fields.Integer('入库疵品/返修件')
    warehousing_total = fields.Integer(string='入库总数', compute="_set_warehousing_total", store=True)

    out_of_stock_xs = fields.Integer('出库XS')
    out_of_stock_s = fields.Integer('出库S')
    out_of_stock_m = fields.Integer('出库M')
    out_of_stock_l = fields.Integer('出库L')
    out_of_stock_xl = fields.Integer('出库XL')
    out_of_stock_two_xl = fields.Integer('出库2XL')
    out_of_stock_three_xl = fields.Integer('出库3XL')
    out_of_stock_four_xl = fields.Integer('出库4XL')
    out_of_stock_repair_parts = fields.Integer('出库疵品/返修件')
    out_of_total = fields.Integer(string='出库总数', compute="_set_out_of_total", store=True)



    # @api.depends("item_number")
    # def _set_style_number(self):
    #     for record in self:
    #         record.style_number = record.item_number.order_id


    # 计算入库总数
    @api.depends("warehousing_xs", "warehousing_s", "warehousing_m", "warehousing_l", "warehousing_xl", "warehousing_two_xl", "warehousing_three_xl", "warehousing_repair_parts", "warehousing_four_xl")
    def _set_warehousing_total(self):
        for record in self:

            record.warehousing_total = record.warehousing_xs + record.warehousing_s + record.warehousing_m + record.warehousing_l + record.warehousing_xl + record.warehousing_two_xl + record.warehousing_three_xl + record.warehousing_four_xl + record.warehousing_repair_parts

    # 计算出库总数
    @api.depends("out_of_stock_xs", "out_of_stock_s", "out_of_stock_m", "out_of_stock_l", "out_of_stock_xl", "out_of_stock_two_xl", "out_of_stock_three_xl", "out_of_stock_repair_parts", "out_of_stock_four_xl")
    def _set_out_of_total(self):

        for record in self:

            record.out_of_total = record.out_of_stock_xs + record.out_of_stock_s + record.out_of_stock_m + record.out_of_stock_l + record.out_of_stock_xl + record.out_of_stock_two_xl + record.out_of_stock_three_xl + record.out_of_stock_four_xl + record.out_of_stock_repair_parts

    # 设置款号件数汇总数据
    def set_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.item_number.id)
        ])
        if style_number_summary_objs:
            style_number_summary_objs.sudo().set_enter_warehouse()  # 入仓
            style_number_summary_objs.sudo().set_out_of_warehouse()     # 出仓
        else:
            new_obj = style_number_summary_objs.sudo().create({
                "style_number": self.item_number.id,
            })
            new_obj.sudo().set_enter_warehouse()  # 入仓
            new_obj.sudo().set_out_of_warehouse()     # 出仓


    # 减少款号件数汇总数据(删除时使用)
    def reduce_style_number_summary(self):


        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.item_number.id)
        ])

        style_number_summary_objs.write({
            "enter_warehouse": style_number_summary_objs.enter_warehouse - self.warehousing_total,     # 入仓
            "out_of_warehouse": style_number_summary_objs.out_of_warehouse - self.out_of_total   # 出仓
        })



    # 设置客户返修数据
    def _set_customer_repair_line(self):
        for record in self:

            objs = self.env["customer_repair_line"].sudo().search([
                ("item_number", "=", record.item_number.id)
                ])

            if objs:

                # 判断是否是返修
                if record.out_of_total < 0:
                    objs._set_data()

            else:
                new_obj = objs.sudo().create({
                    "date": record.date,
                    "item_number": record.item_number.id,
                    "color": record.color,
                    "coustm": record.coustm,
                })
                # 判断是否是返修
                if self.out_of_total < 0:
                    new_obj._set_data()













    def reduce_customer_repair_line(self):

        # 判断是否是返修
        if self.out_of_total < 0:

            obj = self.env["customer_repair_line"].sudo().search([
                ("item_number", "=", self.item_number.id)
            ])

            obj.sudo().write({
                "out_of_stock_xs": obj.out_of_stock_xs + self.out_of_stock_xs,    # XS
                "out_of_stock_s": obj.out_of_stock_s + self.out_of_stock_s,     # S
                "out_of_stock_m": obj.out_of_stock_m + self.out_of_stock_m,    # M
                "out_of_stock_l": obj.out_of_stock_l + self.out_of_stock_l,    # L
                "out_of_stock_xl": obj.out_of_stock_xl + self.out_of_stock_xl,  # XL
                "out_of_stock_two_xl": obj.out_of_stock_two_xl + self.out_of_stock_two_xl,    # XXL
                "out_of_stock_three_xl": obj.out_of_stock_three_xl + self.out_of_stock_three_xl,    # XXXL
                "out_of_stock_four_xl": obj.out_of_stock_four_xl + self.out_of_stock_four_xl,    # XXXL
                "out_of_stock_repair_parts": obj.out_of_stock_repair_parts + self.out_of_stock_repair_parts,    #
                "out_of_total": obj.out_of_total + self.out_of_total  # 总数
            })








    def write(self, vals):

        tem_id = self.item_number.id

        res = super(inbound_and_outbound_quantity, self).write(vals)

        # 设置款号件数汇总数据
        # self.set_style_number_summary()
        # 设置客户返修数据
        self._set_customer_repair_line()

        # obj = self.env["style_number_summary"].sudo().search([("style_number", "=", tem_id)])

        # if "item_number" in vals:

        #     obj.sudo().set_enter_warehouse()  # 入仓
        #     obj.sudo().set_out_of_warehouse()     # 出仓

        return res




    @api.model
    def create(self, vals):

        instance = super(inbound_and_outbound_quantity, self).create(vals)

        # 设置款号件数汇总数据
        # instance.set_style_number_summary()
        # 设置客户返修数据
        instance._set_customer_repair_line()

        return instance


    def unlink(self):

        tem_list = []

        for record in self:

            # record.reduce_style_number_summary()

            tem_list.append([record.item_number.id, record.out_of_total])


        res = super(inbound_and_outbound_quantity, self).unlink()

        # 删除时，同步客户返修数据
        for tem_obj in tem_list:
            if tem_obj[1] < 0:
                obj = self.env["customer_repair_line"].sudo().search([("item_number", "=", tem_obj[0])])
                obj._set_data()

        return res