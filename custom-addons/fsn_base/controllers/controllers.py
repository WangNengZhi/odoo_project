# -*- coding: utf-8 -*-
# from odoo import http


# class FsnBase(http.Controller):
#     @http.route('/fsn_base/fsn_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_base/fsn_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_base.listing', {
#             'root': '/fsn_base/fsn_base',
#             'objects': http.request.env['fsn_base.fsn_base'].search([]),
#         })

#     @http.route('/fsn_base/fsn_base/objects/<model("fsn_base.fsn_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_base.object', {
#             'object': obj
#         })
