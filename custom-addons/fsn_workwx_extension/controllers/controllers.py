# -*- coding: utf-8 -*-
# from odoo import http


# class FsnWorkwxExtension(http.Controller):
#     @http.route('/fsn_workwx_extension/fsn_workwx_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_workwx_extension/fsn_workwx_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_workwx_extension.listing', {
#             'root': '/fsn_workwx_extension/fsn_workwx_extension',
#             'objects': http.request.env['fsn_workwx_extension.fsn_workwx_extension'].search([]),
#         })

#     @http.route('/fsn_workwx_extension/fsn_workwx_extension/objects/<model("fsn_workwx_extension.fsn_workwx_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_workwx_extension.object', {
#             'object': obj
#         })
