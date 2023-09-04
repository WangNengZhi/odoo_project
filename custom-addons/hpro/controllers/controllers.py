# -*- coding: utf-8 -*-
from odoo import http
from . import mssaql_class
import json
import datetime


class Hpro(http.Controller):
    # 获取工序数据
    @http.route('/planning_sheet', auth='user', type='json')
    def planning_sheet(self, **kw):

        sql_server_host = http.request.env.company.sql_server_host
        sql_server_user = http.request.env.company.sql_server_user
        sql_server_password = http.request.env.company.sql_server_password
        sql_server_database = http.request.env.company.sql_server_database

        fsn_sqlserver = mssaql_class.MSSQL(host=sql_server_host, user=sql_server_user, pwd=sql_server_password,
                                           db=sql_server_database)

        ib_detail_objs = http.request.env["ib.detail"].sudo().search([])

        for ib_detail_obj in ib_detail_objs:

            # 款号字符串分割
            tem_list = ib_detail_obj.style_number.split("-")
            if len(tem_list) <= 2:
                tem_list = tem_list[0]
            else:
                tem_list = "-".join(tem_list[0:-1])
            # 查询中间表
            sql = f"select * from planning_sheet where wbkh = '{tem_list}'"
            reslist = fsn_sqlserver.ExecQuery(sql)

            # 循环查询内容
            for res in reslist:

                work_work_objs = http.request.env["work.work"].sudo().search([
                    ("order_number", "=", ib_detail_obj.id),
                    ("employee_id", "=", res[5])
                ])

                if work_work_objs:
                    pass

                else:

                    http.request.env["work.work"].sudo().create({
                        "date": datetime.date.today(),   # 日期
                        "order_number": ib_detail_obj.id,  # 款号
                        "employee_id": res[5],  # 工序序号bjmc
                        "part_name": res[4],  # 部件名称gxxh
                        "process_abbreviation": res[7],  # 工序名称gxmc
                        "mechanical_type": res[8],  # 机器名称jqmc_C
                        "process_level": res[12],  # 工序等级
                        "standard_price": res[16],  # 单价
                        "standard_time": res[17],  # 小时指标，标准实际
                    })

        return json.dumps({'status': "1", 'messages': "成功！"})

    # 同步gst数据到中间数据库
    @http.route('/sync_gst_data', auth='user', type='json')
    def sync_gst_data(self, **kw):

        ib_detail_objs = http.request.env["ib.detail"].sudo().search([])
        for ib_detail_obj in ib_detail_objs:
            ib_detail_obj.sync_sqlserver()


        return json.dumps({'status': "1", 'messages': "成功！"})
