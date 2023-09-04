# -*- coding: utf-8 -*-
# from odoo import http


# class EquipmentManagement(http.Controller):
#     @http.route('/equipment_management/equipment_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/equipment_management/equipment_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('equipment_management.listing', {
#             'root': '/equipment_management/equipment_management',
#             'objects': http.request.env['equipment_management.equipment_management'].search([]),
#         })

#     @http.route('/equipment_management/equipment_management/objects/<model("equipment_management.equipment_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('equipment_management.object', {
#             'object': obj
#         })
