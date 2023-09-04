# -*- coding: utf-8 -*-
# from odoo import http


# class General(http.Controller):
#     @http.route('/general/general/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/general/general/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('general.listing', {
#             'root': '/general/general',
#             'objects': http.request.env['general.general'].search([]),
#         })

#     @http.route('/general/general/objects/<model("general.general"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('general.object', {
#             'object': obj
#         })
