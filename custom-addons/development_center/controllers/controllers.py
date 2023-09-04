# -*- coding: utf-8 -*-
# from odoo import http


# class DevelopmentCenter(http.Controller):
#     @http.route('/development_center/development_center/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/development_center/development_center/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('development_center.listing', {
#             'root': '/development_center/development_center',
#             'objects': http.request.env['development_center.development_center'].search([]),
#         })

#     @http.route('/development_center/development_center/objects/<model("development_center.development_center"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('development_center.object', {
#             'object': obj
#         })
