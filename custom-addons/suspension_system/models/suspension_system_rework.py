from odoo import api, fields, models
from datetime import timedelta

import requests
import json

import itertools

class SuspensionSystemRework(models.Model):
    _name = 'suspension_system_rework'
    _description = '吊挂返修信息'
    # _rec_name = 'group'
    # _order = "dDate desc"


    date = fields.Date(string="日期")
    group = fields.Many2one('check_position_settings', string='组别')
    employee_id = fields.Many2one('hr.employee', string='中查')
    station_number = fields.Integer(string="站号")
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号（对象）')
    order_number_show = fields.Char(string="订单号")
    style_number = fields.Many2one('ib.detail', string='款号（对象）')
    style_number_show = fields.Char(string="款号")
    product_size = fields.Many2one("fsn_size", string="尺码（对象）")
    product_size_show = fields.Char(string="尺码")

    number = fields.Integer(string='件数')
    few_number = fields.Integer(string="次数")
    qc_employee_id = fields.Many2one('hr.employee', string='质检员')
    qc_type = fields.Selection([('总检','总检'), ('尾查','尾查')], string='质检类型')





    def set_suspension_system_rework_data(self, today=None):

        if not today:
            today = fields.datetime.now()
        
        # 开始日期:今天日期
        start_date = today.date()
        # 结束日期:明天日期
        end_date = start_date + timedelta(days=1)
        # 尾查站位列表
        check_position_settings_obj = self.env['check_position_settings'].search([("group", "=", "后整")])
        tail_station_number_list = check_position_settings_obj.position_line_ids.filtered(lambda x: x.type == "尾查").mapped('position')

        dg_os_url = self.env.ref("fsn_setting.dg_os_url").value
        dg_os_port = self.env.ref("fsn_setting.dg_os_port").value
        url = f"http://{dg_os_url}:{dg_os_port}/DgApi/rework"

        query = {"BeginTime": start_date, "EndTime": end_date}

        response = requests.request("GET", url, params=query)

        response.encoding = 'utf8'

        data_list = json.loads(response.text)["Data"]


        data_list = [i for i in data_list if "WorkLine" in i]

        for i in data_list:

            if i['RackQCFail'] == 0:
                check_position_settings_objs = self.env['check_position_settings'].search([("repair_group.group", "=", i['WorkLine'])])
                for check_position_settings_obj in check_position_settings_objs:
                    if i['StationID'] in check_position_settings_obj.repair_group_position_lines_id.mapped("position"):
                        i['StationID'] = check_position_settings_obj.repair_fulcrum
                        
            if len(i["MONo"]) > 7:
                i["MONo"] = i["MONo"][0:7]



        # 组别 订单号 款号 站号 员工 尺码 质检员
        data_list.sort(key=lambda x: (x["StationID"], x["MONo"], x["ColorNo"], x["SizeName"], x["EmpID"], x["EmpIDQC"], x['StationIDQC']), reverse=False)

        for (StationID, MONo, ColorNo, SizeName, EmpID, EmpIDQC, StationIDQC), record_objs in itertools.groupby(data_list, key=lambda x: (x["StationID"], x["MONo"], x["ColorNo"], x["SizeName"], x["EmpID"], x["EmpIDQC"], x['StationIDQC'])):     # 再按站号, 员工, 款号分组

            qc_type = "尾查" if StationIDQC in tail_station_number_list else "总检"
            record_objs_list = list(record_objs)

            employee_id = self.env['hr.employee'].search([("barcode", "=", EmpID)]).id
            qc_employee_id = self.env['hr.employee'].search([("barcode", "=", EmpIDQC)]).id
            group_obj = self.env['check_position_settings'].search([("repair_fulcrum", "=", StationID)])
            if group_obj:

                number = len(set([i['RackCard'] for i in record_objs_list]))
                few_number = len(record_objs_list)

                obj = self.search([
                    ("date", "=", today),
                    ("group", "=", group_obj.id),
                    ("employee_id", "=", employee_id),
                    ("order_number_show", "=", MONo),
                    ("style_number_show", "=", ColorNo),
                    ("product_size_show", "=", SizeName),
                    ("qc_employee_id", "=", qc_employee_id),
                    ("qc_type", "=", qc_type)
                ])
                if obj:
                    obj.number = number
                    obj.few_number = few_number
                else:

                    self.create({
                        "date": today,
                        "group": group_obj.id,
                        "employee_id": self.env['hr.employee'].search([("barcode", "=", EmpID)]).id,
                        "order_number": self.env['sale_pro.sale_pro'].search([("order_number", "=", MONo)]).id,
                        "order_number_show": MONo,
                        "style_number": self.env['ib.detail'].search([("style_number", "=", ColorNo)]).id,
                        "style_number_show": ColorNo,
                        "product_size": self.env['fsn_size'].search([("name", "=", SizeName)]).id,
                        "product_size_show": SizeName,
                        "number": number,
                        "few_number": few_number,
                        "qc_employee_id": self.env['hr.employee'].search([("barcode", "=", EmpIDQC)]).id,
                        "qc_type": qc_type
                    })
            
            else:


                group_obj = self.env['check_position_settings'].search([("group", "=", "后整")])

                number = len(set([i['RackCard'] for i in record_objs_list]))
                few_number = len(record_objs_list)

                obj = self.search([
                    ("date", "=", today),
                    ("group", "=", group_obj.id),
                    ("employee_id", "=", employee_id),
                    ("order_number_show", "=", MONo),
                    ("style_number_show", "=", ColorNo),
                    ("product_size_show", "=", SizeName),
                    ("qc_employee_id", "=", qc_employee_id),
                    ("qc_type", "=", qc_type)
                ])
                if obj:
                    obj.number = number
                    obj.few_number = few_number
                else:

                    self.create({
                        "date": today,
                        "group": group_obj.id,
                        "employee_id": self.env['hr.employee'].search([("barcode", "=", EmpID)]).id,
                        "order_number": self.env['sale_pro.sale_pro'].search([("order_number", "=", MONo)]).id,
                        "order_number_show": MONo,
                        "style_number": self.env['ib.detail'].search([("style_number", "=", ColorNo)]).id,
                        "style_number_show": ColorNo,
                        "product_size": self.env['fsn_size'].search([("name", "=", SizeName)]).id,
                        "product_size_show": SizeName,
                        "number": number,
                        "few_number": few_number,
                        "qc_employee_id": self.env['hr.employee'].search([("barcode", "=", EmpIDQC)]).id,
                        "qc_type": qc_type
                    })
