from datetime import datetime, timedelta

from odoo import api, fields, models


class PersonnelManage(models.Model):
    _name = 'personnel_manage'
    _description = '人事管理'

    month = fields.Char(string="月份")
    name = fields.Many2one('hr.employee', string='姓名')
    joined_date = fields.Date(string='入职日期')
    termination_date = fields.Date(string='离职日期')
    emp = fields.Many2one('hr.department', string='部门')
    planned_recruitment = fields.Integer(string='计划招聘人数')
    full_moon = fields.Integer(string='实际满30天人数')
    number_of_interviewees = fields.Integer(string='面试人数')
    number_of_employees = fields.Integer(string='入职人数')
    on_boarding_rate = fields.Float(string='入职率', digits=(10, 2), compute="set_on_boarding_rate", store=True)

    @api.depends('number_of_interviewees', 'number_of_employees')
    def set_on_boarding_rate(self):
        """计算入职率"""
        for record in self:
            if record.number_of_interviewees:
                record.on_boarding_rate = (record.number_of_employees / record.number_of_interviewees) * 100
            else:
                record.on_boarding_rate = 0

    def get_personnel_matters(self):
        """获取人事数据"""
        
        # 获取当前年份和月份
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        # 构建年初的起始日期
        start_date = datetime(year, 1, 1)
        # 构建当前日期作为截止日期

        persons_ret = []

        for i in range(month, 0, -1):
            # 获取查询月份的起始日期
            start_date_month = datetime(year, i, 1)
            # 获取查询月份的结束日期
            end_date_month = start_date_month.replace(day=1, month=start_date_month.month + 1) - timedelta(days=1)
            start_date_str = start_date_month.strftime('%Y-%m-%d')
            end_date_str = end_date_month.strftime('%Y-%m-%d')
            # 查询人事招聘专员
            persons = self.env['hr.employee'].search([
                ('job_id.name', '=', '人事招聘专员'),
                ('is_delete', '=', False),
            ])

            for person in persons:
                # 查询招聘专员面试人数
                ret = self.env['appointment.recritment'].search([
                    ('recruiter', '=', person.name),
                    ('date', '>=', start_date_str),  # 正式的时候改为start_date
                    ('date', '<=', end_date_str)  # 正式的时候改为end_date
                ])
                interviewee_count = len(ret)

                # 查询入职人数
                number = self.env['hr.employee'].search([('introducer', '=', person.id),
                                                         ('entry_time', '>=', start_date_str),
                                                         ('entry_time', '<=', end_date_str)
                                                         ]) # 正式的时候改为start_date
                employee_count = len(number)


                # 查询入职满30天人数（当月）
                number_of_working_days = self.env['personnel_award'].search([('introducer', '=', person.id),
                                                              ('working_time', '>=', 30),
                                                              ('satisfy_date', '>=', start_date_str),
                                                              ('satisfy_date', '<=', end_date_str),
                                                              ]) # 正式的时候改成start_date和end_date
                full_moon_count = len(number_of_working_days)
                # TODO:如果需要显示出人事招聘专员的离职就注释掉人事招聘查询中的('is_delete', '=', False),然后打开termination_date

                persons_data = {
                    'month': f'{year}-{i}',
                    'name': person.id,
                    'joined_date': person.entry_time,
                    # 'termination_date':person.is_delete_date if person.is_delete else None,
                    'emp': person.department_id.id,
                    'number_of_interviewees': interviewee_count,
                    'number_of_employees': employee_count,
                    'full_moon': full_moon_count
                }
                persons_ret.append(persons_data)
        return persons_ret

    def refresh_personnel(self):
        """更新人事管理"""
        ret = self.get_personnel_matters()
        # 检查记录是否存在
        existing_records = self.env['personnel_manage'].search([])
        if existing_records:
            return

        self.env['personnel_manage'].create(ret)

