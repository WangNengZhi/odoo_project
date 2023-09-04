# -*- coding: utf-8 -*-
# from odoo import http


# class FsnSetting(http.Controller):
#     @http.route('/fsn_setting/fsn_setting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_setting/fsn_setting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_setting.listing', {
#             'root': '/fsn_setting/fsn_setting',
#             'objects': http.request.env['fsn_setting.fsn_setting'].search([]),
#         })

#     @http.route('/fsn_setting/fsn_setting/objects/<model("fsn_setting.fsn_setting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_setting.object', {
#             'object': obj
#         })
