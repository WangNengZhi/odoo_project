# -*- coding: utf-8 -*-
# from odoo import http


# class SalePro(http.Controller):
#     @http.route('/sale_pro/sale_pro/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_pro/sale_pro/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_pro.listing', {
#             'root': '/sale_pro/sale_pro',
#             'objects': http.request.env['sale_pro.sale_pro'].search([]),
#         })

#     @http.route('/sale_pro/sale_pro/objects/<model("sale_pro.sale_pro"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_pro.object', {
#             'object': obj
#         })
