# -*- coding: utf-8 -*-
# from odoo import http


# class FsnPayWay(http.Controller):
#     @http.route('/fsn_pay_way/fsn_pay_way/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_pay_way/fsn_pay_way/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_pay_way.listing', {
#             'root': '/fsn_pay_way/fsn_pay_way',
#             'objects': http.request.env['fsn_pay_way.fsn_pay_way'].search([]),
#         })

#     @http.route('/fsn_pay_way/fsn_pay_way/objects/<model("fsn_pay_way.fsn_pay_way"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_pay_way.object', {
#             'object': obj
#         })
