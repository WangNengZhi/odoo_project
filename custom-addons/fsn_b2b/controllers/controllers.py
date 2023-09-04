# -*- coding: utf-8 -*-
# from odoo import http


# class FsnP2p(http.Controller):
#     @http.route('/fsn_p2p/fsn_p2p/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fsn_p2p/fsn_p2p/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fsn_p2p.listing', {
#             'root': '/fsn_p2p/fsn_p2p',
#             'objects': http.request.env['fsn_p2p.fsn_p2p'].search([]),
#         })

#     @http.route('/fsn_p2p/fsn_p2p/objects/<model("fsn_p2p.fsn_p2p"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fsn_p2p.object', {
#             'object': obj
#         })
