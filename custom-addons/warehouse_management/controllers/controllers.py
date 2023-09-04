# -*- coding: utf-8 -*-
from datetime import date
from odoo import http
import json


class WarehouseManagement(http.Controller):


    # 获取商品信息
    @http.route('/warehouse_management/get_bar_code_messages/', auth='public', type='http', methods=['GET'])
    def get_bar_code_messages(self, *args, **kwargs):

        product_barcode = kwargs.get("product_barcode").strip()     # 产品编码

        goods_info = http.request.env["sale_pro_bar_code"].sudo().search([("barcode_data", "=", product_barcode)])

        goods_list = []
        for good in goods_info:
            goods_list.append({"order_name": good.sale_pro_id.order_number, "order_number": good.sale_pro_id.id, "style_number": good.style_number.id})

        if goods_info:
            return json.dumps({'status': "1", 'messages': "成功", 'data': goods_list})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': []})


    # 创建仓库记录
    @http.route('/warehouse_management/create_warehouse_record/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def create_warehouse_record(self, **kw):

        res = http.request.jsonrequest

        date = res.get("date", None)    # 日期时间
        operate_type = res.get("type", None)    # 类型（出库或者入库）
        receipt_number = res.get("receipt_number", None)    # 单据编号
        remark = res.get("remark", None)    # 备注
        inbound_sender = res.get("inbound_sender", None)    # 入库送件人
        inbound_recipient = res.get("inbound_recipient", None)    # 入库收件人
        outgoer = res.get("outgoer", None)    # 类型（出库或者入库）
        receiving_customers = res.get("receiving_customers", None)    # 类型（出库或者入库）
        warehouse_management_order_number = res.get("order_number", None)    # 订单号
        items = res.get("items", None)  # 物品信息





        # if warehouse_management_obj:
        #     return json.dumps({'status': "1", 'messages': "成功", 'data': {}})
        # else:
        #     return json.dumps({'status': "0", 'messages': "失败", 'data': {}})
