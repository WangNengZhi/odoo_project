from odoo import models, fields, api
import collections
from datetime import datetime, timedelta
from utils import weixin_utils


class HrEmployeeDynamics(models.Model):
    _name = 'hr.employee.dynamics'
    _description = '每日在职员工'

    date = fields.Date(string='日期')
    employee = fields.Many2one('hr.employee', string="当日在职员工")

    def get_employees_working(self, date):
        ''' 获取指定日在职的员工的列表 '''
        return list(self.env["hr.employee"].sudo().search([
                '&', ('entry_time', '<=', date),
                     '|', ('is_delete', '=', False),
                          ('is_delete_date', '>', date),
            ]))

    def get_employee_changes(self):
        ''' 获取今日的职员变动信息 '''
        today = datetime.now().date()
        yesterday= today + timedelta(days=-1)
        a_month_ago = today + timedelta(days=-31)

        current = self.env['hr.employee'].get_employees_current()  # 获取在职员工
        emp_id2job = {}

        self.sudo().search([('date','=',today)]).unlink()  # !
        for e in current:
            emp_id2job[e.id] = e.job_title
            self.sudo().create(dict(date=today, employee=e.id))  # !

        self.sudo().search([('date','<',a_month_ago)]).unlink()  # !

        yesterday_employees = [e.employee for e in self.sudo().search([('date','=',yesterday)])] or \
                              self.get_employees_working(yesterday)

        yesterday_set = set(e.id for e in yesterday_employees)
        current_set = set(e.id for e in current)

        left_set = yesterday_set - current_set
        enrolled_set = current_set - yesterday_set

        def format(employees, emp_id2job):
            if not employees:
                return ''
            cnt = collections.Counter(emp_id2job[id] for id in employees)
            s = '、'.join(f'{n}个{job}' for job, n in cnt.items())
            return f'（{s}）'

        s = format(enrolled_set, emp_id2job)
        return f'{today.year}年{today.month}月{today.day}日入职{len(enrolled_set)}人{s}，离职{len(left_set)}人，在职人数{len(current_set)}。'


    def send_change_of_employees_to_enterprise_weixin(self, chatid):
        ''' 发送今日的职员变动信息和公司各部门岗位人数到企业微信 '''
        content = self.get_employee_changes()
        content += '\n\n' + self.env['hr.employee'].generate_stats_of_posts()

        # weixin_utils.send_text_to_enterprise_weixin(content, to_party=weixin_utils.HEAD_DEPT)
        # weixin_utils.send_text_to_enterprise_weixin(content, to_party=weixin_utils.DEV_DEPT)

        # weixin_utils.send_app_group_info_text_weixin(content, chatid=weixin_utils.FAN_HQ)     # 发送消息到总部群
        # weixin_utils.send_app_group_info_text_weixin(content, chatid=weixin_utils.DEVELOPMENT_AND_TEST)     # 开发测试群

        weixin_utils.send_app_group_info_text_weixin(content, chatid=chatid)

