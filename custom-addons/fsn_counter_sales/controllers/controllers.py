# -*- coding: utf-8 -*-
from cmath import log
from odoo import http, fields
import json


class FsnCounterSales(http.Controller):
    # 添加商品
    @http.route('/fsn_counter_sales/add_goods/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def add_goods(self, **kw):

        res = http.request.jsonrequest

        list_goods = res.get("list_goods", None)    # 商品列表
        user = res.get("user", None)    # 工号
        # order_number = res.get("order_number", None)    # 订单编号

        customer_name = res.get("customer_name", None)    # 订单编号
        customer_phone = res.get("customer_phone", None)    # 订单编号
        customer_address = res.get("customer_address", None)    # 订单编号


        hr_employee_obj = http.request.env["hr.employee"].sudo().search([("barcode", "=", user)])

        # counter_sales_order_obj = http.request.env["counter_sales_order"].sudo().search([("order_number", "=", order_number)])
        counter_sales_order_obj = http.request.env["counter_sales_order"].sudo().create({
            "date": fields.Date.today(),
            "salesman": hr_employee_obj.id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_address": customer_address,
        })

        lines = []

        for good_obj in list_goods:

            goods_info = http.request.env["goods_info"].sudo().search([("product_barcode", "=", good_obj.get("id").strip())])
            if goods_info:

                line = {
                    "good_id": goods_info.id,     # 产品编码
                    "number": good_obj.get("num"),  # 数量
                    "unit_price": good_obj.get("dprice")   # 单价
                }
                lines.append((0, 0, line))
                

        counter_sales_order_obj.counter_sales_order_line_ids = lines




        if True:

            return json.dumps({'status': "1", 'messages': "成功", 'data': "666"})

        # else:
        #     return json.dumps({'status': "0", 'messages': "失败", 'data': []})


    # 获取商品信息
    @http.route('/fsn_counter_sales/get_good_messages/', auth='public', type='http', methods=['GET'])
    def get_good_messages(self, *args, **kwargs):

        product_barcode = kwargs.get("product_barcode").strip()     # 产品编码

        goods_info = http.request.env["goods_info"].sudo().search([("product_barcode", "=", product_barcode)])

        # http://192.168.75.129:8069/web/image?model=goods_info&id=185&field=sample_image&unique=20220605092504
        base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f"{base_url}/get_imgae?model=goods_info&id={goods_info.id}&field=sample_image"

        # if goods_info and goods_info.is_active:
        if goods_info:
            return json.dumps({'status': "1", 'messages': "成功", 'data': {"name": goods_info.name, "unit_price": goods_info.unit_price, "url": url}})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': {}})


    # 通过款号和尺码获取商品条码数据
    @http.route('/fsn_counter_sales/get_goods_barcode/', auth='public', type='http', methods=['GET'])
    def get_goods_barcode(self, *args, **kwargs):

        style_number = kwargs.get("style_number").strip()     # 款式编号
        size = kwargs.get("size").strip()     # 尺码

        ib_detail_obj = http.request.env["ib.detail"].sudo().search([("style_number", "=", style_number)])
        fsn_size_obj = http.request.env["fsn_size"].sudo().search([("name", "=", size)])

        if ib_detail_obj and fsn_size_obj:

            goods_info = http.request.env["goods_info"].sudo().search([
                ("style_number", "=", ib_detail_obj.id),
                ("size", "=", fsn_size_obj.id),
            ])

            if goods_info:
                return json.dumps({'status': "1", 'messages': "成功", 'result': goods_info.product_barcode})
            
            else:
                return json.dumps({'status': "0", 'messages': "失败", 'result': {}})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'result': {}})



