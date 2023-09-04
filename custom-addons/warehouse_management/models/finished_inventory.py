from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FinishedProductWareLine(models.Model):
    '''成品仓管理明细'''
    _inherit = "finished_product_ware_line"


    finished_inventory_id = fields.Many2one("finished_inventory", string="成品仓库存", compute="set_finished_inventory_id", store=True)


    # 设置库存
    @api.depends('order_number', 'style_number', 'size', 'quality')
    def set_finished_inventory_id(self):
        for record in self:

            if record.order_number and record.style_number and record.size and record.quality:

                finished_inventory_obj = record.finished_inventory_id.sudo().search([
                    ("order_number", "=", record.order_number.id),     # 订单号
                    ("style_number", "=", record.style_number.id),    # 款号
                    ("size", "=", record.size.id),    # 尺码
                ])

                if finished_inventory_obj:
                    pass
                else:

                    finished_inventory_obj = record.finished_inventory_id.sudo().create({
                        "order_number": record.order_number.id,   # 订单号
                        "style_number": record.style_number.id,   # 款号
                        "size": record.size.id,   # 尺码
                    })
                record.finished_inventory_id = finished_inventory_obj.id


    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine, self).create(vals)

        res.set_finished_inventory_id()

        return res


class FinishedInventory(models.Model):
    _name = 'finished_inventory'
    _description = '成品仓库存'
    _rec_name = 'style_number'
    _order = "write_date desc"


    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "finished_inventory_id", string="成品仓管理明细")

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    # style_number_date
    fsn_color = fields.Many2one("fsn_color", string="颜色", compute="_set_fsn_color", store=True)
    # 设置颜色
    @api.depends('style_number')
    def _set_fsn_color(self):
        for record in self:
            record.fsn_color = record.style_number.fsn_color.id
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    quality = fields.Selection([('合格', '合格'), ('次品', '次品'), ('返修件', '返修件'), ('退货', '退货')], string="产品质量", default="合格")
    number = fields.Integer(string="总库存件数", compute="set_number", store=True)
    put_number = fields.Integer(string="总入库件数", compute="set_number", store=True)
    out_number = fields.Integer(string="总出库件数", compute="set_number", store=True)
    # 设置件数
    @api.depends('finished_product_ware_line_ids', 'finished_product_ware_line_ids.type', 'finished_product_ware_line_ids.state')
    def set_number(self):
        for record in self:

            record.put_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认").mapped('number'))

            record.out_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认").mapped('number'))

            record.number = record.put_number - record.out_number

    normal_number = fields.Integer(string="正常库存件数", compute="set_normal_number", store=True)
    normal_put_number = fields.Integer(string="正常入库件数", compute="set_normal_number", store=True)
    normal_out_number = fields.Integer(string="正常出库件数", compute="set_normal_number", store=True)
    # 设置正常库存件数
    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.type',\
            'finished_product_ware_line_ids.state',\
                'finished_product_ware_line_ids.quality',\
                    'finished_product_ware_line_ids.number',\
                        'finished_product_ware_line_ids.character')
    def set_normal_number(self):
        for record in self:

            record.normal_put_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and x.quality == "合格" and x.character == "正常").mapped('number'))

            record.normal_out_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and x.quality == "合格" and x.character == "正常").mapped('number'))

            record.normal_number = record.normal_put_number - record.normal_out_number
    
    defective_number = fields.Integer(string="报次库存件数", compute="set_defective_number", store=True)
    defective_put_number = fields.Integer(string="报次入库件数", compute="set_defective_number", store=True)
    defective_out_number = fields.Integer(string="报次出库件数", compute="set_defective_number", store=True)
    # 设置报次库存件数
    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.type',\
            'finished_product_ware_line_ids.state',\
                'finished_product_ware_line_ids.quality',\
                    'finished_product_ware_line_ids.number',\
                        'finished_product_ware_line_ids.character')
    def set_defective_number(self):
        for record in self:

            record.defective_put_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and (x.quality == "报次" or x.quality == "裁片报次")).mapped('number'))

            record.defective_out_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and (x.quality == "报次" or x.quality == "裁片报次")).mapped('number'))

            record.defective_number = record.defective_put_number - record.defective_out_number

    no_accomplish_number = fields.Integer(string="半成品库存件数", compute="set_no_accomplish_number", store=True)
    no_accomplish_put_number = fields.Integer(string="半成品入库件数", compute="set_no_accomplish_number", store=True)
    no_accomplish_out_number = fields.Integer(string="半成品出库件数", compute="set_no_accomplish_number", store=True)
    # 设置半成品库存件件数
    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.type',\
            'finished_product_ware_line_ids.state',\
                'finished_product_ware_line_ids.quality',\
                    'finished_product_ware_line_ids.number',\
                        'finished_product_ware_line_ids.character')
    def set_no_accomplish_number(self):
        for record in self:

            record.no_accomplish_put_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and x.quality == "半成品").mapped('number'))

            record.no_accomplish_out_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and x.quality == "半成品").mapped('number'))

            record.no_accomplish_number = record.no_accomplish_put_number - record.no_accomplish_out_number


    cutting_number = fields.Integer(string="裁片库存件数", compute="set_cutting_number", store=True)
    cutting_put_number = fields.Integer(string="裁片入库件数", compute="set_cutting_number", store=True)
    cutting_out_number = fields.Integer(string="裁片出库件数", compute="set_cutting_number", store=True)
    # 设置裁片库存件件数
    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.type',\
            'finished_product_ware_line_ids.state',\
                'finished_product_ware_line_ids.quality',\
                    'finished_product_ware_line_ids.number',\
                        'finished_product_ware_line_ids.character')
    def set_cutting_number(self):
        for record in self:

            record.cutting_put_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and x.quality == "裁片").mapped('number'))

            record.cutting_out_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and x.quality == "裁片").mapped('number'))

            record.cutting_number = record.cutting_put_number - record.cutting_out_number


    no_normal_number = fields.Integer(string="非正常库存件数", compute="set_no_normal_number", store=True)
    no_normal_put_number = fields.Integer(string="非正常入库件数", compute="set_no_normal_number", store=True)
    no_normal_out_number = fields.Integer(string="非正常出库件数", compute="set_no_normal_number", store=True)
    # 设置非正常库存件数
    @api.depends('out_number', 'normal_out_number', 'defective_out_number', 'put_number', 'normal_put_number', 'defective_put_number',\
        'no_accomplish_out_number', 'no_accomplish_put_number', 'cutting_put_number', 'cutting_out_number')
    def set_no_normal_number(self):
        for record in self:
            # 非正常出库 = 全部出库 - （正常出库 + 报次出库 + 半成品出库 + 裁片出库）
            record.no_normal_out_number = record.out_number - (record.normal_out_number + record.defective_out_number + record.no_accomplish_out_number)
            # 非正常入库 = 全部入库 - （正常入库 + 报次入库 + 半成品入库 + 裁片入库）
            record.no_normal_put_number = record.put_number - (record.normal_put_number + record.defective_put_number + record.no_accomplish_put_number)
            # 非正常件数 = 非正常入库 - 非正常出库
            record.no_normal_number = record.no_normal_put_number - record.no_normal_out_number


    customer_enter = fields.Integer(string="客户入库数", compute="set_customer_inventory_info", store=True)
    customer_out = fields.Integer(string="客户出库数", compute="set_customer_inventory_info", store=True)
    # 设置客户进程信息
    @api.depends('finished_product_ware_line_ids', 'finished_product_ware_line_ids.source_destination', 'finished_product_ware_line_ids.source_destination.type', 'finished_product_ware_line_ids.state')
    def set_customer_inventory_info(self):
        for record in self:

            record.customer_out = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.state == "确认" and x.type == "出库" and x.finished_product_ware_id.customer_id.type == "外部").mapped("number"))
            record.customer_enter = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.state == "确认" and x.type == "入库" and x.finished_product_ware_id.customer_id.type == "外部").mapped("number"))


    stock = fields.Integer(string="存量", compute="set_stock", store=True)
    delivery_quantity = fields.Integer(string="客户交付数量", compute="set_stock", store=True)
    # 设置存量和客户交付数量
    @api.depends('customer_out', 'customer_enter', 'number')
    def set_stock(self):
        for record in self:
            # 存量 = 客出 - 客入 + 总库存
            record.stock = record.customer_out - record.customer_enter + record.number
            # 客户交付数量 = 客出 - 客入
            record.delivery_quantity = record.customer_out - record.customer_enter
    

    normal_inventory_number = fields.Integer(string="库存（合格）", compute="set_statistics_info", store=True)
    abnormal_inventory_number = fields.Integer(string="库存（不合格）", compute="set_statistics_info", store=True)

    put_storage_qualified = fields.Integer(string="入库（合格）", compute="set_statistics_info", store=True)
    outbound_storage_qualified = fields.Integer(string="出库（合格）", compute="set_statistics_info", store=True)
    put_storage_not_qualified = fields.Integer(string="入库（不合格）", compute="set_statistics_info", store=True)
    outbound_storage_not_qualified = fields.Integer(string="出库（不合格）", compute="set_statistics_info", store=True)
    @api.depends('finished_product_ware_line_ids',\
        'finished_product_ware_line_ids.type',\
            'finished_product_ware_line_ids.state',\
                'finished_product_ware_line_ids.quality',\
                    'finished_product_ware_line_ids.character')
    def set_statistics_info(self):
        for record in self:

            record.put_storage_qualified = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and x.quality == "合格").mapped('number'))

            record.outbound_storage_qualified = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and x.quality == "合格").mapped('number'))
        
            record.normal_inventory_number = record.put_storage_qualified - record.outbound_storage_qualified

            record.put_storage_not_qualified = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "入库" and x.state == "确认" and x.quality == "次品").mapped('number'))

            record.outbound_storage_not_qualified = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.type == "出库" and x.state == "确认" and x.quality == "次品").mapped('number'))

            record.abnormal_inventory_number = record.put_storage_not_qualified - record.outbound_storage_not_qualified