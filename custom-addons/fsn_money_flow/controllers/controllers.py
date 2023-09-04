# -*- coding: utf-8 -*-
# from odoo import http


# class FsnMoneyFlow(http.Controller):
#     @http.route('/fsn_money_flow/fsn_money_flow/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_money_flow/fsn_money_flow/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_money_flow.listing', {
#             'root': '/fsn_money_flow/fsn_money_flow',
#             'objects': http.request.env['fsn_money_flow.fsn_money_flow'].search([]),
#         })

#     @http.route('/fsn_money_flow/fsn_money_flow/objects/<model("fsn_money_flow.fsn_money_flow"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_money_flow.object', {
#             'object': obj
#         })
