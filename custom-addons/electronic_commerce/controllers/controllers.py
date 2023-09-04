# -*- coding: utf-8 -*-
# from odoo import http


# class ElectronicCommerce(http.Controller):
#     @http.route('/electronic_commerce/electronic_commerce/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/electronic_commerce/electronic_commerce/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('electronic_commerce.listing', {
#             'root': '/electronic_commerce/electronic_commerce',
#             'objects': http.request.env['electronic_commerce.electronic_commerce'].search([]),
#         })

#     @http.route('/electronic_commerce/electronic_commerce/objects/<model("electronic_commerce.electronic_commerce"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('electronic_commerce.object', {
#             'object': obj
#         })
