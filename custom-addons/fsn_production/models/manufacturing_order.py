from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalePro(models.Model):
    """ 继承订单"""
    _inherit = 'sale_pro.sale_pro'

    manufacturing_order_id = fields.Many2one("manufacturing_order", string="生产订单id")


    # 创建生产订单
    def create_manufacturing_order(self):
        manufacturing_order_obj = self.manufacturing_order_id.sudo().create({
            "order_serial_number": self.id,
            "client": self.name,
        })
        self.manufacturing_order_id = manufacturing_order_obj.id

        line_list = []


        for sale_pro_line in self.sale_pro_line_ids:
            for voucher_detail in sale_pro_line.voucher_details:
                line = {
                    "style_number": sale_pro_line.style_number.id,  # 款号
                    "size": voucher_detail.size.id,     # 尺码
                    "number": voucher_detail.number,    # 件数
                }
                line_list.append((0, 0, line))

        self.manufacturing_order_id.write({
            "manufacturing_order_line_ids": line_list
        })


    # 创建生产订单(弃用)
    def create_manufacturing_order1(self):

        manufacturing_order_obj = self.manufacturing_order_id.sudo().create({
            "order_serial_number": self.id,
            "client": self.name,
        })
        self.manufacturing_order_id = manufacturing_order_obj.id

        line_list = []

        def set_date(line_list, record, size, number):
            fsn_size_id = self.env["fsn_size"].sudo().search([("name", "=", size)]).id
            line = {
                "style_number":record.id,
                "size": fsn_size_id,
                "number": number
            }
            line_list.append((0, 0, line))

        for record in self.ib_detail_ids:
            if record.z_xs:
                set_date(line_list, record, "XS", record.z_xs)
            if record.z_s:
                set_date(line_list, record, "S", record.z_s)
            if record.z_m:
                set_date(line_list, record, "M", record.z_m)
            if record.z_l:
                set_date(line_list, record, "L", record.z_l)
            if record.z_xl:
                set_date(line_list, record, "XL", record.z_xl)
            if record.z_two_xl:
                set_date(line_list, record, "XXL", record.z_two_xl)
            if record.z_three_xl:
                set_date(line_list, record, "XXXL", record.z_three_xl)
            if record.z_four_xl:
                set_date(line_list, record, "XXXXL", record.z_four_xl)
            if record.z_five_xl:
                set_date(line_list, record, "XXXXXL", record.z_five_xl)

        self.manufacturing_order_id.write({
            "manufacturing_order_line_ids": line_list
        })







class ManufacturingOrder(models.Model):
    _name = 'manufacturing_order'
    _description = 'FSN生产工单'
    _rec_name = 'order_serial_number'
    _order = "create_date desc"


    order_serial_number = fields.Many2one("sale_pro.sale_pro", string="销售订单")
    state = fields.Selection([('草稿', '草稿'), ('确认', '确认'), ('进行中', '进行中'), ('完成', '完成'), ('报废', '报废')], string="状态", default="草稿", required=True)

    client = fields.Char(string="客户(旧)")
    client_id = fields.Many2one("fsn_customer", string="客户", related="order_serial_number.customer_id", store=True)
    principal = fields.Many2one("hr.employee", string="生产负责人")

    price = fields.Float(string="价格", compute="_value_price", store=True, digits=(16, 5))

    manufacturing_order_line_ids = fields.One2many("manufacturing_order_line", "manufacturing_order", string="生产工单明细")


    # 计算价格
    @api.depends('manufacturing_order_line_ids', 'manufacturing_order_line_ids.price')
    def _value_price(self):
        for record in self:
            record.price = sum(self.manufacturing_order_line_ids.mapped('price'))























