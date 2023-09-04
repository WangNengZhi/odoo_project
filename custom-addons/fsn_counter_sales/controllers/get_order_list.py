# -*- coding: utf-8 -*-
from odoo import http
import json



class GetOrderList(http.Controller):
    # 获取订单列表
    @http.route('/fsn_counter_sales/get_order_list/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def get_order_list(self, **kw):
        res = http.request.jsonrequest

        order_date = res.get("date", None)    # 日期或电话
        search_type = res.get("search_type", None)      # 搜索类型


        if search_type == "电话":
            counter_sales_order_objs = http.request.env["counter_sales_order"].sudo().search([("customer_phone", "=", order_date)])
        else:
            counter_sales_order_objs = http.request.env["counter_sales_order"].sudo().search([("date", "=", order_date)])

        order_list = []

        for counter_sales_order_obj in counter_sales_order_objs:

            line_list = []
            for line_obj in counter_sales_order_obj.counter_sales_order_line_ids:

                base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = f"{base_url}/get_imgae?model=goods_info&id={line_obj.good_id.id}&field=sample_image"

                subscript_list = [i for i,d in enumerate(line_list) if "goodsNumber" in d and d["goodsNumber"]==line_obj.product_barcode]
                if subscript_list:

                    if line_obj.state == "正常":

                        line_list[subscript_list[0]]["num"] = line_list[subscript_list[0]]["num"] + line_obj.number
                    else:
                        line_list[subscript_list[0]]["num"] = line_list[subscript_list[0]]["num"] -  line_obj.number
                else:

                    line_list.append({
                        "id": line_obj.id,
                        "goodsImage": url,
                        "goodsNumber": line_obj.product_barcode,
                        "goodsName": line_obj.good_id.name,
                        "goodsPrice": line_obj.unit_price,
                        "num": line_obj.number if line_obj.state == "正常" else -line_obj.number,
                    })

            def is_odd(obj):
                return obj["num"] != 0
            line_list = list(filter(is_odd, line_list))
            
            order_list.append({
                "orderId": counter_sales_order_obj.order_number,
                "type": counter_sales_order_obj.state,
                "total": counter_sales_order_obj.order_amount,
                "orderLists": line_list
            })
            

        if order_list:

            return json.dumps({'status': "1", 'messages': "成功", 'data': order_list})

        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': []})



