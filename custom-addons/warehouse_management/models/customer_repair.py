from odoo import models, fields, api


class CustomerRepair(models.Model):
    _name = 'customer_repair'
    _description = '客户返修'
    _rec_name = 'number_no'
    _order = "date desc"


    date = fields.Date('日期')
    number_delivery = fields.Char('出库单号')
    inbound_order_number = fields.Char('入库单号')
    client_name = fields.Char('客户名称')
    number_no = fields.Many2one('sale_pro.sale_pro', '订单')
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
    customer_repair_line_ids = fields.One2many('customer_repair_line', 'customer_repair_id', string='入库与出库数量')


    # 设置到仓件数/出仓件数/库存件数
    @api.depends("customer_repair_line_ids")
    def _set_inventory_number(self):
        for record in self:
            # 临时到仓件数
            tem_arrival_number = 0
            # 临时出仓件数
            tem_out_of_warehouse_number = 0
            # 临时库存件数
            tem_number_of_inventory = 0
            for line in record.customer_repair_line_ids:

                tem_arrival_number = tem_arrival_number + line.warehousing_total

                tem_out_of_warehouse_number = tem_out_of_warehouse_number + line.out_of_total

            tem_number_of_inventory = tem_arrival_number - tem_out_of_warehouse_number

            record.write({
                "arrival_number": tem_arrival_number,
                "out_of_warehouse_number": tem_out_of_warehouse_number,
                "number_of_inventory": tem_number_of_inventory
            })














class CustomerRepairLine(models.Model):
    _name = 'customer_repair_line'
    _description = '客户返修明细'
    _rec_name = 'item_number'
    _order = "date desc"


    customer_repair_id = fields.Many2one("customer_repair")
    date = fields.Date('日期')
    item_number = fields.Many2one('ib.detail', '款号')
    color = fields.Char('颜色')
    manage = fields.Char('管理员')
    inspector = fields.Char('验布员')
    coustm = fields.Char('客户')

    out_of_stock_xs = fields.Integer('出库XS')
    out_of_stock_s = fields.Integer('出库S')
    out_of_stock_m = fields.Integer('出库M')
    out_of_stock_l = fields.Integer('出库L')
    out_of_stock_xl = fields.Integer('出库XL')
    out_of_stock_two_xl = fields.Integer('出库2XL')
    out_of_stock_three_xl = fields.Integer('出库3XL')
    out_of_stock_repair_parts = fields.Integer('出库疵品/返修件')
    out_of_total = fields.Integer(string='出库总数', compute="_set_out_of_total", store=True)

    reality_tailor = fields.Integer(string="实裁数量")



    def _set_data(self):

        objs = self.env["inbound.outbound"].sudo().search([
            ("item_number", "=", self.item_number.id)
        ])

        tem_out_of_stock_xs = 0
        tem_out_of_stock_s = 0
        tem_out_of_stock_m = 0
        tem_out_of_stock_l = 0
        tem_out_of_stock_xl = 0
        tem_out_of_stock_two_xl = 0
        tem_out_of_stock_three_xl = 0
        tem_out_of_stock_repair_parts = 0
        tem_out_of_total = 0

        for obj in objs:

            if obj.out_of_total < 0:

                tem_out_of_stock_xs = tem_out_of_stock_xs + abs(obj.out_of_stock_xs)
                tem_out_of_stock_s = tem_out_of_stock_s + abs(obj.out_of_stock_s)
                tem_out_of_stock_m = tem_out_of_stock_m + abs(obj.out_of_stock_m)
                tem_out_of_stock_l = tem_out_of_stock_l + abs(obj.out_of_stock_l)
                tem_out_of_stock_xl = tem_out_of_stock_xl + abs(obj.out_of_stock_xl)
                tem_out_of_stock_two_xl = tem_out_of_stock_two_xl + abs(obj.out_of_stock_two_xl)
                tem_out_of_stock_three_xl = tem_out_of_stock_three_xl + abs(obj.out_of_stock_three_xl)
                tem_out_of_stock_repair_parts = tem_out_of_stock_repair_parts + abs(obj.out_of_stock_repair_parts)

                tem_out_of_total = tem_out_of_total + abs(obj.out_of_total)

        self.write({
            "out_of_stock_xs": tem_out_of_stock_xs,    # XS
            "out_of_stock_s": tem_out_of_stock_s,     # S
            "out_of_stock_m": tem_out_of_stock_m,    # M
            "out_of_stock_l": tem_out_of_stock_l,    # L
            "out_of_stock_xl": tem_out_of_stock_xl,  # XL
            "out_of_stock_two_xl": tem_out_of_stock_two_xl,    # XXL
            "out_of_stock_three_xl": tem_out_of_stock_three_xl,    # XXXL
            "out_of_stock_repair_parts": tem_out_of_stock_repair_parts,    #
            "out_of_total": tem_out_of_total,  # 总数
        })
