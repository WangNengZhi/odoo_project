# -*- coding: utf-8 -*-
from odoo import http
import json


class CancelOrder(http.Controller):
    # 取消订单
    @http.route('/fsn_counter_sales/cancel_order/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def cancel_order(self, **kw):

        res = http.request.jsonrequest
        order_id = res.get("order_id", None)    # 订单编号

        counter_sales_order_obj = http.request.env["counter_sales_order"].sudo().search([("order_number", "=", order_id)])
        is_success = counter_sales_order_obj.sudo().write({
            "state": "已取消"
        })

        if is_success:

            return json.dumps({'status': "1", 'messages': "成功", 'data': []})

        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': []})