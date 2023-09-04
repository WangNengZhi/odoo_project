from odoo import http
import json
# from datetime import datetime
import requests


class WxChangePassword(http.Controller):

    # 微信小程序修改密码接口
    @http.route('/wx_change_password/wx_change_password/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def wx_change_password(self, **kw):

        res = http.request.jsonrequest

        user = res.get("user", None)    # 用户名
        password = res.get("password", None)    # 密码

        hr_employee_obj = http.request.env["hr.employee"].sudo().search([("barcode", "=", user)])

        is_modify = hr_employee_obj.sudo().write({
            "wx_password": password
        })

        if hr_employee_obj:
            return json.dumps({'status': "1", 'messages': "登录成功！", "is_modify": is_modify})
        else:
            return json.dumps({'status': "0", 'messages': "用户名或密码错误！"})