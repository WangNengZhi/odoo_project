# -*- coding: utf-8 -*-
# from odoo import http


# class FsnKpi(http.Controller):
#     @http.route('/fsn_kpi/fsn_kpi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_kpi/fsn_kpi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_kpi.listing', {
#             'root': '/fsn_kpi/fsn_kpi',
#             'objects': http.request.env['fsn_kpi.fsn_kpi'].search([]),
#         })

#     @http.route('/fsn_kpi/fsn_kpi/objects/<model("fsn_kpi.fsn_kpi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_kpi.object', {
#             'object': obj
#         })
