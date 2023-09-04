# -*- coding: utf-8 -*-
from odoo import http


class MyDashboard(http.Controller):
    @http.route('/my_dashboard/my_dashboard/', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/my_dashboard/my_dashboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_dashboard.listing', {
#             'root': '/my_dashboard/my_dashboard',
#             'objects': http.request.env['my_dashboard.my_dashboard'].search([]),
#         })

#     @http.route('/my_dashboard/my_dashboard/objects/<model("my_dashboard.my_dashboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_dashboard.object', {
#             'object': obj
#         })
