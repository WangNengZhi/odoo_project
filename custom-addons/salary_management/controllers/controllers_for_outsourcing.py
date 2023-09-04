import traceback, json
from odoo.exceptions import ValidationError
from odoo import http


class Outsourcing(http.Controller):

    @http.route('/outsourcing_wages_per_work_time', auth='user', type='json')
    def foo(self, **kw):
        year, month = map(int, kw['month'].split('-'))
        try:
            http.request.env["outsourcing_wages"].outsourcing_wages_per_work_time(year, month)
        except:
            traceback.print_exc()
            res = dict(status=1, messages="失败！")
        else:
            res = dict(status=0, messages="成功！")
        return json.dumps(res)


    @http.route('/outsourcing_wages_for_work_done', auth='user', type='json')
    def outsourcing_wages_for_work_done(self, **kw):
        year, month = map(int, kw['month'].split('-'))
        try:
            http.request.env["outsourcing_wages"].outsourcing_wages_for_work_done(year, month)
        except:
            traceback.print_exc()
            res = dict(status=1, messages="失败！")
        else:
            res = dict(status=0, messages="成功！")
        return json.dumps(res)
