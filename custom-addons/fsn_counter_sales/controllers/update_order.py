from odoo import http
import json


class UpdateOrder(http.Controller):
    # 更新商品列表
    @http.route('/fsn_counter_sales/update_order/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def update_order(self, **kw):
        res = http.request.jsonrequest

        order_id = res.get("order_id", None)    # 订单编号
        goodsList = res.get("goodsList", None)    # 商品列表

        counter_sales_order_obj = http.request.env["counter_sales_order"].sudo().search([("order_number", "=", order_id)])
        try:
            for good_record in goodsList:
                if good_record.get("id"):
                    pass

                else:
                    goods_info = http.request.env["goods_info"].sudo().search([("product_barcode", "=", good_record.get("goodsNumber").strip())])

                    counter_sales_order_obj.counter_sales_order_line_ids.sudo().create({
                        "counter_sales_order_id": counter_sales_order_obj.id,
                        "good_id": goods_info.id,
                        "number": good_record.get("num"),
                        "unit_price": good_record.get("goodsPrice"),
                        "state": good_record.get("state") if good_record.get("state") == "退货" else "正常",
                        "order_line_id": good_record.get("order_line_id") if good_record.get("order_line_id") else False,
                    })

        except Exception as e:
            return json.dumps({'status': "0", 'messages': "失败"})
        else:

            return json.dumps({'status': "1", 'messages': "成功"})

