# -*- coding: utf-8 -*-
# from odoo import http


# class FsnProduction(http.Controller):
#     @http.route('/fsn_production/fsn_production/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_production/fsn_production/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_production.listing', {
#             'root': '/fsn_production/fsn_production',
#             'objects': http.request.env['fsn_production.fsn_production'].search([]),
#         })

#     @http.route('/fsn_production/fsn_production/objects/<model("fsn_production.fsn_production"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_production.object', {
#             'object': obj
#         })
