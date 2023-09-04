from odoo import http


class DataExportSetting(http.Controller):
    # 导出权限判断
    @http.route('/fsn_base/check_the_permissions/', methods=['POST', 'GET'], type='json', auth="user")
    def check_the_permissions(self, **kw):

        model_name = kw.get("model")
        user_id = kw.get("user_id")
        is_show = False

        ir_model_obj = http.request.env["ir.model"].sudo().search([("model", "=", model_name)])

        data_export_setting_obj = http.request.env["data_export_setting"].sudo().search([("model_id", "=", ir_model_obj.id)])

        if data_export_setting_obj and user_id in data_export_setting_obj.users.ids:
            is_show = True

        return {"is_show": is_show}

    # FSN超级用户权限判断
    @http.route('/fsn_base/check_is_super_user/', methods=['POST', 'GET'], type='json', auth="user")
    def check_is_super_user(self, **kw):

        user_id = http.request.env.uid
        fsn_super_user_group = http.request.env.ref('fsn_base.fsn_super_user_group')

        # 判断是否是管理员！
        if user_id in fsn_super_user_group.users.ids:
            return {"is_show": True}
        else:
            return {"is_show": False}


