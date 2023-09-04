# -*- coding: utf-8 -*-
# from odoo import http


# class FsnPlan(http.Controller):
#     @http.route('/fsn_plan/fsn_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_plan/fsn_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_plan.listing', {
#             'root': '/fsn_plan/fsn_plan',
#             'objects': http.request.env['fsn_plan.fsn_plan'].search([]),
#         })

#     @http.route('/fsn_plan/fsn_plan/objects/<model("fsn_plan.fsn_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_plan.object', {
#             'object': obj
#         })
