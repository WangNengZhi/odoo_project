# -*- coding: utf-8 -*-
# from odoo import http


# class FsnTimedTask(http.Controller):
#     @http.route('/fsn_timed_task/fsn_timed_task/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_timed_task/fsn_timed_task/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_timed_task.listing', {
#             'root': '/fsn_timed_task/fsn_timed_task',
#             'objects': http.request.env['fsn_timed_task.fsn_timed_task'].search([]),
#         })

#     @http.route('/fsn_timed_task/fsn_timed_task/objects/<model("fsn_timed_task.fsn_timed_task"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_timed_task.object', {
#             'object': obj
#         })
