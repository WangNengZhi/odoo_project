# -*- coding: utf-8 -*-
from odoo import http
import pymssql
import json
import traceback
import datetime


class HrPay(http.Controller):

    @http.route('/sync_attendance_record', auth='public', type='json')
    def sync_attendance_record(self):


        sql_server_host = http.request.env.company.sql_server_host
        sql_server_user = http.request.env.company.sql_server_user
        sql_server_password = http.request.env.company.sql_server_password
        sql_server_database = http.request.env.company.sql_server_database

        conn = pymssql.connect(host=sql_server_host, user=sql_server_user, password=sql_server_password, database=sql_server_database, charset="utf8")
        cur = conn.cursor()
        if not cur:
            raise (NameError, "数据库连接失败")

        employee_objs = http.request.env["hr.employee"].sudo().search([])

        for employee_obj in employee_objs:

            # 获取更新打卡机记录的时间范围
            punch_in_record_obj = http.request.env["punch.in.record"].sudo().search([
                ("employee", "=", employee_obj.id)
            ], limit=1, order='date desc')
            if punch_in_record_obj:
                start_time = str(punch_in_record_obj.date)
            else:
                start_time = str(employee_obj.entry_time)
            punch_in_record_obj.sudo().unlink()
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)


            sql = "SELECT * from punching_card_record where name = '{}' and record_date >= '{}' and record_date <= '{}'".format(employee_obj.name, start_time, yesterday.date())
            cur.execute(sql)

            resList = cur.fetchall() #fetchall()是接收全部的返回结果行


            if resList:

                tem_dict = {}

                for res in resList:
                    res = list(res)

                    if res[6] not in tem_dict:
                        tem_dict[res[6]] = []

                    res[7] = res[7].replace("T", " ")
                    tem_dict[res[6]].append(res)



                for key in tem_dict:

                    # 排序
                    if len(tem_dict[key]) > 1:
                        tem_dict[key].sort(key=lambda x: x[7], reverse=False)


                        if tem_dict[key][-1][5][0:-3] > '14:00' and tem_dict[key][0][5][0:-3] <= '14:00':
                            http.request.env["punch.in.record"].sudo().create({
                                "date": tem_dict[key][0][6],
                                "employee": employee_obj.id,
                                "check_sign": tem_dict[key][0][5][0:-3] + " " + tem_dict[key][-1][5][0:-3]
                            })
                        elif tem_dict[key][-1][5][0:-3] < '14:00':
                            http.request.env["punch.in.record"].sudo().create({
                                "date": tem_dict[key][0][6],
                                "employee": employee_obj.id,
                                "check_sign": tem_dict[key][0][5][0:-3] + " --:--"
                            })
                        elif tem_dict[key][0][5][0:-3] >= '14:00':
                            http.request.env["punch.in.record"].sudo().create({
                                "date": tem_dict[key][0][6],
                                "employee": employee_obj.id,
                                "check_sign": "--:-- " + tem_dict[key][-1][5][0:-3]
                            })
                    else:
                        if tem_dict[key][0][5][0:-3] <= '14:00':
                            http.request.env["punch.in.record"].sudo().create({
                                "date": tem_dict[key][0][6],
                                "employee": employee_obj.id,
                                "check_sign": tem_dict[key][0][5][0:-3] + " --:--"
                            })
                        elif tem_dict[key][0][5][0:-3] > '14:00':
                            http.request.env["punch.in.record"].sudo().create({
                                "date": tem_dict[key][0][6],
                                "employee": employee_obj.id,
                                "check_sign": "--:-- " + tem_dict[key][0][5][0:-3]
                            })

        conn.close()
        


        return json.dumps({'status': "1",'messages': "成功！"})



    @http.route('/update_punch_record_stats', auth='user', type='json')
    def update_punch_record_stats(self, **kw):
        # print('*'*80, 'update_punch_record_stats')
        try:
            http.request.env["punch_record_with_missing_time"].update_punch_record_stats()
        except:
            traceback.print_exc()
            res = dict(status=1, messages="失败！")
        else:
            res = dict(status=0, messages="成功！")
        return json.dumps(res)
