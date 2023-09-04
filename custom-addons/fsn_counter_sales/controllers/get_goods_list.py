from odoo import http
import json

class GetGoodsList(http.Controller):
    # 获取商品列表
    @http.route('/fsn_counter_sales/get_goods_list/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def get_goods_list(self, **kw):
        res = http.request.jsonrequest

        order_id = res.get("order_id", None)    # 订单编号

        counter_sales_order_obj = http.request.env["counter_sales_order"].sudo().search([("order_number", "=", order_id)])

        goods_list = []

        for goods_line_obj in counter_sales_order_obj.counter_sales_order_line_ids:

            base_url = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = f"{base_url}/get_imgae?model=goods_info&id={goods_line_obj.good_id.id}&field=sample_image"

            subscript_list = [i for i,d in enumerate(goods_list) if "goodsNumber" in d and d["goodsNumber"]==goods_line_obj.product_barcode]
            if subscript_list:
                if goods_line_obj.state == "正常":

                    goods_list[subscript_list[0]]["num"] = goods_list[subscript_list[0]]["num"] + goods_line_obj.number
                else:
                    goods_list[subscript_list[0]]["num"] = goods_list[subscript_list[0]]["num"] -  goods_line_obj.number
            else:

                goods_list.append({
                    "id": goods_line_obj.id,
                    "goodsNumber": goods_line_obj.product_barcode,
                    "goodsName": goods_line_obj.good_id.name,
                    "goodsImage": url,
                    "goodsPrice": goods_line_obj.unit_price,
                    "num": goods_line_obj.number if goods_line_obj.state == "正常" else -goods_line_obj.number,
                    "state": "正常",
                })
        
        def is_odd(obj):

            if obj["num"] == 0:
                pass
            else:
                return obj
        goods_list = list(filter(is_odd, goods_list))

        if goods_list:
            return json.dumps({'status': "1", 'messages': "成功", 'data': goods_list})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': []})