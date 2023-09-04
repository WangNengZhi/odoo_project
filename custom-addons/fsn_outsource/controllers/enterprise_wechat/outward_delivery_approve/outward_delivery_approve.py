from odoo import http
import json
import requests
import time
import hashlib

from utils import weixin_utils



class OutwardDeliveryApprove(http.Controller):

    @staticmethod
    def get_jsapi_ticket(ACCESS_TOKEN):
        """
        通过access_token获取到应用jsapi_ticket
        jsapi_ticket是H5应用调用企业微信JS接口的临时票据
        分为企业 jsapi_ticket和 应用jsapi_ket
        详情 https://developer.work.weixin.qq.com/document/path/90506
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/ticket/get?access_token={}&type=agent_config'.format(ACCESS_TOKEN)
        resp = requests.get(url).json()
        if resp['errmsg'] == 'ok':
            return resp['ticket']
        else:
            print('请求错误', resp['errmsg'])
            return ''
    

    @http.route('/get_workwx_signature/', methods=['POST', 'GET'], type='http', auth='public')
    def get_workwx_signature(self, **kw):
        ''' 企业微信agentConfig'''

        access_token = weixin_utils.get_access_token(weixin_utils._CORPSECRET)
        
        jsapi_ticket = self.get_jsapi_ticket(access_token)
        noncestr = "wdc"
        timestamp = int(time.time())
        url = kw.get('url')


        str1 = "jsapi_ticket={}&noncestr={}&timestamp={}&url={}".format(
            jsapi_ticket, noncestr, timestamp, url
        )
        sha_str = hashlib.sha1(str1.encode('utf-8')).hexdigest()
        
        jm_data = {
            'sha_str': sha_str, 
            'timestamp': timestamp,
            'jsapi_ticket': jsapi_ticket,
            'noncestr': noncestr,
            'url': url,
            'corpid': weixin_utils._CORPID,
            'agentid': weixin_utils._AGENTID,
        }

        return json.dumps(jm_data)


    @http.route('/fsn_size_select/', methods=['POST', 'GET'], type='http', auth='public')
    def fsn_size_select(self, **kw):
        ''' 企业微信：获取尺码尺码'''

        fsn_size_objs = http.request.env["fsn_size"].sudo().search([])

        datas = {
            "key": kw.get("key"),
            "fsn_size_list": fsn_size_objs.mapped("name"),
        }

        return http.request.render("fsn_outsource.fsn_outsource_size_select", {"datas": datas})



    @http.route('/fsn_workwx_outsource_order_select/', methods=['POST', 'GET'], type='http', auth='public')
    def fsn_workwx_outsource_order_select(self, **kw):
        ''' 企业微信：外发订单'''

        outsource_order_objs = http.request.env["outsource_order"].sudo().search([("outsource_plant_id", "!=", False)])

        datas = {
            "key": kw.get("key"),
            "outsource_order_list": [{"id": i.id, "outsource_order_title": f"{i.order_id.order_number}({i.outsource_plant_id.name})"}for i in outsource_order_objs],
        }

        return http.request.render("fsn_outsource.fsn_outsource_fsn_workwx_order_number_select", {"datas": datas})



    @http.route('/fsn_workwx_outsource_order_line_select/', methods=['POST', 'GET'], type='http', auth='public')
    def fsn_workwx_outsource_order_line_select(self, **kw):
        ''' 企业微信：外发订单明细'''

        ib_detail_objs = http.request.env['ib.detail'].sudo().search([])

        datas = {
            "key": kw.get("key"),
            "ib_detail_list": [{"id": i.id, "ib_detail_title": f"{i.style_number}"} for i in ib_detail_objs],
        }

        return http.request.render("fsn_outsource.fsn_outsource_fsn_workwx_outsource_order_line_select", {"datas": datas})




