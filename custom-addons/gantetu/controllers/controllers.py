# -*- coding: utf-8 -*-
from odoo import http


class Gantetu(http.Controller):
    @http.route('/gantetu/gantetu/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/gantetu/gantetu/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('gantetu.listing', {
            'root': '/gantetu/gantetu',
            'objects': http.request.env['gantetu.gantetu'].search([]),
        })

    @http.route('/gantetu/gantetu/objects/<model("gantetu.gantetu"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('gantetu.object', {
            'object': obj
        })

    @http.route('/api/v1/<string:model>/<int:id>', auth='public')
    def qqqqqqqqqqq(self, **kw):

        print("----------------------------")
        print(kw)


        print(http.request.session)

        # obj = http.request.env['gantetu.gantetu'].search([])
        # print(obj)

        return "Hello, world"
