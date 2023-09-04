# -*- coding: utf-8 -*-
# from odoo import http


# class FsnRecruitment(http.Controller):
#     @http.route('/fsn_recruitment/fsn_recruitment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_recruitment/fsn_recruitment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_recruitment.listing', {
#             'root': '/fsn_recruitment/fsn_recruitment',
#             'objects': http.request.env['fsn_recruitment.fsn_recruitment'].search([]),
#         })

#     @http.route('/fsn_recruitment/fsn_recruitment/objects/<model("fsn_recruitment.fsn_recruitment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_recruitment.object', {
#             'object': obj
#         })
