from datetime import datetime, timedelta
import json

from odoo import http
from odoo.http import request, Response


class WXAPIController(http.Controller):
    '''小程序信息界面信息选择'''

    @http.route('/wechat_api/select_middle_check/', methods=['POST', 'GET'], type='http', auth='public', cors="*", csrf=False)
    def select_middle_check(self, **kw):
        '''中查选择'''
        emp_objs = http.request.env["hr.employee"].sudo().search([("is_delete", "=", False)])
        response_data = {
            'data': [i.name for i in emp_objs]
        }

        response_json = json.dumps(response_data, ensure_ascii=False)
        return http.Response(response_json, content_type='application/json')

    @http.route('/wechat_api/select_group/', methods=['POST', 'GET'], type='http', auth='public', cors="*", csrf=False)
    def select_group(self):
        '''组别选择'''
        # fsn_staff_team_objs = http.request.env["fsn_staff_team"].sudo().search([])
        # response_data = {
        #     'data': [i.name for i in fsn_staff_team_objs]
        # }
        # 获取今天的日期
        today_date = datetime.now().date()
        # 计算三天前的日期
        three_days_ago = today_date - timedelta(days=7)

        # # 测试
        # tmp_custom_date_str = '2023-2-10'
        # tmp_custom_date = datetime.strptime(tmp_custom_date_str, "%Y-%m-%d").date()
        # # 计算三天前的日期
        # three_days_ago = tmp_custom_date - timedelta(days=5)

        # 正式环境筛选日期改成`today_date`和`three_days_ago`
        fsn_staff_team_objs = http.request.env["suspension_system_summary"].sudo().search([('dDate', '>=', three_days_ago),
                                                                                           ('dDate', '<=', today_date)])

        response_data = {
            'data': list(set(i.group.group for i in fsn_staff_team_objs))
        }

        response_json = json.dumps(response_data, ensure_ascii=False)
        return http.Response(response_json, content_type='application/json')


    @http.route('/wechat_api/select_order_no/', methods=['POST', 'GET'], type='http', auth='public', cors="*", csrf=False)
    def select_order_no(self):
        '''订单号选择'''
        # sale_pro_objs = http.request.env["sale_pro.sale_pro"].sudo().search([])
        # response_data = {
        #     'data': [i.order_number for i in sale_pro_objs]
        # }

        # 获取今天的日期
        today_date = datetime.now().date()
        # 计算三天前的日期
        three_days_ago = today_date - timedelta(days=7)

        # # 测试
        # tmp_custom_date_str = '2023-2-10'
        # tmp_custom_date = datetime.strptime(tmp_custom_date_str, "%Y-%m-%d").date()
        # # 计算三天前的日期
        # three_days_ago = tmp_custom_date - timedelta(days=5)

        # 正式环境筛选日期改成`today_date`和`three_days_ago`
        sale_pro_objs = http.request.env["suspension_system_summary"].sudo().search([('dDate', '>=', three_days_ago),
                                                                                    ('dDate', '<=', today_date)])

        unique_order_numbers = list(set(sale.order_number_show for sale in sale_pro_objs))

        response_data = {
            'data': [order_number for order_number in unique_order_numbers]
        }

        response_json = json.dumps(response_data, ensure_ascii=False)
        return http.Response(response_json, content_type='application/json')

    @http.route('/wechat_api/select_item_number/', methods=['POST', 'GET'], type='http', auth='public', cors="*", csrf=False)
    def select_item_number(self):
        '''款号选择'''
        # ib_detail_objs = http.request.env["ib.detail"].sudo().search([])
        # response_data = {
        #     'data': [i.style_number for i in ib_detail_objs]
        # }

        # 获取今天的日期
        today_date = datetime.now().date()
        # 计算三天前的日期
        three_days_ago = today_date - timedelta(days=7)

        # # 测试
        # tmp_custom_date_str = '2023-2-10'
        # tmp_custom_date = datetime.strptime(tmp_custom_date_str, "%Y-%m-%d").date()
        # # 计算三天前的日期
        # three_days_ago = tmp_custom_date - timedelta(days=5)

        # 正式环境筛选日期改成`today_date`和`three_days_ago`
        ib_detail_objs = http.request.env["suspension_system_summary"].sudo().search([('dDate', '>=', three_days_ago),
                                                                                    ('dDate', '<=', today_date)])

        unique_ib_numbers = list(set(ib.MONo for ib in ib_detail_objs))

        response_data = {
            'data': [ib for ib in unique_ib_numbers]
        }

        response_json = json.dumps(response_data, ensure_ascii=False)
        return http.Response(response_json, content_type='application/json')

    @http.route('/wechat_api/get_submit_data/', methods=['POST'], type='json', auth='public', cors="*", csrf=False)
    def get_submit_data(self, **kwargs):
        """提交待审批数据库临时存储"""
        data = request.jsonrequest
        name_id = http.request.env['hr.employee'].sudo().search([("name", "=", data['selectedName1'])]).id  # 中查姓名id

        # group_id = http.request.env['fsn_staff_team'].sudo().search([('name', '=', data['selectedName2'])]).id  # 组别id
        # order_id = http.request.env['sale_pro.sale_pro'].sudo().search(
        #     [('order_number', '=', data['selectedName3'])]).id  # 订单id
        # style_number_id = http.request.env["ib.detail"].sudo().search(
        #     [("style_number", "=", data['selectedName4'])]).id  # 款号id

        group_id = http.request.env['check_position_settings'].sudo().search([('group', '=', data['selectedName2'])]).id

        parking_space_name_id = http.request.env['hr.employee'].sudo().search(
            [("name", "=", data['parkingspacename'])]).id  # 车位名称id

        deliveryDate = data.get('deliveryDate')
        selectedName1 = name_id
        selectedName2 = group_id
        selectedName3 = data.get('selectedName3')
        selectedName4 = data.get('selectedName4')
        numberInspection = data.get('numberInspection')
        numberRepair = data.get('numberRepair')
        numberOfDeliverie = data.get('numberOfDeliverie')
        numberOFSecondary = data.get('numberOFSecondary')
        NumberSecondaryRepairs = data.get('NumberSecondaryRepairs')
        NumberSecondRepairsDelivered = data.get('NumberSecondRepairsDelivered')
        problempoint = data.get('problempoint')
        problempointsnumberno = data.get('problempointsnumberno')
        repairtypename = data.get('repairtypename')
        parkingspacename = parking_space_name_id

        vals = {
            'date': deliveryDate,
            'check_in_name': selectedName1,
            'group': selectedName2,
            'order_number': selectedName3,
            'style_number': selectedName4,
            'large_cargo_inspection_number': numberInspection,
            'number_of_bulk_repairs': numberRepair,
            'number_of_bulk_deliveries': numberOfDeliverie,
            'number_of_secondary_inspections': numberOFSecondary,
            'number_of_secondary_repairs': NumberSecondaryRepairs,
            'number_of_second_repair_deliveries': NumberSecondRepairsDelivered,
            'problems': problempoint,
            'question_points': problempointsnumberno,
            'rework_type': repairtypename,
            'parking_space_name': parkingspacename
        }

        http.request.env['wechat.delivery'].sudo().create(vals)
        return {'result': 'success'}

    @http.route('/wechat_api/obtain_pending/approval_data/', methods=['GET'], type='http', auth='public', cors="*", csrf=False)
    def obtain_pending_approval_data(self):
        """获取待审批数据"""
        # name_id = http.request.env['hr.employee'].sudo().search([("name", "=", data['selectedName1'])]).id  # 中查姓名id
        pending_data = http.request.env['wechat.delivery'].sudo().search([('status', '=', '待审批')])

        if pending_data:
            data = []
            for record in pending_data:
                data.append({
                    'id': record.id,
                    'data': record.date.strftime('%Y-%m-%d'),
                    'check_in_name': record.check_in_name.name if record.check_in_name else '',
                    'group': record.group.group,
                    'order_number': record.order_number if record.order_number else '',
                    'style_number': record.style_number if record.style_number else '',
                    'large_cargo_inspection_number': record.large_cargo_inspection_number,
                    'number_of_bulk_repairs': record.number_of_bulk_repairs,
                    'number_of_bulk_deliveries': record.number_of_bulk_deliveries,
                    'number_of_secondary_inspections': record.number_of_secondary_inspections,
                    'number_of_secondary_repairs': record.number_of_secondary_repairs,
                    'number_of_second_repair_deliveries': record.number_of_second_repair_deliveries,
                    'problems': record.problems,
                    'question_points': record.question_points,
                    'rework_type': record.rework_type,
                    'parking_space_name': record.parking_space_name.name if record.parking_space_name else '',
                    'sp_emp_list': [i.emp_id.barcode for i in record.wechat_delivery_line_ids],
                    # "wechatDeliver_id": [i.id for i in record.wechat_delivery_line_ids]
                })

            json_data = {'data': data}
            response_json = json.dumps(json_data, ensure_ascii=False)
            return http.Response(response_json, content_type='application/json')

        json_data = {'data': []}
        response_json = json.dumps(json_data, ensure_ascii=False)
        return http.Response(response_json, content_type='application/json')


    @http.route('/wechat_api/refuse/', methods=['POST'], type='json', auth='public')
    def refuse(self, **kwargs):
        """更新拒绝审批状态"""
        data = request.jsonrequest
        record = http.request.env['wechat.delivery'].sudo().search([('status', '=', '待审批')])
        record.write({'status': data['status']})
        return  {'result': 'success'}

    @http.route('/wechat_api/pass_through/', methods=['POST'], type='json', auth='public')
    def pass_through(self):
        """更新通过审批状态"""
        data = request.jsonrequest

        emp_obj = http.request.env['hr.employee'].sudo().search([("barcode", "=", data['user'])])

        record = http.request.env['wechat_delivery_line'].sudo().search([
            ('wechat_delivery_id', '=', data['id']),
            ("emp_id", "=", emp_obj.id)
        ])

        if record:
            record.write({
                'status': '审批通过'
            })
        return {'result': 'success'}

    @http.route('/wechat_api/obtain_payable/', methods=['POST'], type='json', auth='public', cors="*", csrf=False)
    def get_obtain_payable(self, **kwargs):
        """获取应交数量"""
        data = request.jsonrequest

        # 获取组别id
        group_id = http.request.env['check_position_settings'].sudo().search([('group', '=', data['group'])], limit=1)
        # # 获取订单号id
        order = http.request.env['sale_pro.sale_pro'].sudo().search([('order_number', '=', data['orderNumber'])]) # 调试使用tmp_order_num正式使用data['orderNumber']
        # # 获取款号id
        item = http.request.env['ib.detail'].sudo().search([('style_number', '=', data['itmerNumber'])]) # 调试使用tmp_item正式使用data['itmerNumber']

        # hang_num = http.request.env['suspension_system_station_summary'].sudo().search([
        #     ('dDate', '=', data['deliveryDate']), # 调试改为tmp_data，正式使用data['deliveryDate']
        #     ('group', '=', group_id.id),
        #     ('station_number', 'not in', group_id.position_line_ids.mapped("position")),
        #     ('order_number', '=', order.id),
        #     ('style_number', '=', item.id)
        # ], order='station_number desc', limit=1)

        # 构建查询条件
        search_domain = [
            ('dDate', '=', data['deliveryDate']),  # 调试改为tmp_data，正式使用data['deliveryDate']
            ('group', '=', group_id.id),
            ('station_number', 'not in', group_id.position_line_ids.mapped("position")),
            ('order_number', '=', order.order_number),
            ('style_number', '=', item.style_number)
        ]

        hang_num = http.request.env['suspension_system_station_summary'].sudo().search(search_domain,
                                                                                       order='total_quantity desc', limit=1)


        data = hang_num.total_quantity
        return {'data': data}


