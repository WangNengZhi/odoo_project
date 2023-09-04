from odoo.exceptions import ValidationError
from odoo import models, fields, api



class OrderCost(models.Model):
    _name = 'order_cost'
    _description = '单件成本'
    _rec_name = 'style_number_id'
    _order = "order_id desc"

    order_id = fields.Many2one("sale_pro.sale_pro", string="订单编号", required=True, ondelete="cascade")
    style_number_id = fields.Many2one('ib.detail', string='款号', required=True, ondelete="cascade")
    material_cost = fields.Float(string="物料", digits=(16, 5))
    special_process_cost = fields.Float(string="特殊工艺", digits=(16, 5))
    wages_cost = fields.Float(string="工价", digits=(16, 5))
    accept_order_cost = fields.Float(string="接单价", digits=(16, 5), compute="set_order_info", store=True)
    contract_price = fields.Float(string="合同价格", digits=(16, 5), compute="set_order_info", store=True)
    sell_price = fields.Float(string="售价", digits=(16, 5))



    @api.depends('order_id', 'order_id.order_price', 'order_id.contract_price')
    def set_order_info(self):
        for record in self:
            record.accept_order_cost = record.order_id.order_price  # 接单价
            record.contract_price = record.order_id.contract_price  # 合同价格


    # 获取物料成本和特殊工艺成本
    def set_material_cost(self):
        for record in self:
            # 生产工单
            manufacturing_order_obj = self.env["manufacturing_order"].sudo().search([("order_serial_number", "=", record.order_id.id)])
            # 生产工单明细过滤
            manufacturing_order_line_objs = manufacturing_order_obj.manufacturing_order_line_ids.sudo().filtered(lambda x: x.style_number.id == record.style_number_id.id)

            record.material_cost = sum(manufacturing_order_line_objs.manufacturing_bom_ids.sudo().mapped('price'))
            record.special_process_cost = sum(manufacturing_order_line_objs.manufacturing_special_process_ids.sudo().mapped('price'))


    # 设置工价成本
    def set_wages_cost(self):
        for record in self:
            # 查询工序单
            work_work_objs = self.env["work.work"].sudo().search([("order_number", "=", record.style_number_id.id)])

            record.wages_cost = sum(work_work_objs.sudo().mapped('standard_price'))




class SalePro(models.Model):
    _inherit = "sale_pro.sale_pro"


    order_cost_ids = fields.One2many("order_cost", "order_id", string="订单成本")



class SaleProLine(models.Model):
    _inherit = "sale_pro_line"

    order_cost_id = fields.Many2one("order_cost", string="订单成本")


    @api.model
    def create(self, vals):

        rec = super(SaleProLine, self).create(vals)

        rec.sudo().create_order_cost()

        return rec

    # 创建订单成本
    def create_order_cost(self):

        for record in self:

            record.order_cost_id.sudo().create({
                "order_id": record.sale_pro_id.id,   # 订单id
                "style_number_id": record.style_number.id,     # 款号id
                "accept_order_cost": float(record.sale_pro_id.order_price),    # 接单价
                "contract_price": record.sale_pro_id.contract_price,     # 合同价格
            })