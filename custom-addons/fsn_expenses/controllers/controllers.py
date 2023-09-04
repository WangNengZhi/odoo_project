# -*- coding: utf-8 -*-
# from odoo import http


# class FsnExpenses(http.Controller):
#     @http.route('/fsn_expenses/fsn_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_expenses/fsn_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_expenses.listing', {
#             'root': '/fsn_expenses/fsn_expenses',
#             'objects': http.request.env['fsn_expenses.fsn_expenses'].search([]),
#         })

#     @http.route('/fsn_expenses/fsn_expenses/objects/<model("fsn_expenses.fsn_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_expenses.object', {
#             'object': obj
#         })
