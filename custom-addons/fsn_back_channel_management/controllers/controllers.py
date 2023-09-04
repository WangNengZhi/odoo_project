# -*- coding: utf-8 -*-
# from odoo import http


# class FsnBackChannelManagement(http.Controller):
#     @http.route('/fsn_back_channel_management/fsn_back_channel_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_back_channel_management/fsn_back_channel_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_back_channel_management.listing', {
#             'root': '/fsn_back_channel_management/fsn_back_channel_management',
#             'objects': http.request.env['fsn_back_channel_management.fsn_back_channel_management'].search([]),
#         })

#     @http.route('/fsn_back_channel_management/fsn_back_channel_management/objects/<model("fsn_back_channel_management.fsn_back_channel_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_back_channel_management.object', {
#             'object': obj
#         })
