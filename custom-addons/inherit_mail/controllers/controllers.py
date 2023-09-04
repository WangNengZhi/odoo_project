# -*- coding: utf-8 -*-
from odoo import http


class InheritMail(http.Controller):

    # 判断日报刷新权限
    @http.route('/inherit_mail/daily_newspaper_refresh/', methods=['POST', 'GET'], type='json', auth="user")
    def check_daily_newspaper_refresh(self, **kw):

        user_id = http.request.env.uid
        fsn_super_user_group = http.request.env.ref('inherit_mail.fsn_daily_newspaper_refresh_group')

        # 判断是否有权限！
        if user_id in fsn_super_user_group.users.ids:
            return {"is_show": True}
        else:
            return {"is_show": False}