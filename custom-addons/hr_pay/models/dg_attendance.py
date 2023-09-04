from odoo import models, fields, api
import requests
import json
from datetime import timedelta

from utils import weixin_utils


class DgAttendance(models.Model):
    _name = 'dg_attendance'
    _description = '吊挂考勤'
    _order = 'date desc'

    date = fields.Date(string='日期')
    employee_id = fields.Many2one('hr.employee', string='员工')
    department_id = fields.Many2one('hr.department', string='部门', compute="_set_emp_message", store=True)
    job_id = fields.Many2one('hr.job', string='岗位', compute="_set_emp_message", store=True)
    contract = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], string='工种', compute="_set_emp_message", store=True)

    record_moment = fields.Selection([
        ('上午', '上午'),
        ('中午', '中午'),
        ('晚上', '晚上'),
    ], string="记录时刻")

    # 设置员工信息
    @api.depends('employee_id')
    def _set_emp_message(self):
        for record in self:

            # 部门
            record.department_id = record.employee_id.department_id.id
            # 岗位
            record.job_id = record.employee_id.job_id.id
            # 合同/工种
            record.contract = record.employee_id.is_it_a_temporary_worker


    # 生成吊挂考勤记录
    def generate_dg_attendance_record(self, today, record_moment):
        today += timedelta(hours=8)

        dg_os_url = self.env.ref("fsn_setting.dg_os_url").value
        dg_os_port = self.env.ref("fsn_setting.dg_os_port").value
        url = f"http://{dg_os_url}:{dg_os_port}/DgApi/GetStation"

        check_position_settings_list = self.env["check_position_settings"].sudo().search_read([], ['line_guid'])

        for check_position_settings_record in check_position_settings_list:

            querystring = {"Line_Guid": check_position_settings_record['line_guid']}

            response = requests.request("GET", url, params=querystring)

            res_date = json.loads(response.text)

            for station_info in res_date.get('Data'):
                
                if "EmpID" in station_info:

                    emp_obj = self.env['hr.employee'].search([("barcode", "=", station_info['EmpID'])])

                    if emp_obj:

                        if not self.env['dg_attendance'].search([("date", "=", today), ("employee_id", "=", emp_obj.id), ("record_moment", "=", record_moment)]):

                            self.env["dg_attendance"].create({
                                "date": today,
                                "employee_id": emp_obj.id,
                                "record_moment": record_moment
                            })
        

        if record_moment == "上午":
            self.send_fsn_hr_inspect_channel_messages(today, record_moment)

            self.send_to_work_wx_messages(today, record_moment)



    def send_fsn_hr_inspect_channel_messages(self, today, record_moment):
        ''' 发送吊挂考勤信息到人事专用频道'''

        group_name_list = ['缝纫一组', '缝纫二组', '缝纫三组', '缝纫四组', '缝纫五组', '缝纫六组', '缝纫七组', '缝纫八组', '缝纫九组', '缝纫十组']

        message_str = f"{today.date()}，吊挂考勤！<br/>"

        for group_name in group_name_list:

            on_job_num = self.env['hr.employee'].sudo().search_count([("department_id.name", "=", group_name), ("is_delete", "=", False), ("job_id.name", "!=", "流水组长")])
            dg_num = self.env['dg_attendance'].sudo().search_count([("department_id.name", "=", group_name), ("record_moment", "=", record_moment), ("date", "=", today)])
            dg = self.env['dg_attendance'].sudo().search([("department_id.name", "=", group_name), ("record_moment", "=", record_moment), ("date", "=", today)])
            on_job_employee = self.env['hr.employee'].sudo().search([("department_id.name", "=", group_name), ('is_delete', '=', False), ("job_id.name", "!=", "流水组长")])
            on_job_id = on_job_employee.mapped('id')
            dg_job = dg.mapped('employee_id')
            dg_job_id =dg_job.mapped('id')
            no_job_employee = self.env['hr.employee'].sudo().search([("department_id.name", "=", group_name),('id', '!=', dg_job_id),('is_delete', '=', False), ('is_delete', '=', False), ("job_id.name", "!=", "流水组长")])
            no_job_name = ', '.join(str(item) for item in no_job_employee.mapped('name'))
            on_job_employee_name = on_job_employee.mapped('name')
            if on_job_num:
               message_str += f"组别：{group_name}，在职人数：{on_job_num}，吊挂人数：{dg_num}，缺勤员工姓名：{no_job_name}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env['mail.channel'].browse(self.env.ref("fsn_timed_task.fsn_hr_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
    

    def send_to_work_wx_messages(self, today, record_moment):
        ''' 发送吊挂考勤信息到企业微信人事群'''

        group_name_list = ['缝纫一组', '缝纫二组', '缝纫三组', '缝纫四组', '缝纫五组', '缝纫六组', '缝纫七组', '缝纫八组', '缝纫九组', '缝纫十组']

        messages = f"{today.date()}，吊挂考勤！\n"

        for group_name in group_name_list:

            on_job_num = self.env['hr.employee'].sudo().search_count([("department_id.name", "=", group_name), ("is_delete", "=", False), ("job_id.name", "!=", "流水组长")])
            dg_num = self.env['dg_attendance'].sudo().search_count([("department_id.name", "=", group_name), ("record_moment", "=", record_moment), ("date", "=", today)])
            if on_job_num:
                messages += f"组别：{group_name}，在职人数：{on_job_num}，吊挂人数：{dg_num}\n"

        weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.PERSONNEL_DEP)