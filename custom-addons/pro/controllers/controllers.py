# -*- coding: utf-8 -*-
# from odoo import http


# class Pro(http.Controller):
#     @http.route('/pro/pro/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pro/pro/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pro.listing', {
#             'root': '/pro/pro',
#             'objects': http.request.env['pro.pro'].search([]),
#         })

#     @http.route('/pro/pro/objects/<model("pro.pro"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pro.object', {
#             'object': obj
#         })
