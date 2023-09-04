from odoo import models, fields, api

import calendar, datetime

import itertools

class FinishedInventory(models.Model):
    """ 继承库存"""
    _inherit = 'finished_inventory'


class WarehouseFinishedProductStock(models.Model):
    _name = 'warehouse_finished_product_stock'
    _description = '仓库成品存量统计'
    _rec_name = 'date'
    _order = "date desc"


    belong_to_month = fields.Char(string="月份")
    date = fields.Date(string='日期')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号')
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ], string="加工类型", related="order_number.processing_type", store=True)
    style_number = fields.Many2one('ib.detail', string='款号')
    size = fields.Many2one("fsn_size", string="尺码")

    before_inventory_number = fields.Integer(string="之前库存")
    change_inventory_number = fields.Integer(string="库存变化")
    intraday_inventory_number = fields.Integer(string="当天库存数量", compute="set_intraday_inventory_number", store=True)
    @api.depends("before_inventory_number", "change_inventory_number")
    def set_intraday_inventory_number(self):
        for record in self:
            record.intraday_inventory_number = record.before_inventory_number + record.change_inventory_number

    before_customer_enter_number = fields.Integer(string="之前客户入库数")
    change_customer_enter_number = fields.Integer(string="客户入库数变化")
    intraday_customer_enter_number = fields.Integer(string="当天客户入库数", compute="set_intraday_customer_enter_number", store=True)
    @api.depends("before_customer_enter_number", "change_customer_enter_number")
    def set_intraday_customer_enter_number(self):
        for record in self:
            record.intraday_customer_enter_number = record.before_customer_enter_number + record.change_customer_enter_number

    before_customer_out_number = fields.Integer(string="之前客户出库数")
    change_customer_out_number = fields.Integer(string="客户出库数变化")
    intraday_customer_out_number = fields.Integer(string="当天客户出库数", compute="set_intraday_customer_out_number", store=True)
    @api.depends("before_customer_out_number", "change_customer_out_number")
    def set_intraday_customer_out_number(self):
        for record in self:
            record.intraday_customer_out_number = record.before_customer_out_number + record.change_customer_out_number

    before_stock = fields.Integer(string="之前存量", compute="set_before_stock", store=True)
    @api.depends("before_inventory_number", "before_customer_enter_number", "before_customer_out_number")
    def set_before_stock(self):
        for record in self:
            record.before_stock = record.before_customer_out_number - record.before_customer_enter_number + record.before_inventory_number
    
    intraday_stock = fields.Integer(string="当天存量", compute="set_intraday_stock", store=True)
    @api.depends("intraday_inventory_number", "intraday_customer_enter_number", "intraday_customer_out_number")
    def set_intraday_stock(self):
        for record in self:
            record.intraday_stock = record.intraday_customer_out_number - record.intraday_customer_enter_number + record.intraday_inventory_number

    change_stock = fields.Integer(string="存量变化", compute="set_change_stock", store=True)
    @api.depends("intraday_stock", "before_stock")
    def set_change_stock(self):
        for record in self:
            record.change_stock = record.intraday_stock - record.before_stock

    change_stock_production_value = fields.Float(string="存量变化产值", compute="set_change_stock_production_value", store=True)
    @api.depends("change_stock", "order_number", "order_number.order_price")
    def set_change_stock_production_value(self):
        for record in self:
            record.change_stock_production_value = record.change_stock * float(record.order_number.order_price)



    # 获取指定日期月的全部天数
    def get_all_dates(self, date):

        num_days = calendar.monthrange(date.year, date.month)[1]
        days = [datetime.date(date.year, date.month, day) for day in range(1, num_days+1)]

        return days


    def getbefore_stock_date(self, day, order_number, style_number, size):

        finished_product_ware_line_objs = self.env['finished_product_ware_line'].sudo().search([
            ("date", "<", day),
            ("order_number", "=", order_number),
            ("style_number", "=", style_number),
            ("size", "=", size),
            ("state", "=", "确认")
        ])

        before_dict = {"put_number": [], "out_number": [], "customer_enter": [], "customer_out": []}

        for finished_product_ware_line_obj in finished_product_ware_line_objs:

            if finished_product_ware_line_obj.type == "入库":

                before_dict['put_number'].append(finished_product_ware_line_obj.number)

                if finished_product_ware_line_obj.finished_product_ware_id.customer_id.type == "外部":

                    before_dict['customer_enter'].append(finished_product_ware_line_obj.number)

            if finished_product_ware_line_obj.type == "出库":

                before_dict['out_number'].append(finished_product_ware_line_obj.number)

                if finished_product_ware_line_obj.finished_product_ware_id.customer_id.type == "外部":

                    before_dict['customer_out'].append(finished_product_ware_line_obj.number)

        return before_dict


    def get_that_very_day_stock_date(self, day, order_number, style_number, size):

        that_very_day_objs = self.env['finished_product_ware_line'].sudo().search([
            ("date", "=", day),
            ("order_number", "=", order_number),
            ("style_number", "=", style_number),
            ("size", "=", size),
            ("state", "=", "确认")
        ])

        change_dict = {"put_number": [], "out_number": [], "customer_enter": [], "customer_out": []}

        for that_very_day_obj in that_very_day_objs:

            if that_very_day_obj.type == "入库":

                change_dict['put_number'].append(that_very_day_obj.number)

                if that_very_day_obj.finished_product_ware_id.customer_id.type == "外部":

                    change_dict['customer_enter'].append(that_very_day_obj.number)

            if that_very_day_obj.type == "出库":

                change_dict['out_number'].append(that_very_day_obj.number)

                if that_very_day_obj.finished_product_ware_id.customer_id.type == "外部":

                    change_dict['customer_out'].append(that_very_day_obj.number)
        
        return change_dict


    def manual_day_stock_generation(self, day):

        finished_product_ware_line_list = self.env['finished_product_ware_line'].sudo().search_read(
            [("date", "=", day)],
            fields=["id", "order_number", "style_number", "size"])

        finished_product_ware_line_list.sort(key=lambda x: (x["order_number"][0], x["style_number"][0], x["size"][0]), reverse=False)

        for (order_number, style_number, size), _ in itertools.groupby(finished_product_ware_line_list, key=lambda x:(x["order_number"][0], x["style_number"][0], x["size"][0])):

            before_dict = self.getbefore_stock_date(day, order_number, style_number, size)

            change_dict = self.get_that_very_day_stock_date(day, order_number, style_number, size)

            self.env['warehouse_finished_product_stock'].create({
                "date": day,
                "order_number": order_number,
                "style_number": style_number,
                "size": size,

                "before_inventory_number": sum(before_dict['put_number']) - sum(before_dict['out_number']),
                "change_inventory_number": sum(change_dict['put_number']) - sum(change_dict['out_number']),

                "before_customer_enter_number": sum(before_dict['customer_enter']),
                "change_customer_enter_number": sum(change_dict['customer_enter']),

                "before_customer_out_number": sum(before_dict['customer_out']),
                "change_customer_out_number": sum(change_dict['customer_out']),
            })


    def manual_stock_generation(self, today):

        if today.day == 1:
            date = today - datetime.timedelta(days=1)

            days = self.get_all_dates(date)

            for day in days:

                self.manual_day_stock_generation(day)



