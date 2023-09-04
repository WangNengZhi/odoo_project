# -*- coding: utf-8 -*-
import json
import traceback
from datetime import datetime
from odoo import http


class TemplateHouse(http.Controller):
    # 同步 GST 数据到中间数据库
    @http.route('/sync_machine_data', auth='user', type='json')
    def sync_machine_data(self, **kw):
        # print('*'*80, 'sync_machine_data')
        # print(*(f'{k}={v}' for k,v in kw.items()))  # start_date=2021-12-01 end_date=2021-12-29
        
        # start_date = datetime(*map(int, start_date.split('-')))  # NameError: name 'start_date' is not defined
        start_date = datetime(*map(int, kw['start_date'].split('-')))
        end_date = datetime(*map(int, kw['end_date'].split('-')))
        try:
            http.request.env["template_machine_record"].sync(start_date, end_date)
        except:
            traceback.print_exc()
            res = dict(status=1, messages="失败！")
        else:
            res = dict(status=0, messages="成功！")
        return json.dumps(res)


#     @http.route('/template_house/template_house/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('template_house.listing', {
#             'root': '/template_house/template_house',
#             'objects': http.request.env['template_house.template_house'].search([]),
#         })

#     @http.route('/template_house/template_house/objects/<model("template_house.template_house"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('template_house.object', {
#             'object': obj
#         })
