from odoo import http


# class WorkwxFsnBaseInfoSelect(http.Controller):
#     ''' 企业微信：基础信息选择选择'''
#
#
#     @http.route('/workwx_api/v1/fsn_order_number_select/', methods=['POST', 'GET'], type='http', auth='public')
#     def fsn_order_number_select(self, **kw):
#         ''' 企业微信：订单编号选择'''
#
#         sale_pro_objs = http.request.env["sale_pro.sale_pro"].sudo().search([])
#         datas = {
#             "key": kw.get("key"),
#             "value_list": [{"id": i.id, "name": i.order_number} for i in sale_pro_objs],
#         }
#
#         return http.request.render("fsn_workwx_extension.workwx_select_page", {"datas": datas})
#
#
#     @http.route('/workwx_api/v1/fsn_size_select/', methods=['POST', 'GET'], type='http', auth='public')
#     def fsn_size_select(self, **kw):
#         ''' 企业微信：尺码选择'''
#
#         fsn_size_objs = http.request.env["fsn_size"].sudo().search([])
#         datas = {
#             "key": kw.get("key"),
#             "value_list": [{"id": i.id, "name": i.name} for i in fsn_size_objs],
#         }
#
#         return http.request.render("fsn_workwx_extension.workwx_select_page", {"datas": datas})
#
#
#     @http.route('/workwx_api/v1/fsn_style_number_select/', methods=['POST', 'GET'], type='http', auth='public')
#     def fsn_style_number_select(self, **kw):
#         ''' 企业微信：款式编号选择'''
#
#         ib_detail_objs = http.request.env["ib.detail"].sudo().search([])
#         datas = {
#             "key": kw.get("key"),
#             "value_list": [{"id": i.id, "name": i.style_number} for i in ib_detail_objs],
#         }
#
#         return http.request.render("fsn_workwx_extension.workwx_select_page", {"datas": datas})
#
#
#     @http.route('/workwx_api/v1/fsn_staff_team_select/', methods=['POST', 'GET'], type='http', auth='public')
#     def fsn_staff_team_select(self, **kw):
#         ''' 企业微信：员工小组选择'''
#
#         fsn_staff_team_objs = http.request.env["fsn_staff_team"].sudo().search([])
#         datas = {
#             "key": kw.get("key"),
#             "value_list": [{"id": i.id, "name": i.name} for i in fsn_staff_team_objs],
#         }
#
#         return http.request.render("fsn_workwx_extension.workwx_select_page", {"datas": datas})
#
#
#     @http.route('/workwx_api/v1/fsn_employee_select/', methods=['POST', 'GET'], type='http', auth='public')
#     def fsn_employee_select(self, **kw):
#         ''' 企业微信：员工选择'''
#
#         emp_objs = http.request.env["hr.employee"].sudo().search([("is_delete", "=", False)])
#         datas = {
#             "key": kw.get("key"),
#             "value_list": [{"id": i.id, "name": i.name} for i in emp_objs],
#         }
# 
#         return http.request.render("fsn_workwx_extension.workwx_select_page", {"datas": datas})
