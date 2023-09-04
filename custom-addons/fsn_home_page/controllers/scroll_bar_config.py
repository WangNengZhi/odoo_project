# -*- coding: utf-8 -*-
from odoo import http


class FsnHomePage(http.Controller):

    @http.route('/fsn_home_page/get_visibility_scroll_bar_info/', auth='user', type='json')
    def get_visibility_scroll_bar_info(self, **kw):

        user_id = kw.get("user_id")

        scroll_bar_config_objs = http.request.env['scroll_bar_config'].sudo().search([("is_enable", "=", True)])

        text = "，".join([i.content for i in scroll_bar_config_objs if user_id in i.user_ids.ids])

        return {"text": text}
