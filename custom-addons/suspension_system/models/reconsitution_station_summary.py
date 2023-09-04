from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import requests
import json
import itertools


class SuspensionSystemStationSummary(models.Model):
    _inherit = "suspension_system_station_summary"


    # 远程调用同步吊挂数据
    def sync_data(self):
        self._sync_data()

        return True


    # 获取衣架信息列表
    def get_rack_info_list(self, dg_host, dg_port, line_number):

        url = f"http://{dg_host}:{dg_port}/DgApi/stations?LineID={line_number}"
        res = requests.get(url)
        res.encoding = 'utf-8'

        return json.loads(res.text)["Data"]

    # 获取站位衣架信息
    def get_station_rack_info(self, rack_info_list, StationID):
        try:
            # 站位衣架数量，站位衣架容量
            rack_cnt, rack_cap = next((i['RackCnt'], i['RackCap']) for i in rack_info_list if i['StationID'] == StationID)
        except:
            rack_cnt, rack_cap = 0, 0

        return rack_cnt, rack_cap

    def _sync_data(self, today=None):

        if not today:
            today = fields.Date.today()

        # 开始日期:今天日期
        start_date = today
        # 结束日期:明天日期
        end_date = start_date + timedelta(days=1)

        dg_host = self.env.company.dg_host      # ip
        dg_port = self.env.company.dg_port      # 端口号


        check_position_settings_objs = self.env["check_position_settings"].sudo().search([])

        for check_position_settings_obj in check_position_settings_objs:
            
            if not check_position_settings_obj.line_number:
                ''' 如果没有填写线号, 则直接跳过'''
                continue

            # 从接口获取数据
            print(start_date, end_date, check_position_settings_obj.group)
            url = f"http://{dg_host}:{dg_port}/DgApi/Details?BeginTime={start_date}&EndTime={end_date}&WorkLine={check_position_settings_obj.group}"
            res = requests.get(url)
            res.encoding = 'utf-8'

            data_list = json.loads(res.text).get("Data")

            if not data_list:
                print(res.text, check_position_settings_obj.group)
                ''' 如果没有数据, 则直接跳过'''
                continue


            # 获取衣架信息列表
            rack_info_list = self.get_rack_info_list(dg_host, dg_port, check_position_settings_obj.line_number)

            # 设置挂片组站号为0
            for data_record in data_list:

                # 奖挂片组的站号设置为0
                if "IsFirstSeq1" in data_record:
                    data_record["StationID"] = 0

                if len(data_record['EmpID']) != 6:
                    data_record['EmpID'] = '%06d' % int(data_record['EmpID'])


            data_list = [i for i in data_list if i['InsOrder'] == 1]    # 去掉返修的

            data_list.sort(key=lambda x: (x["StationID"], x["EmpID"], x["SeqCode"], x["ColorNo"]), reverse=False)     # 订单号, 站号, 员工, 款号排序

            for (StationID, EmpID, SeqCode, ColorNo), SeqNo_objs in itertools.groupby(data_list, key=lambda x:(x["StationID"], x["EmpID"], x["SeqCode"], x["ColorNo"])):     # 再按站号, 员工, 款号分组

                SeqNo_objs_list = list(SeqNo_objs)   # 转换成列表

                # 获取站位衣架信息
                rack_cnt, rack_cap = self.get_station_rack_info(rack_info_list, StationID)

                # 获取员工对象	000002
                EmpID = EmpID.strip()
                staff_obj = self.get_employee_name(EmpID)
                # 获取订单对象
                SeqCode = SeqCode.strip()
                order_obj = self.get_order_number(SeqCode)


                # 查询汇总表是否已经存在数据
                suspension_system_station_summary_obj = self.env["suspension_system_station_summary"].sudo().search([
                    ("dDate", "=", start_date),
                    ("group", "=", check_position_settings_obj.id),
                    ("MONo", "=", ColorNo),
                    ("order_number_show", "=", SeqCode),
                    ("station_number", "=", StationID),
                    ("employee_id", "=", staff_obj.id)
                ])


                if suspension_system_station_summary_obj:

                    suspension_system_station_summary_obj.rack_cnt = rack_cnt
                    suspension_system_station_summary_obj.rack_cap = rack_cap

                else:

                    ib_detail_ids = self.env["ib.detail"].sudo().search([
                        ("style_number", "=", ColorNo.strip())
                    ])

                    # 如果查询到款号信息
                    if ib_detail_ids:
                        suspension_system_station_summary_obj = self.env["suspension_system_station_summary"].sudo().create({
                            "dDate": start_date,
                            "group": check_position_settings_obj.id,
                            "order_number_show": SeqCode,
                            "order_number": order_obj.id,
                            "style_number": ib_detail_ids.id,
                            "station_number": StationID,
                            "MONo": ColorNo,
                            "employee_id": staff_obj.id,
                            "job_id": staff_obj.job_id.id,
                            "rack_cap": rack_cap,
                            "rack_cnt": rack_cnt
                        })
                    else:
                        suspension_system_station_summary_obj = self.env["suspension_system_station_summary"].sudo().create({
                            "dDate": start_date,
                            "group": check_position_settings_obj.id,
                            "order_number_show": SeqCode,
                            # "order_number": order_obj.id,
                            "MONo": ColorNo,
                            # "style_number": ib_detail_ids.id,
                            "station_number": StationID,
                            "employee_id": staff_obj.id,
                            "job_id": staff_obj.job_id.id,
                            "rack_cap": rack_cap,
                            "rack_cnt": rack_cnt
                        })



                SeqNo_objs_list.sort(key=lambda x: x["SeqNo"], reverse=False)

                for SeqNo, SeqNo_objs in itertools.groupby(SeqNo_objs_list, key=lambda x:x["SeqNo"]):

                    SeqNo_list = list(SeqNo_objs)

                    number = len(SeqNo_list)      # 件数

                    SeqNo_list.sort(key=lambda x: x["EndTime"], reverse=False)  # 按时间排序

                    # 第一件时间
                    first_time = SeqNo_list[0]["EndTime"]
                    first_time = first_time.replace("T", " ")[0: 18]
                    first_time = datetime.strptime(first_time, "%Y-%m-%d %H:%M:%S")
                    first_time = first_time - timedelta(hours=8)


                    # 最后一件时间
                    last_time = SeqNo_list[-1]["EndTime"]
                    last_time = last_time.replace("T", " ")[0: 18]
                    last_time = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                    last_time = last_time - timedelta(hours=8)

                    # print(check_position_settings_obj.group, StationID, staff_obj.name, ColorNo, SeqNo, len(list(SeqNo_objs)))

                    SeqNo_line_obj = suspension_system_station_summary_obj.line_lds.sudo().search([
                        ("seqno_id", "=", suspension_system_station_summary_obj.id),
                        ("SeqNo", "=", SeqNo)
                    ])
                    if SeqNo_line_obj:

                        if SeqNo_line_obj.number != number:

                            SeqNo_line_obj.sudo().write({
                                "number": number,
                                "update_number": SeqNo_line_obj.update_number + 1,
                                "is_update": True,
                                "last_time": last_time,
                            })
                        else:
                            SeqNo_line_obj.sudo().write({
                                "update_number": SeqNo_line_obj.update_number + 1,
                                "is_update": False,
                            })
                    else:
                        SeqNo_line_obj.sudo().create({
                            "seqno_id": suspension_system_station_summary_obj.id,
                            "SeqNo": SeqNo,      # 工序号
                            "number": number,     # 数量
                            "update_number": 1,     # 更新次数
                            "is_update": True,      # 是否活跃
                            "first_time": first_time,   # 第一件时间
                            "last_time": last_time,     # 最后一件时间
                        })

                # 计算件数
                end_time_list = []
                for SeqNo_obj in SeqNo_objs_list:
                    end_time_list.append(SeqNo_obj["EndTime"])

                suspension_system_station_summary_obj.total_quantity = len(set(end_time_list))







