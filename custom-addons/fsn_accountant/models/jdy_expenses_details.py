from datetime import datetime

from odoo import models, fields, api
import requests


class JdyExpensesDetails(models.Model):
    _name = 'jdy_expenses_details'
    _description = '精斗云会计费用明细'
    _rec_name = 'jdy_subject_id'

    month = fields.Char(string="月份")
    jdy_subject_id = fields.Many2one("jdy_subject", string="所属科目")
    parent_jdy_subject_id = fields.Many2one("jdy_subject", string="父级科目")
    expense = fields.Float(string="费用")



    def sync_schedule_of_expenses(self, today):
        ''' 同步精斗云会计费用明细表'''

        *year_month, _ = str(today).split("-")
        toPeriod = ''.join(year_month)
   

        app_key = self.env.ref('fsn_accountant.jdy_setting_app_key').value
        app_secret = self.env.ref('fsn_accountant.jdy_setting_app_secret').value
        client_id = self.env.ref('fsn_accountant.jdy_setting_client_id').value
        client_secret = self.env.ref('fsn_accountant.jdy_setting_client_secret').value
        outer_instance_id = self.env.ref('fsn_accountant.jdy_setting_outer_instance_id').value

        url = 'https://api.kingdee.com/jdyaccouting/report/expenseDetail'


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
            'fromPeriod': 202301,
            'toPeriod': toPeriod,
            # 'accountNum': 5601,
        }

        jdy_subject_objs = self.env['jdy_subject'].sudo().search([("classId", "=", "5"), ("level", "=", 1)])

        for jdy_subject_obj in jdy_subject_objs:
            querystring['accountNum'] = jdy_subject_obj.number

            response = requests.request("GET", url=url, headers=headers, params=querystring)
            response = response.json()
            if response['status'] == 250:
                continue
            else:
                for items in response['data']['items']:
                    for key, value in items['period_expense'].items():
                        if items['level'] == 2:
                            key = key[0: 4] + "-" + key[4:]
                            jdy_expenses_details_obj = self.env['jdy_expenses_details'].sudo().search([("month", "=", key), ("jdy_subject_id.number", "=", items['number'])])
                            if not jdy_expenses_details_obj:
                                jdy_expenses_details_obj = self.env['jdy_expenses_details'].sudo().create({
                                    "month": key,
                                    "jdy_subject_id": self.env['jdy_subject'].sudo().search([("subject_id", "=", items['accountId'])]).id,
                                    "parent_jdy_subject_id": self.env['jdy_subject'].sudo().search([("subject_id", "=", items['parentId'])]).id,
                                })

                            jdy_expenses_details_obj.expense = value
