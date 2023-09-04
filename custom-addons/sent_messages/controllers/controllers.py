# -*- coding: utf-8 -*-
# from odoo import http


# class ModHello(http.Controller):
#     @http.route('/mod_hello/mod_hello/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mod_hello/mod_hello/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mod_hello.listing', {
#             'root': '/mod_hello/mod_hello',
#             'objects': http.request.env['mod_hello.mod_hello'].search([]),
#         })

#     @http.route('/mod_hello/mod_hello/objects/<model("mod_hello.mod_hello"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mod_hello.object', {
#             'object': obj
#         })
