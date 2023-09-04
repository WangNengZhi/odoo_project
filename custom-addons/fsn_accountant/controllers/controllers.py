# -*- coding: utf-8 -*-
# from odoo import http


# class FsnAccountant(http.Controller):
#     @http.route('/fsn_accountant/fsn_accountant/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_accountant/fsn_accountant/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_accountant.listing', {
#             'root': '/fsn_accountant/fsn_accountant',
#             'objects': http.request.env['fsn_accountant.fsn_accountant'].search([]),
#         })

#     @http.route('/fsn_accountant/fsn_accountant/objects/<model("fsn_accountant.fsn_accountant"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_accountant.object', {
#             'object': obj
#         })
