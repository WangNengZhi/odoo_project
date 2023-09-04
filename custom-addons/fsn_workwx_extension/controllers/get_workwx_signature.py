from odoo import http
import json
import time
import hashlib

from utils import weixin_utils, weixin_approval_utils


class GetWorkwxSignature(http.Controller):


    @http.route('/workwx_api/v1/get_workwx_signature/', methods=['POST', 'GET'], type='http', auth='public')
    def get_workwx_signature(self, **kw):
        ''' 企业微信agentConfig'''

        jsapi_ticket = weixin_approval_utils.get_jsapi_ticket()
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