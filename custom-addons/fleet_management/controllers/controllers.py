# -*- coding: utf-8 -*-
# from odoo import http


# class FleetManagement(http.Controller):
#     @http.route('/fleet_management/fleet_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_management/fleet_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_management.listing', {
#             'root': '/fleet_management/fleet_management',
#             'objects': http.request.env['fleet_management.fleet_management'].search([]),
#         })

#     @http.route('/fleet_management/fleet_management/objects/<model("fleet_management.fleet_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_management.object', {
#             'object': obj
#         })
