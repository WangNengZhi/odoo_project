import datetime

from odoo import models, fields, api


class HangingInspection(models.TransientModel):
    """吊挂检查"""
    _inherit = "fsn_daily"

    def obtain_the_previous_day_date(self):
        """获取前一天日期"""
        # 获取当前日期
        today = datetime.date.today()

        # 计算前一天日期
        previous_day = today - datetime.timedelta(days=1)

        # 格式化前一天日期
        previous_day_formatted = previous_day.strftime('%Y-%m-%d')

        return previous_day_formatted

    def obtain_hanging_date(self):
        """获取吊挂数据"""
        # tmp_data = '2023-05-06'
        date = self.obtain_the_previous_day_date()
        ret_data = self.env['suspension_system_station_summary'].search([('dDate', '=', date)])

        employee_ratios = []  # 跟踪员工工件比例总值的字典

        post_list = ['裁床主管', '品控主管', '后道主管', '外发主管', '车间主任', '厂长', '副厂长', '中查', '现场IE', '工时IE',
                     '分析IE', 'IE主管', '组长', '流水组长', '整件组长'] # 岗位列表

        for staff in ret_data:
            if staff.employee_id.job_id.name not in post_list and staff.workpiece_ratio == 0.1 and staff.station_number != 0:
            # if staff.employee_id.is_it_a_temporary_worker == "正式工(计件工资)" and staff.workpiece_ratio == 0:
                employee_name = staff.employee_id.name
                workpiece_ratio = staff.workpiece_ratio
                group = staff.employee_id.department_id.name
                found_employee = next((e for e in employee_ratios if e['name'] == employee_name), None)

                if found_employee is None:
                    employee_ratios.append({'date': date, 'group': group, 'name': employee_name, 'ratio': workpiece_ratio})
                else:
                    found_employee['ratio'] += workpiece_ratio
        return employee_ratios

    def personal_productivity(self):
        """获取个人效率"""
        # tmp_data = '2023-02-06'
        date = self.obtain_the_previous_day_date()
        manual_efficiency = []
        data_ret = self.env['eff.eff'].search([('date', '=', date)])
        manual_efficiency.append({'date': date, 'efficiency': data_ret})
        return manual_efficiency


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_fsn_hanging_daily(self):
        """发送吊挂日报"""
        message_content = {}

        message_content['get_hanging_data'] = self.env['fsn_daily'].obtain_hanging_date()

        message_content['get_personal_productivity'] = self.env['fsn_daily'].personal_productivity()

        message_str = f"{len(message_content['get_hanging_data'])}条吊挂信息异常:<br/>"
        for message in message_content['get_hanging_data']:
            message_str += f"日期：{message['date']}，部门：{message['group']}，员工：{message['name']}，效率：{round(message['ratio'], 2)}<br/>"

        message_str += f"<br/>个人效率检查：<br/>"
        for message in message_content['get_personal_productivity']:
            message_str += f"日期：{message['date']}， 手工效率已录入：{len(message['efficiency'])}条<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
