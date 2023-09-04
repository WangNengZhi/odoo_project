from odoo import models, fields, api

import requests
import time

import urllib.parse

import hashlib
import hmac
import base64


class JdySetting(models.Model):
    _name = 'jdy_setting'
    _description = '精斗云API配置'
    _rec_name = 'key'

    key = fields.Char(string="键")
    value = fields.Char(string="值")




    def get_app_signature(self, data, secret):
        ''' 获取app_signature'''

        signature_hex = hmac.new(key=secret.encode('utf-8'),
                                msg=data.encode('utf-8'),
                                digestmod=hashlib.sha256).hexdigest()
        signature_hex_base64 = base64.b64encode(signature_hex.encode('utf-8'))
        signature_result = signature_hex_base64.decode('utf-8')
        return signature_result



    def get_x_api_signature(self, request_mode, path_url, timestamp, nonce, client_secret, kw):
        ''' 生成X-Api-Signature'''

        # request_mode = 'GET'
        path_url = urllib.parse.quote(path_url, safe="")

        params_list = []
        for key, value in kw.items():

            value = urllib.parse.quote(value, safe="")
            value = urllib.parse.quote(value, safe="")

            params_list.append(f'{key}={value}')
        
        params = "&".join(params_list)


        nonce = f'x-api-nonce:{nonce}'
        timestamp = f'x-api-timestamp:{timestamp}'


        x_api_signature = f'{request_mode}\n{path_url}\n{params}\n{nonce}\n{timestamp}\n'

        signature_hex = hmac.new(key=client_secret.encode('utf-8'),
                                msg=x_api_signature.encode('utf-8'),
                                digestmod=hashlib.sha256).hexdigest()

        signature_hex_base64 = base64.b64encode(signature_hex.encode('utf-8'))
        signature_result = signature_hex_base64.decode('utf-8')

        return signature_result

    

    def get_x_gw_router_addr(self, app_key, app_signature, client_secret, client_id, outerInstanceId):
        ''' 主动获取授权信息'''

        path_url = '/jdyconnector/app_management/push_app_authorize'
        base_url = 'https://api.kingdee.com'
        url = base_url + path_url
        timestamp = str(int(time.time() * 1000.0))
        nonce = '666'

        x_api_signature = self.get_x_api_signature('POST', path_url, timestamp, nonce, client_secret, {'outerInstanceId': outerInstanceId})

        headers = {
            'content-type': 'application/json',
            'X-Api-ClientID': client_id,
            'X-Api-Auth-Version': '2.0',
            'x-api-timestamp': timestamp,
            'X-Api-SignHeaders': 'X-Api-TimeStamp,X-Api-Nonce',
            'x-api-nonce': nonce,
            'X-Api-Signature': x_api_signature
        }

        querystring = {
            'outerInstanceId': outerInstanceId,
        }

        response = requests.request("POST", url, headers=headers, params=querystring)
        response = response.json()
        
        return response
    

    def get_access_token(self, app_key, app_signature, client_secret, client_id):
        ''' 获取金蝶精斗云 云会计 token'''

        path_url = '/jdyconnector/app_management/kingdee_auth_token'
        base_url = 'https://api.kingdee.com'
        get_token_url = base_url + path_url
        timestamp = str(int(time.time() * 1000.0))
        nonce = '666'

        x_api_signature = self.get_x_api_signature('GET', path_url, timestamp, nonce, client_secret, {'app_key': app_key, 'app_signature': app_signature})

        headers = {
            'content-type': 'application/json',
            'X-Api-ClientID': client_id,
            'X-Api-Auth-Version': '2.0',
            'x-api-timestamp': timestamp,
            'X-Api-SignHeaders': 'X-Api-TimeStamp,X-Api-Nonce',
            'x-api-nonce': nonce,
            'X-Api-Signature': x_api_signature
        }

        querystring = {
            'app_key': app_key,
            'app_signature': app_signature,
        }

        
        response = requests.request("GET", get_token_url, headers=headers, params=querystring)
        response = response.json()
        

        return response



    def update_jdy_app_secret(self):
        ''' 更新app_secret app_secret需要每天重新获取'''

        app_key = self.env.ref('fsn_accountant.jdy_setting_app_key').value
        app_secret = self.env.ref('fsn_accountant.jdy_setting_app_secret').value
        client_id = self.env.ref('fsn_accountant.jdy_setting_client_id').value
        client_secret = self.env.ref('fsn_accountant.jdy_setting_client_secret').value
        outer_instance_id = self.env.ref('fsn_accountant.jdy_setting_outer_instance_id').value

        app_signature = self.get_app_signature(app_key, app_secret)

        x_gw_router_addr = self.get_x_gw_router_addr(app_key, app_signature, client_secret, client_id, outer_instance_id)

        assert x_gw_router_addr['code'] == 200

        appSecret = x_gw_router_addr['data'][0]['appSecret']
        self.env.ref('fsn_accountant.jdy_setting_app_secret').value = x_gw_router_addr['data'][0]['appSecret']


