# -*- coding: utf-8 -*-

from odoo import http
import json
from datetime import datetime
import requests
import pymssql

import logging

_logger = logging.getLogger(__name__)


class FsnWechatExtension(http.Controller):

    # 检测权限
    def check_wx_permissions(self, hr_employee_obj):

        wechat_extension_group_name_list = http.request.env["wechat_extension_group"].sudo().search([('job_ids', 'in', hr_employee_obj.job_id.id)]).mapped('name')

        return wechat_extension_group_name_list

    # 微信小程序登录接口
    @http.route('/fsn_wechat_extension/wx_login/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def wx_login(self, **kw):

        res = http.request.jsonrequest

        user = res.get("user", None)    # 用户名
        password = res.get("password", None)    # 密码


        hr_employee_obj = http.request.env["hr.employee"].sudo().search([("barcode", "=", user), ("wx_password", "=", password), ("is_delete", "=", False)])

        permissions_list = self.check_wx_permissions(hr_employee_obj)

        if hr_employee_obj:
            return json.dumps({'status': "1", 'messages': "登录成功！", 'permissions_list': permissions_list})
        else:
            return json.dumps({'status': "0", 'messages': "用户名或密码错误！"})



    # 获取吊挂工序数据
    @http.route('/fsn_wechat_extension/get_process_line/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def get_process_line(self, **kw):

        # 日期
        today = http.request.jsonrequest.get("date", None)
        # 工号
        work_number = http.request.jsonrequest.get("work_number", None)

        if today and work_number:
            hr_employee_obj = http.request.env["hr.employee"].sudo().search([("barcode", "=", work_number)])

            if hr_employee_obj:

                dg_objs = http.request.env["suspension_system_station_summary"].sudo().search([
                    ("dDate", "=", today),  # 日期
                    ("employee_id", "=", hr_employee_obj.id),   # 员工
                ])

                process_list = []   # 工序列表

                for dg_obj in dg_objs:

                    for line_obj in dg_obj.line_lds:

                        process_list.append({
                            "date": today,  # 日期
                            "employee_name": hr_employee_obj.name,  # 员工名称
                            "station_number": dg_obj.station_number,    # 站位号
                            "group": dg_obj.group.group,    # 组别
                            "style_number": dg_obj.MONo,   # 款号
                            "process_number": line_obj.SeqNo,   # 工序号
                            "number": line_obj.number,      # 件数

                            "employee_id": hr_employee_obj.id,  # 员工id
                        })

                return json.dumps({'status': "1", 'messages': "成功！", "data": process_list})

            else:
                return json.dumps({'status': "0", 'messages': "没有查询到该员工！可能员工编号有误！"})
        else:

            return json.dumps({'status': "0", 'messages': "没填写日期或者工号！"})




    # 设置员工确认状态
    @http.route('/fsn_wechat_extension/set_any_objection/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def set_any_objection(self, *args, **kwargs):

        # 日期
        today = http.request.jsonrequest.get("date", None)
        # 工号
        work_number = http.request.jsonrequest.get("work_number", None)


        if today and work_number:
            hr_employee_obj = http.request.env["hr.employee"].sudo().search([("barcode", "=", work_number)])

            if hr_employee_obj:

                dg_objs = http.request.env["suspension_system_station_summary"].sudo().search([
                    ("dDate", "=", today),   # 日期
                    ("employee_id", "=", hr_employee_obj.id)  # 员工
                ])
                for dg_obj in dg_objs:
                    dg_obj.line_lds.write({"is_affirm_state": "已确认"})

                return json.dumps({'status': "1", 'messages': "成功！", "data": ""})
            else:
                return json.dumps({'status': "0", 'messages': "没有查询到该员工！可能员工编号有误！"})
        else:

            return json.dumps({'status': "0", 'messages': "没填写日期或者工号！"})


    # 获取全部组别
    @http.route('/fsn_wechat_extension/get_group_data/', auth='public', type='http', methods=['GET'])
    def get_group_data(self, *args, **kwargs):

        group_list = http.request.env["check_position_settings"].sudo().search([]).search_read([], ["line_number", "group"])

        return json.dumps({'status': "1", 'messages': "成功", 'data': group_list})


    # 获取吊挂站位信息
    @http.route('/fsn_wechat_extension/get_dg_stations_info/', auth='public', type='http', methods=['GET'])
    def get_dg_stations_info(self, *args, **kwargs):

        LineID = kwargs.get("LineID")
        StationID = kwargs.get("StationID")

        dg_host = http.request.env.company.dg_host      # ip
        dg_port = http.request.env.company.dg_port      # 端口号

        url = f'http://{dg_host}:{dg_port}/DgApi/stations'

        data= {'LineID': LineID, 'StationID': StationID}

        res = requests.get(url, params=data)
        res = json.loads(res.text)

        return res


    # 获取零号站位工序
    def get_zero_process(self):
        pass


    # 获取站位当前工序
    @http.route('/fsn_wechat_extension/get_dg_stations_process/', auth='public', type='http', methods=['GET'])
    def get_dg_stations_process(self, *args, **kwargs):

        LineID = kwargs.get("group_choose")     # 线号
        StationID = kwargs.get("position_number")   # 站位号

        dg_db_server = http.request.env["fsn_dg_setting"].sudo().search([("key", "=", "吊挂数据库ip")], limit=1).value
        dg_db_user = http.request.env["fsn_dg_setting"].sudo().search([("key", "=", "吊挂数据库用户名")], limit=1).value
        dg_db_password = http.request.env["fsn_dg_setting"].sudo().search([("key", "=", "吊挂数据库密码")], limit=1).value
        dg_db_database = http.request.env["fsn_dg_setting"].sudo().search([("key", "=", "吊挂数据库名")], limit=1).value

        """连接数据库"""
        conn = pymssql.connect(dg_db_server, dg_db_user, dg_db_password, dg_db_database)
        cursor = conn.cursor()

        process_list = []


        res = self.get_dg_stations_info(LineID=LineID, StationID=StationID)
        position_datas = res.get("Data")

        # style_number = ""


        if position_datas:
            # 1-23站位
            if len(position_datas) == 1:

                for position_data in position_datas:

                    cursor.execute("exec [pc_GetStationSeq] '{Line_guid}'".format(Line_guid=position_data.get("Line_guid")))
                    result = cursor.fetchall()  #得到结果集
                    for record in result:

                        if position_data.get("StationID") == record[2]:
                            process_list.append({
                                "process_number": record[3],    # 工序号
                                # "process_describe": record[4],  # 工序描述
                                "style_number": record[5]   # 款号
                            })

                        # style_number = record[5]
            # 挂片站
            else:
                is_list = []
                not_list = []

                position_data = position_datas[0]
                # 查询有站位的工序
                cursor.execute("exec [pc_GetStationSeq] '{Line_guid}'".format(Line_guid=position_data.get("Line_guid")))
                is_position_result = cursor.fetchall()

                for i in is_position_result:
                    is_list.append(i[3])

                package_name = is_position_result[0][-1]    # 方案名称
                # 查询方案id
                cursor.execute(f"SELECT * FROM tRoute WHERE RouteName = '{package_name}';")
                result = cursor.fetchall()

                route_guid = result[0][0]   # 方案id
                # 查询方案全部工序
                cursor.execute(f"SELECT * FROM  tSeqAssign WHERE Route_guid = '{route_guid}';")
                not_positionresult = cursor.fetchall()

                for i in not_positionresult:
                    not_list.append(i[6])


                for i in list(set(is_list) ^ set(not_list)):
                    process_list.append({
                        "process_number": i,    # 工序号
                        # "process_describe": record[4],  # 工序描述
                        "style_number": package_name   # 款号
                    })



        if process_list:
            for process in process_list:


                # 查询款号
                style_number_objs = http.request.env["ib.detail"].sudo().search([
                    ("style_number", "like", process.get("style_number"))   # 款号
                # ], limit=1, order="date desc")
                ], order="date")
                if style_number_objs:
                    for style_number_obj in style_number_objs:
                        _logger.info(f'查询到款号！{style_number_obj.style_number}')

                        # 查询工序单
                        work_work_objs = http.request.env["work.work"].sudo().search([
                            ("order_number", "=", style_number_obj.id),  # 款号
                            ("employee_id", "=", process.get("process_number")),     # 工序号
                        ])

                        process["process_abbreviation"] = work_work_objs.process_abbreviation   # 系统里面的工序描述
                        if work_work_objs:
                            _logger.info(f'查询到工序单！')
                            break
                        else:
                            _logger.error(f'没查询到工序单！')

                else:
                    _logger.error(f'没查询到款号！')

        # 关闭光标
        cursor.close()
        # 关闭连接对象，否则会导致连接泄漏，消耗数据库资源
        conn.close()

        return json.dumps({'status': "1", 'messages': "成功", 'data': process_list})




    # 设置工序确认记录
    @http.route('/fsn_wechat_extension/set_process_confirm_record/', methods=['POST'], type='json', auth="public", cors="*", csrf=False)
    def set_process_confirm_record(self, *args, **kwargs):

        res = http.request.jsonrequest

        position_number = res.get("position_number", None)    # 站号
        if position_number:
            position_number = str(int(position_number))

        group_name = res.get("group_name", None)    # 组名
        process_list = res.get("process_list", None)    # 工序列表
        work_number = res.get("user", None)     # 工号

        # date = datetime.now().date()  # 日期,
        date = res.get("date", None)    # 日期

        group_obj = http.request.env["check_position_settings"].sudo().search([("group", "=", group_name)])

        create_successful_list = []

        # print(date[0], group_obj.id, position_number)



        for process_info in process_list:
            wechat_process_confirm_objs = http.request.env["wechat_process_confirm"].sudo().search([
                ("date", "=", date),  # 日期,
                ("group_id", "=", group_obj.id),  # 组别id
                ("position", "=", position_number),   # 站号
                ("work_number", "=", work_number),   # 工号
                ("style_number", "=", process_info.get("style_number")),    # 款号
                ("process_number", "=", process_info.get("process_number")),    # 工序号
            ])

            wechat_process_confirm_objs.sudo().unlink()

            wechat_process_confirm_obj = http.request.env["wechat_process_confirm"].sudo().create({
                "date": date,  # 日期
                "work_number": work_number,     # 工号
                "group_id": group_obj.id,   # 组别
                "position": position_number,    # 站号
                "style_number": process_info.get("style_number"),   # 款号
                "process_number": process_info.get("process_number"),     # 工序号
                # "process_describe": process_info.get("process_describe"),   # 工序描述
                "process_describe": process_info.get("process_abbreviation"),   # 工序描述
            })


            automatic_scene_process_objs = http.request.env["automatic_scene_process"].sudo().search([
                ("date", "=", date),  # 日期,
                ("group", "=", group_obj.id),  # 组别id
                ("station_number", "=", position_number),   # 站号
                ("work_number", "=", work_number),   # 工号
                ("style_number", "=", process_info.get("style_number")),    # 款号
                ("process_number", "=", process_info.get("process_number")),    # 工序号
            ])
            automatic_scene_process_objs.sudo().unlink()

            http.request.env["automatic_scene_process"].sudo().create({
                "date": date,  # 日期
                "work_number": work_number,     # 工号
                "group": group_obj.id,  # 组别
                "station_number": position_number,  # 站号
                "style_number": process_info.get("style_number"),   # 款号
                "process_number": process_info.get("process_number"),     # 工序号
            })


            create_successful_list.append(wechat_process_confirm_obj.id)

        if create_successful_list:

            return json.dumps({'status': "1", 'messages': "成功", 'data': create_successful_list})

        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': []})




