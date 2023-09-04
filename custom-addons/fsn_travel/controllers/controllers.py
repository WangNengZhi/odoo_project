# -*- coding: utf-8 -*-
# from odoo import http


# class FsnTravel(http.Controller):
#     @http.route('/fsn_travel/fsn_travel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_travel/fsn_travel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_travel.listing', {
#             'root': '/fsn_travel/fsn_travel',
#             'objects': http.request.env['fsn_travel.fsn_travel'].search([]),
#         })

#     @http.route('/fsn_travel/fsn_travel/objects/<model("fsn_travel.fsn_travel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_travel.object', {
#             'object': obj
#         })
