# -*- coding: utf-8 -*-
# from odoo import http


# class FsnSaleManagement(http.Controller):
#     @http.route('/fsn_sale_management/fsn_sale_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_sale_management/fsn_sale_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_sale_management.listing', {
#             'root': '/fsn_sale_management/fsn_sale_management',
#             'objects': http.request.env['fsn_sale_management.fsn_sale_management'].search([]),
#         })

#     @http.route('/fsn_sale_management/fsn_sale_management/objects/<model("fsn_sale_management.fsn_sale_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_sale_management.object', {
#             'object': obj
#         })
