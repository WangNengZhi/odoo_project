from odoo import models, fields, api
import requests

import datetime

class FsnAccountingDetail(models.Model):
    _name = 'fsn_accounting_detail'
    _description = 'FSN会计明细'
    # _rec_name = 'jdy_subject_id'

    type = fields.Selection([('1001', '库存现金'), ('1002', '银行存款'), ('1012', '其他货币资金'), ('5001', '开票明细')], string="类别")
    jdy_subject_id = fields.Many2one("jdy_subject", string="所属科目")
    creditFor = fields.Float(string="原币贷方发生")
    dcType = fields.Char(string="方向")
    balanceForOld = fields.Float(string="原币余额")
    yearPeriod = fields.Float(string="会计期间")
    remark = fields.Char(string="摘要")
    voucherNo = fields.Char(string="凭证字号")
    ymd = fields.Date(string="日期")
    balance = fields.Float(string="余额")
    balanceOld = fields.Float(string="历史余额")
    startYearPeriod = fields.Float(string="开始期间")
    periodfrom = fields.Float(string="起始日期")
    debit = fields.Float(string="借方")
    credit = fields.Float(string="贷方")
    debitFor = fields.Float(string="原币借方发生")
    dc = fields.Float(string="科目借贷方向")

    def get_jdy_subject_list(self, number):
        ''' 获取科目列表'''

        jdy_subject_obj = self.env['jdy_subject'].sudo().search([("number", "=", number)])

        child_jdy_subject = self.env['jdy_subject'].sudo().search([("parentId", "=", jdy_subject_obj.subject_id)])
        if child_jdy_subject:
            return child_jdy_subject
        return jdy_subject_obj
    


    @staticmethod
    def get_year_start_end(year):
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        return start_date, end_date


    
    def sync_accounting_detail(self, today):
        ''' 同步精斗云会计明细账-1002银行存款'''

        year, month, _ = str(today).split("-")
        toPeriod = year + month

        fromPeriod = year + "01"


        start_date, end_date = self.get_year_start_end(int(year))

        app_key = self.env.ref('fsn_accountant.jdy_setting_app_key').value
        app_secret = self.env.ref('fsn_accountant.jdy_setting_app_secret').value
        client_id = self.env.ref('fsn_accountant.jdy_setting_client_id').value
        client_secret = self.env.ref('fsn_accountant.jdy_setting_client_secret').value
        outer_instance_id = self.env.ref('fsn_accountant.jdy_setting_outer_instance_id').value

        url = 'https://api.kingdee.com/jdyaccouting/querydetail'

        app_signature = self.env['jdy_setting'].get_app_signature(app_key, app_secret)

        access_token = self.env['jdy_setting'].get_access_token(app_key, app_signature, client_secret, client_id)

        x_gw_router_addr = self.env['jdy_setting'].get_x_gw_router_addr(app_key, app_signature, client_secret, client_id, outer_instance_id)

        serviceId = x_gw_router_addr['data'][0]['serviceId']
        accountId = x_gw_router_addr['data'][0]['accountId']
        domain = x_gw_router_addr['data'][0]['domain']

        headers = {
            'content-type': 'application/json',
            'X-GW-Router-Addr': domain
        }

        querystring = {
            'access_token': access_token['data']['access_token'],
            'sId': serviceId,
            'dbId': accountId,
            'fromPeriod': fromPeriod,
            'toPeriod': toPeriod,
        }
        type_list = ["1001", "1002", "1012", "5001"]

        for type in type_list:

            jdy_subject_objs = self.get_jdy_subject_list(type)

            for jdy_subject_obj in jdy_subject_objs:

                self.env['fsn_accounting_detail'].sudo().search([("jdy_subject_id", "=", jdy_subject_obj.id), ("ymd", ">=", start_date), ("ymd", "<=", end_date)]).unlink()


                querystring['accountNum'] = jdy_subject_obj.number

                response = requests.request("GET", url=url, headers=headers, params=querystring)
                response = response.json()

                if "data" in response:
                    
                    for item in response['data']['items']:

                        if item.get('voucherNo'):
                                
                            self.env['fsn_accounting_detail'].sudo().create({
                                "type": type,
                                "jdy_subject_id": jdy_subject_obj.id,
                                "creditFor": item.get('creditFor'),
                                "dcType": item.get('dcType'),
                                "balanceForOld": item.get('balanceFor'),
                                "yearPeriod": item.get('yearPeriod'),
                                "remark": item.get('remark'),
                                "voucherNo": item.get('voucherNo'),
                                "ymd": item.get('ymd'),
                                "balance": item.get('balance'),
                                "balanceOld": item.get('balanceOld'),
                                "startYearPeriod": item.get('startYearPeriod'),
                                "debit": item.get('debit'),
                                "credit": item.get('credit'),
                                "debitFor": item.get('debitFor'),
                                "dc": item.get('dc'),
                            })
