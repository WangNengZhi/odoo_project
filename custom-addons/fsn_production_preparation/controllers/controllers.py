# -*- coding: utf-8 -*-
# from odoo import http


# class FsnProductionPreparation(http.Controller):
#     @http.route('/fsn_production_preparation/fsn_production_preparation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_production_preparation/fsn_production_preparation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_production_preparation.listing', {
#             'root': '/fsn_production_preparation/fsn_production_preparation',
#             'objects': http.request.env['fsn_production_preparation.fsn_production_preparation'].search([]),
#         })

#     @http.route('/fsn_production_preparation/fsn_production_preparation/objects/<model("fsn_production_preparation.fsn_production_preparation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_production_preparation.object', {
#             'object': obj
#         })
