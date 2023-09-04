# -*- coding: utf-8 -*-
# from odoo import http


# class FsnDesignDepartment(http.Controller):
#     @http.route('/fsn_design_department/fsn_design_department/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_design_department/fsn_design_department/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_design_department.listing', {
#             'root': '/fsn_design_department/fsn_design_department',
#             'objects': http.request.env['fsn_design_department.fsn_design_department'].search([]),
#         })

#     @http.route('/fsn_design_department/fsn_design_department/objects/<model("fsn_design_department.fsn_design_department"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_design_department.object', {
#             'object': obj
#         })
