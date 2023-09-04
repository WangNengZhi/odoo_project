# -*- coding: utf-8 -*-
# from odoo import http


# class FsnBom(http.Controller):
#     @http.route('/fsn_bom/fsn_bom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_bom/fsn_bom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_bom.listing', {
#             'root': '/fsn_bom/fsn_bom',
#             'objects': http.request.env['fsn_bom.fsn_bom'].search([]),
#         })

#     @http.route('/fsn_bom/fsn_bom/objects/<model("fsn_bom.fsn_bom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_bom.object', {
#             'object': obj
#         })
