# -*- coding: utf-8 -*-
# from odoo import http


# class FsnEmployee(http.Controller):
#     @http.route('/fsn_employee/fsn_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_employee/fsn_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_employee.listing', {
#             'root': '/fsn_employee/fsn_employee',
#             'objects': http.request.env['fsn_employee.fsn_employee'].search([]),
#         })

#     @http.route('/fsn_employee/fsn_employee/objects/<model("fsn_employee.fsn_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_employee.object', {
#             'object': obj
#         })
