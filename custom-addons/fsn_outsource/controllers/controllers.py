# -*- coding: utf-8 -*-
# from odoo import http


# class FsnOutsource(http.Controller):
#     @http.route('/fsn_outsource/fsn_outsource/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_outsource/fsn_outsource/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_outsource.listing', {
#             'root': '/fsn_outsource/fsn_outsource',
#             'objects': http.request.env['fsn_outsource.fsn_outsource'].search([]),
#         })

#     @http.route('/fsn_outsource/fsn_outsource/objects/<model("fsn_outsource.fsn_outsource"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_outsource.object', {
#             'object': obj
#         })
