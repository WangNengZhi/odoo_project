from odoo import models, fields, api
import requests

class JdySubject(models.Model):
    _name = 'jdy_subject'
    _description = '精斗云会计科目'
    _rec_name = 'name'

    classId = fields.Selection([('1','资产'), ('2','负债'), ('3','权益'), ('4','成本'), ('5','损益'), ('5','共同')], string='类别')
    subject_id = fields.Char(string="科目ID")
    number = fields.Char(string="科目代码")
    name = fields.Char(string="科目名称")
    fullName = fields.Char(string="科目全称")
    level = fields.Integer(string="科目级次")
    parentId = fields.Char(string="父级科目ID")
    rootId = fields.Char(string="根科目ID")


    groupId = fields.Char(string="科目类别ID")
    groupName = fields.Char(string="科目类别名称")
    isDetail = fields.Boolean(string="是否明细科目")
    dc = fields.Selection([('1','借方科目'), ('-1','贷方科目')], string='余额方向')


    currency = fields.Char(string="货币代码")




    def sync_jdy_subject(self):
        ''' 同步精斗云会计科目'''

        app_key = self.env.ref('fsn_accountant.jdy_setting_app_key').value
        app_secret = self.env.ref('fsn_accountant.jdy_setting_app_secret').value
        client_id = self.env.ref('fsn_accountant.jdy_setting_client_id').value
        client_secret = self.env.ref('fsn_accountant.jdy_setting_client_secret').value
        outer_instance_id = self.env.ref('fsn_accountant.jdy_setting_outer_instance_id').value

        url = 'https://api.kingdee.com/jdyaccouting/account'

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
        }

        for classId in map(str, range(1, 6)):

            querystring['classId'] = classId

            response = requests.request("GET", url=url, headers=headers, params=querystring)
            response = response.json()
            # print(response)
            for i in response['list']:

                if not self.env['jdy_subject'].search([("number", "=", i['number'])]):
                    self.env['jdy_subject'].create({
                        "classId": classId,
                        "subject_id": i['id'],
                        "number": i['number'],
                        "name": i['name'],
                        "fullName": i['fullname'],
                        "level": i['level'],
                        "parentId": i['parentId'],
                        "rootId": i['rootId'],
                        "groupId": i['groupId'],
                        "groupName": i['groupName'],
                        "isDetail": i['isDetail'],
                        "dc": str(i['dc']),
                        "currency": i['currency']
                    })
                    
        return True







