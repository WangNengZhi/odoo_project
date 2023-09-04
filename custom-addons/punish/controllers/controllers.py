# -*- coding: utf-8 -*-
from odoo import http
import traceback
import json
import datetime
from dateutil.relativedelta import relativedelta


class Punish(http.Controller):
    @http.route('/punish/punish/', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/punish/punish/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('punish.listing', {
#             'root': '/punish/punish',
#             'objects': http.request.env['punish.punish'].search([]),
#         })

#     @http.route('/punish/punish/objects/<model("punish.punish"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('punish.object', {
#             'object': obj
#         })

    @http.route('/hard_working_workers_of_year', auth='user', type='json')
    def hard_working_workers_of_year(self, **kw):
        # print('*'*80, 'hard_working_workers_of_year (controler)')
        # print(kw)



        end_month = tuple(map(int, kw['end_month'].split('-')))

        start_month = (end_month[0]-1, end_month[1])

        try:
            http.request.env["hard_working_workers_of_year"].stats(start_month, end_month, 15, 2)
        except:
            traceback.print_exc()
            res = dict(status=1, messages="失败！")
        else:
            res = dict(status=0, messages="成功！")
        return json.dumps(res)
