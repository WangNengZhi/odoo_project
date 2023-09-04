import calendar, datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api

# 订单
class InheritSalePro(models.Model):
    _inherit = "sale_pro.sale_pro"


    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")


    def set_fsn_operate_id(self):
        for record in self:

            year = record.date.year
            month = '%02d' % record.date.month

            year_month = f"{year}-{month}"

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if fsn_operate_obj:
                pass
            else:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id


    @api.model
    def create(self, vals):

        res = super(InheritSalePro,self).create(vals)

        res.set_fsn_operate_id()

        return res
    
# 裁床产值
class CuttingBed(models.Model):
    _inherit = "cutting_bed"

    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")

    def set_fsn_operate_id(self):
        for record in self:

            year = record.date.year
            month = '%02d' % record.date.month
            year_month = f"{year}-{month}"


            if record.fsn_operate_id:
                temp_fsn_operate_obj = record.fsn_operate_id
            else:
                temp_fsn_operate_obj = False

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if not fsn_operate_obj:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id
            if temp_fsn_operate_obj:
                temp_fsn_operate_obj.set_cutting_bed()


    @api.model
    def create(self, vals):

        res = super(CuttingBed, self).create(vals)

        res.set_fsn_operate_id()

        return res
    

# 组产值
class product(models.Model):
    _inherit = "pro.pro"

    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")


    def set_fsn_operate_id(self):
        for record in self:

            year = record.date.year
            month = '%02d' % record.date.month
            year_month = f"{year}-{month}"


            if record.fsn_operate_id:
                temp_fsn_operate_obj = record.fsn_operate_id
            else:
                temp_fsn_operate_obj = False

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if not fsn_operate_obj:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id
            if temp_fsn_operate_obj:
                temp_fsn_operate_obj.set_workshop()


    @api.model
    def create(self, vals):

        res = super(product, self).create(vals)

        res.set_fsn_operate_id()

        return res


# 外发产值
class OutgoingOutput(models.Model):
    _inherit = "outgoing_output"

    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")



    def set_fsn_operate_id(self):
        for record in self:

            year = record.date.year
            month = '%02d' % record.date.month
            year_month = f"{year}-{month}"

            if record.fsn_operate_id:
                temp_fsn_operate_obj = record.fsn_operate_id
            else:
                temp_fsn_operate_obj = False

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if not fsn_operate_obj:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})
            record.fsn_operate_id = fsn_operate_obj.id
            if temp_fsn_operate_obj:
                temp_fsn_operate_obj.set_outbound()


    @api.model
    def create(self, vals):

        res = super(OutgoingOutput, self).create(vals)

        res.set_fsn_operate_id()

        return res


# 后道产值
class PosteriorPassageOutputValue(models.Model):
    _inherit = "posterior_passage_output_value"

    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")


    def set_fsn_operate_id(self):
        for record in self:

            year = record.date.year
            month = '%02d' % record.date.month
            year_month = f"{year}-{month}"


            if record.fsn_operate_id:
                temp_fsn_operate_obj = record.fsn_operate_id
            else:
                temp_fsn_operate_obj = False

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if not fsn_operate_obj:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id
            if temp_fsn_operate_obj:
                temp_fsn_operate_obj.set_posterior_passage()



    @api.model
    def create(self, vals):

        res = super(PosteriorPassageOutputValue, self).create(vals)

        res.set_fsn_operate_id()

        return res


# 出入库
class FinishedProductWareLine(models.Model):
    _inherit = "finished_product_ware_line"


    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")



    def set_fsn_operate_id(self):
        for record in self:
            year = record.date.year
            month = '%02d' % record.date.month

            year_month = f"{year}-{month}"

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if fsn_operate_obj:
                pass
            else:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id

    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine, self).create(vals)

        res.set_fsn_operate_id()

        return res



class WarehouseFinishedProductStock(models.Model):
    _inherit = "warehouse_finished_product_stock"

    fsn_operate_id = fields.Many2one("fsn_operate", string="FSN运营")

    def set_fsn_operate_id(self):
        for record in self:
            year = record.date.year
            month = '%02d' % record.date.month

            year_month = f"{year}-{month}"

            fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
            if not fsn_operate_obj:
                fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})

            record.fsn_operate_id = fsn_operate_obj.id

    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine, self).create(vals)

        res.set_fsn_operate_id()

        return res




