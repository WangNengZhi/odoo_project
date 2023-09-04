# -*- coding: utf-8 -*-
# from odoo import http


# class FsnSale(http.Controller):
#     @http.route('/fsn_sale/fsn_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_sale/fsn_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_sale.listing', {
#             'root': '/fsn_sale/fsn_sale',
#             'objects': http.request.env['fsn_sale.fsn_sale'].search([]),
#         })

#     @http.route('/fsn_sale/fsn_sale/objects/<model("fsn_sale.fsn_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_sale.object', {
#             'object': obj
#         })
