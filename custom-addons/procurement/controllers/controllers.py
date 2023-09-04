# -*- coding: utf-8 -*-
# from odoo import http


# class Procurement(http.Controller):
#     @http.route('/procurement/procurement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/procurement/procurement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('procurement.listing', {
#             'root': '/procurement/procurement',
#             'objects': http.request.env['procurement.procurement'].search([]),
#         })

#     @http.route('/procurement/procurement/objects/<model("procurement.procurement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('procurement.object', {
#             'object': obj
#         })