# 销售
class SaleOrder(models.Model):
    _inherit = "sale.order"


    fsn_operate_id = fields.Many2one("fsn_operate", string="运营", compute="set_fsn_operate_id", store=True)
    @api.depends("fsn_delivery_date")
    def set_fsn_operate_id(self):
        for record in self:
            if record.fsn_delivery_date:
                year = record.fsn_delivery_date.year
                month = '%02d' % record.fsn_delivery_date.month
                year_month = f"{year}-{month}"

                if record.fsn_operate_id:
                    temp_fsn_operate_obj = record.fsn_operate_id
                else:
                    temp_fsn_operate_obj = False

                fsn_operate_obj = record.fsn_operate_id.sudo().search([("month", "=", year_month)])
                if not fsn_operate_obj:
                    fsn_operate_obj = fsn_operate_obj.sudo().create({"month": year_month})
                
                record.fsn_operate_id = fsn_operate_obj.id
                if temp_fsn_operate_obj:
                    temp_fsn_operate_obj.sudo().set_sale_order_value()
            else:
                record.fsn_operate_id = False

    @api.model
    def create(self, vals):

        res = super(SaleOrder, self).create(vals)

        res.set_fsn_operate_id()

        return res


class FsnOperate(models.Model):
    _name = 'fsn_operate'
    _description = 'fsn_运营'
    _rec_name = 'month'


    month = fields.Char(string="月份", required=True)
    year = fields.Char(string="年", compute="set_year", store=True)
    @api.depends("month")
    def set_year(self):
        for record in self:
            if "-" in record.month:
                record.year, _ = record.month.split("-")

    sale_order_ids = fields.One2many("sale.order", "fsn_operate_id", string="销售订单")
    sale_order_value = fields.Float(string="销售额", compute="set_sale_order_value", store=True)
    @api.depends("sale_order_ids", "sale_order_ids.amount_total")
    def set_sale_order_value(self):
        for record in self:
            record.sale_order_value = sum(record.sale_order_ids.mapped("amount_total"))

    order_number_ids = fields.One2many("sale_pro.sale_pro", "fsn_operate_id", string="生产订单")
    order_number_value = fields.Float(string="订单", compute="set_order_number_value", store=True)
    factory_order_number_value = fields.Float(string="工厂", compute="set_order_number_value", store=True)
    send_out_order_number_value = fields.Float(string="外发", compute="set_order_number_value", store=True)
    # 设置订单总价格
    @api.depends('order_number_ids', 'order_number_ids.order_price', 'order_number_ids.sum_voucher_count', 'order_number_ids.processing_type')
    def set_order_number_value(self):

        for record in self:

            temp_value = 0
            temp_factory_order_number_value = 0
            temp_send_out_order_number_value = 0

            for i in record.order_number_ids:
                if i.sale_pro_line_ids:
                    temp_value += (i.sum_voucher_count * float(i.order_price))
                else:
                    temp_value += i.total_price

                if i.processing_type:
                    if i.processing_type == "外发":
                        temp_send_out_order_number_value += (i.sum_voucher_count * float(i.order_price))
                    elif i.processing_type == "工厂":
                        temp_factory_order_number_value += (i.sum_voucher_count * float(i.order_price))


            record.order_number_value = temp_value
            record.factory_order_number_value = temp_factory_order_number_value
            record.send_out_order_number_value = temp_send_out_order_number_value

    
    cutting_bed_ids = fields.One2many("cutting_bed", "fsn_operate_id", string="裁床产值")
    cutting_bed = fields.Float(string="裁床", compute="set_cutting_bed", store=True)
    @api.depends('cutting_bed_ids', 'cutting_bed_ids.pro_value')
    def set_cutting_bed(self):
        for record in self:
            record.cutting_bed = sum(record.cutting_bed_ids.mapped("pro_value"))

    pro_pro_ids = fields.One2many("pro.pro", "fsn_operate_id", string="组产值")
    workshop = fields.Float(string="车间", compute="set_workshop", store=True)
    @api.depends('pro_pro_ids', 'pro_pro_ids.pro_value')
    def set_workshop(self):
        for record in self:
            record.workshop = sum(record.pro_pro_ids.mapped("pro_value"))
    

    shop_sales_value = fields.Float(string="车间销售产值")

    @staticmethod
    def set_begin_and_end(today):

        year, month = today.year, today.month

        this_month_start = datetime.date(year, month, 1)
        this_month_end = datetime.date(year, month, calendar.monthrange(year, month)[1])

        return this_month_start, this_month_end

    def set_shop_sales_value(self, today):
        ''' 设置车间销售产值'''

        this_month_start, this_month_end = self.set_begin_and_end(today)
        
        if "suspension_system_summary" in self.env:
            
            suspension_system_summary_objs_list = self.env['suspension_system_summary'].sudo().read_group(
                domain=[("dDate", ">=", this_month_start), ("dDate", "<=", this_month_end), ('group.group','!=', '后整')],
                fields=['total_quantity', 'style_number'],
                groupby="style_number"
            )

            temp_total_quantity = 0

            for i in suspension_system_summary_objs_list:

                if i['style_number']:

                    ib_detail_obj = self.env['ib.detail'].sudo().browse(i['style_number'][0])

                    sale_order_line_objs = self.env['sale.order.line'].sudo().search([("product_id.name", "=", ib_detail_obj.style_number_base_id.name)])
                    

                    temp_total_quantity += (i['total_quantity'] * min(sale_order_line_objs.mapped("price_unit"), default=0))

            year, month, _ = str(today).split("-")

            fsn_operate_obj = self.env['fsn_operate'].sudo().search([("month", "=", f"{year}-{month}")])
            fsn_operate_obj.shop_sales_value = temp_total_quantity


    outgoing_output_ids = fields.One2many("outgoing_output", "fsn_operate_id", string="外发产值")
    outbound = fields.Float(string="外发", compute="set_outbound", store=True)
    @api.depends('outgoing_output_ids', 'outgoing_output_ids.pro_value')
    def set_outbound(self):
        for record in self:
            record.outbound = sum(record.outgoing_output_ids.mapped("pro_value"))

    send_out_sales_value = fields.Float(string="外发销售产值")

    def set_send_out_sales_value(self, today):
        ''' 设置外发销售产值'''
        year, month, _ = str(today).split("-")

        fsn_operate_obj = self.env['fsn_operate'].sudo().search([("month", "=", f"{year}-{month}")])

        temp_total_quantity = 0

        for i in fsn_operate_obj.outgoing_output_ids:

            sale_order_line_objs = self.env['sale.order.line'].sudo().search([("product_id.name", "=", i.style_number.style_number_base_id.name)])

            temp_total_quantity += (i.number * min(sale_order_line_objs.mapped("price_unit"), default=0))

        fsn_operate_obj.send_out_sales_value = temp_total_quantity


    posterior_passage_output_value_ids = fields.One2many("posterior_passage_output_value", "fsn_operate_id", string="后道产值")
    posterior_passage = fields.Float(string="后道", compute="set_posterior_passage", store=True)
    @api.depends('posterior_passage_output_value_ids', 'posterior_passage_output_value_ids.pro_value')
    def set_posterior_passage(self):
        for record in self:
            record.posterior_passage = sum(record.posterior_passage_output_value_ids.mapped("pro_value"))


    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "fsn_operate_id", string="出入库明细")
    enter_warehouse = fields.Float(string="仓库(入库)", compute="set_warehouse_info", store=True)
    out_of_warehouse = fields.Float(string="仓库(出仓)", compute="set_warehouse_info", store=True)
    customer_out = fields.Float(string="客户出库", compute="set_warehouse_info", store=True)
    customer_enter = fields.Float(string="客户入库", compute="set_warehouse_info", store=True)
    actual_delivery = fields.Float(string="实际出库产值", compute="set_warehouse_info", store=True)
    # 设置订单总价格
    @api.depends('finished_product_ware_line_ids',
    'finished_product_ware_line_ids.order_number',
    'finished_product_ware_line_ids.order_number.order_price',
    'finished_product_ware_line_ids.style_number',
    'finished_product_ware_line_ids.type')
    def set_warehouse_info(self):
        for record in self:

            tem_enter_warehouse = 0
            tem_out_of_warehouse = 0
            tem_customer_enter = 0
            tem_customer_out = 0


            for finished_product_ware_line_obj in record.finished_product_ware_line_ids:

                if finished_product_ware_line_obj.state == "确认":

                    order_price = float(finished_product_ware_line_obj.order_number.order_price)

                    if finished_product_ware_line_obj.type == "入库":
                        tem_enter_warehouse += (finished_product_ware_line_obj.number * order_price)

                        if finished_product_ware_line_obj.source_destination.type == "外部":
                            tem_customer_enter += (finished_product_ware_line_obj.number * order_price)

                    elif finished_product_ware_line_obj.type == "出库":
                        tem_out_of_warehouse += (finished_product_ware_line_obj.number * order_price)

                        if finished_product_ware_line_obj.source_destination.type == "外部":
                            tem_customer_out += (finished_product_ware_line_obj.number * order_price)
                    

            record.enter_warehouse = tem_enter_warehouse
            record.out_of_warehouse = tem_out_of_warehouse
            record.customer_enter = tem_customer_enter
            record.customer_out = tem_customer_out
            record.actual_delivery = record.customer_out - record.customer_enter






    warehouse_finished_product_stock_ids = fields.One2many("warehouse_finished_product_stock", "fsn_operate_id", string="存量产值")
    stock_output_value = fields.Float(string="存量产值", compute="set_stock_output_value", store=True)
    @api.depends("warehouse_finished_product_stock_ids", "warehouse_finished_product_stock_ids.change_stock_production_value")
    def set_stock_output_value(self):
        for record in self:
            record.stock_output_value = sum(record.warehouse_finished_product_stock_ids.mapped("change_stock_production_value"))












    


                
            


    cashmere_filling_room = fields.Float(string="充绒房")


    @api.constrains('date')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([('date', '=', self.date)])
        if len(demo) > 1:
            raise ValidationError(f"已经存在日期为：{self.date}的记录了！")








