# -*- coding: utf-8 -*-
from odoo import http
import json
import requests
from datetime import datetime, timedelta




class SuspensionSystem(http.Controller):
    @http.route('/get_details_data', auth='user', type='json')
    def get_details_data(self, **kw):

        start_time = kw.get("start_time")        # 开始时间
        end_time = kw.get("end_time")        # 结束时间
        dg_host = http.request.env.company.dg_host      # ip
        dg_port = http.request.env.company.dg_port      # 端口号


        check_position_settings_objs = http.request.env["check_position_settings"].sudo().search([])



        for check_position_settings_obj in check_position_settings_objs:
            
            # 从接口获取数据
            url = f"http://{dg_host}:{dg_port}/DgApi/Details?BeginTime={start_time}&EndTime={end_time}&StationID={check_position_settings_obj.position}&WorkLine={check_position_settings_obj.group}"
            res = requests.get(url)
            res.encoding = 'utf-8'
            data_list = json.loads(res.text)["Data"]


            for data_record in data_list:

                # 时间字段格式化
                BeginTime = data_record.get("BeginTime", None).replace("T", " ")
                EndTime = data_record.get("EndTime", None).replace("T", " ")
                
                BeginTime = datetime.strptime(BeginTime[0: 19], "%Y-%m-%d %H:%M:%S")
                EndTime = datetime.strptime(EndTime[0: 19], "%Y-%m-%d %H:%M:%S")

                After_BeginTime = BeginTime - timedelta(hours=8)
                After_EndTime = EndTime  - timedelta(hours=8)


                # 查询汇总表是否已经存在数据
                suspension_system_summary_objs = http.request.env["suspension_system_summary"].sudo().search([
                    ("dDate", "=", data_record.get("dDate", None)),
                    ("date_host", "=", EndTime.hour),
                    ("group", "=", data_record.get("WorkLine", None))
                ])

                # 如果不存在则创建
                if suspension_system_summary_objs:
                    pass
                else:
                    suspension_system_summary_objs = http.request.env["suspension_system_summary"].sudo().create({
                        "dDate": data_record.get("dDate", None),
                        "date_host": EndTime.hour,
                        "group": data_record.get("WorkLine", None),
                    })


                # 明细数据表查重
                suspension_system_details_ids = http.request.env["suspension_system_details"].sudo().search([
                    ("Nid", "=", data_record.get("Nid", None)),
                ])

                # 如果没有重复记录则创建
                if suspension_system_details_ids:
                    pass
                else:

                    http.request.env["suspension_system_details"].sudo().create({

                        "suspension_system_summary_id": suspension_system_summary_objs.id,

                        "Nid": data_record.get("Nid", None),
                        
                        "dDate": data_record.get("dDate", None),
                        "BeginTime": After_BeginTime,
                        "EndTime":After_EndTime,
                        "TimeCount": data_record.get("TimeCount", None),
                        "StandFlag": data_record.get("StandFlag", None),
                        "MONo": data_record.get("MONo", None),
                        "ColorNo": data_record.get("ColorNo", None),
                        "SizeName": data_record.get("SizeName", None),
                        "SeqNo": data_record.get("SeqNo", None),
                        "SeqCode": data_record.get("SeqCode", None),

                        "SAM": data_record.get("SAM", None),
                        "Price": data_record.get("Price", None),
                        "StationID": data_record.get("StationID", None),
                        "EmpID": data_record.get("EmpID", None),
                        "WorkLine": data_record.get("WorkLine", None),
                        "ShtCode": data_record.get("ShtCode", None),
                        "ShtType": data_record.get("ShtType", None),
                        "IsOT": data_record.get("IsOT", None),
                        "RackCard": data_record.get("RackCard", None),
                        "WorkShop": data_record.get("WorkShop", None),

                        "SeqVersion": data_record.get("SeqVersion", None),
                        "InsOrder": data_record.get("InsOrder", None),
                        "IsMerge": data_record.get("IsMerge", None),
                        "Qty": data_record.get("Qty", None),
                        "IsCalced": data_record.get("IsCalced", None),
                        "IsFirstSeq": data_record.get("IsFirstSeq", None),
                        "COLORNAME": data_record.get("COLORNAME", None),
                        # "BarCode": data_record.get("BarCode", None),
                        # "CardNo": data_record.get("CardNo", None),
                        # "BedNo": data_record.get("BedNo", None),

                        # "GroupNo": data_record.get("GroupNo", None),
                    })


        return json.dumps({'dg_host': dg_host, dg_port: dg_port})

#     @http.route('/suspension_system/suspension_system/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('suspension_system.listing', {
#             'root': '/suspension_system/suspension_system',
#             'objects': http.request.env['suspension_system.suspension_system'].search([]),
#         })

#     @http.route('/suspension_system/suspension_system/objects/<model("suspension_system.suspension_system"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('suspension_system.object', {
#             'object': obj
#         })
