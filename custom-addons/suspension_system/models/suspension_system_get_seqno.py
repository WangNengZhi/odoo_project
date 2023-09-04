from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import requests
import json


class SuspensionSystemGetSeqno(models.Model):
    _name = 'suspension_system_get_seqno'
    _description = '吊挂站号实时工序'
    # _rec_name = 'group'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    group = fields.Many2one('check_position_settings', string='组别')
    style_number = fields.Many2one('ib.detail', string='款号')
    MONo = fields.Char(string="款号")
    employee_id = fields.Many2one('hr.employee', string='员工')
    station_number = fields.Integer(string="站号")
    line_lds = fields.One2many("seqno_line", "seqno_id", string="工序号")







    # 获取员工对象
    def get_employee_name(self, EmpID):

        hr_employee_obj = self.env["hr.employee"].sudo().search([
            ("barcode", "=", EmpID)
        ])
        # 返回员工对象
        return hr_employee_obj



    def _sync_data(self):

        # 开始日期:今天日期
        start_time = date.today()
        # 结束日期:明天日期
        end_time = start_time + timedelta(days=1)

        # 执行前先把今天的记录上的件数和产值全部设置为0
        # self.empty_records(start_time)

        dg_host = self.env.company.dg_host      # ip
        dg_port = self.env.company.dg_port      # 端口号

        # 工序号获取时间范围区间
        end_interval_time = datetime.now() + timedelta(hours=8)
        start_interval_time = datetime.now() + timedelta(hours=7)

        check_position_settings_objs = self.env["check_position_settings"].sudo().search([])

        for check_position_settings_obj in check_position_settings_objs:
            # 从接口获取数据
            url = f"http://{dg_host}:{dg_port}/DgApi/Details?BeginTime={start_time}&EndTime={end_time}&WorkLine={check_position_settings_obj.group}"
            res = requests.get(url)
            res.encoding = 'utf-8'
            data_list = json.loads(res.text)["Data"]


            for data_record in data_list:

                # 获取员工对象	000002
                staff_obj = self.get_employee_name(data_record["EmpID"])

                EndTime = data_record["EndTime"].replace("T", " ")[0: 18]
                EndTime = datetime.strptime(EndTime, "%Y-%m-%d %H:%M:%S")

                # 奖挂片组的站号设置为0
                if "IsFirstSeq1" in data_record:
                    data_record["StationID"] = 0

                # 收集一个小时内的工序号
                if start_interval_time < EndTime < end_interval_time:


                    # 先查询是否已经有该日期，该组，该款号，该站号的记录
                    suspension_system_get_seqno_obj = self.env["suspension_system_get_seqno"].sudo().search([
                        ("dDate", "=", data_record["dDate"]),   # 日期
                        ("group", "=", check_position_settings_obj.id),     # 组别
                        ("MONo", "=", data_record["ColorNo"]),      # 款号
                        ("station_number", "=", data_record["StationID"]),      # 站号
                        ("employee_id", "=", staff_obj.id),      # 员工
                    ])

                    if suspension_system_get_seqno_obj:

                        
                        seqno_line_obj = self.env["seqno_line"].sudo().search([
                            ("seqno_id", "=", suspension_system_get_seqno_obj.id),
                            ("SeqNo", "=", data_record["SeqNo"])
                        ])

                        if seqno_line_obj:
                            pass
                        else:

                            suspension_system_get_seqno_obj.line_lds = [(0, 0, {"SeqNo": data_record["SeqNo"]})]

                    else:

                        self.env["suspension_system_get_seqno"].sudo().create({
                            "dDate": data_record["dDate"],   # 日期
                            "group": check_position_settings_obj.id,     # 组别
                            "MONo": data_record["ColorNo"],      # 款号
                            "station_number": data_record["StationID"],      # 站号
                            "employee_id": staff_obj.id,      # 员工
                            "line_lds": [(0, 0, {"SeqNo": data_record["SeqNo"]})],      # 序号明细
                        })



                    







class SeqnoLine(models.Model):
    _name = 'seqno_line'
    _description = '吊挂站号实时工序明细'
    _rec_name = 'SeqNo'

    seqno_id = fields.Many2one("suspension_system_get_seqno")
    SeqNo = fields.Integer(string="工序号")



    @api.constrains('SeqNo', 'seqno_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[record._name].sudo().search([
                ("seqno_id", "=", record.seqno_id.id),
                ("SeqNo", "=", record.SeqNo),
                ])
            if len(demo) > 1:
                raise ValidationError(f"吊挂工序重复！")




