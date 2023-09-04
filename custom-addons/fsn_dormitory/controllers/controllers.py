# -*- coding: utf-8 -*-
# from odoo import http


# class FsnDormitory(http.Controller):
#     @http.route('/fsn_dormitory/fsn_dormitory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_dormitory/fsn_dormitory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_dormitory.listing', {
#             'root': '/fsn_dormitory/fsn_dormitory',
#             'objects': http.request.env['fsn_dormitory.fsn_dormitory'].search([]),
#         })

#     @http.route('/fsn_dormitory/fsn_dormitory/objects/<model("fsn_dormitory.fsn_dormitory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_dormitory.object', {
#             'object': obj
#         })
