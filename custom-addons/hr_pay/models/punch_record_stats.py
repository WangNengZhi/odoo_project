from datetime import datetime, timedelta
import collections
from odoo import models, fields, api


def missing_a_punch_record(emp_id, working_time, entry_date, leave_stats, date, check_sign):
    # 暂不考虑单双休

    # 上下班时间: 8:00 - 21:00/9:00 - 18:00, 单休/双休
    begin_time, end_time = working_time.split(', ')[0].split(' - ')

    delta = timedelta(hours=-8)
    h, m = map(int, begin_time.split(':'))
    begin_work = datetime(date.year, date.month, date.day, h, m) + delta
    h, m = map(int, end_time.split(':'))
    end_work = datetime(date.year, date.month, date.day, h, m) + delta

    leaves = leave_stats.get(emp_id, [])
    for leave in leaves:
        begin_leave, end_leave = leave.date, leave.end_date
        if begin_work>=end_leave or end_work<=begin_leave:
            continue

        # print('!'*80, begin_leave, end_leave, begin_work, end_work)
        if begin_leave<=begin_work and end_work<=end_leave:
            # print('!'*80, emp_id, date)
            return False

        if begin_work<begin_leave and end_leave<end_work:  #
            pass
        elif begin_work <= begin_leave:
            end_work = begin_leave
        else:
            begin_work = end_leave
        break

    # 这天此人应该打卡的时间：最早的打卡 <= begin_work; 最后的打卡 >= end_work
    first_punch, last_punch = check_sign.split()
    return not (first_punch == '--:--' and date == entry_date)  # 入职当天？


class PunchRecordWithMissingTime(models.Model):
    _name = 'punch_record_with_missing_time'
    _description = '员工缺打卡统计'
    _order = 'year desc, month desc'

    year = fields.Integer(string='年')
    month = fields.Integer(string='月')
    employee = fields.Many2one('hr.employee', string='员工')
    missing_times = fields.Integer(string='缺卡次数')
    is_it_a_temporary_worker = fields.Char(string='工种')

    year_month = fields.Char('月份', compute="generate_year_month", store=False)

    @api.depends('year', 'month')
    def generate_year_month(self):
        for rec in self:
            rec.year_month = f'{rec.year}-{rec.month:02d}'


    def update_punch_record_stats(self):
        old_data = self.sudo().search([])
        old_dict = {(x.year, x.month, x.employee.id): x.missing_times for x in old_data}

        leaves = self.env['every.detail'].sudo().search([])  # 请假表
        leave_stats = {}
        for x in leaves:
            emp_id = x.leave_officer.id
            if emp_id not in leave_stats:
                leave_stats[emp_id] = []
            leave_stats[emp_id].append(x)

        punch_stats = {}  # month -> Counter()
        punch_records = self.env['punch.in.record'].sudo().search([('check_sign','like','--:--')])  # 打卡机记录
        emp_id2job = {}
        for x in punch_records:
            emp_id = x.employee.id
            working_time = x.employee.time_plan
            entry_date = x.employee.entry_time
            if missing_a_punch_record(x.employee.id, working_time, entry_date, leave_stats, x.date, x.check_sign):
                year_month = (x.date.year, x.date.month)
                if year_month not in punch_stats:
                    punch_stats[year_month] = collections.Counter()
                punch_stats[year_month][emp_id] += 1

            emp_id2job[emp_id] = x.employee.is_it_a_temporary_worker

        new_set = set()
        for (year, month), cnter in punch_stats.items():
            for emp_id, n in cnter.items():
                key = (year, month, emp_id)
                new_set.add(key)
                if key in old_dict:
                    if n != old_dict[key]:
                        # print('!'*20, 'UPDATE!')
                        self.sudo().search([
                                ('year', '=', year),
                                ('month', '=', month),
                                ('employee', '=', emp_id),
                            ]).write(dict( missing_times = n))
                else:
                    # print('!'*20, 'CREATE!')
                    self.sudo().create(dict(year = year,
                                            month = month,
                                            employee = emp_id,
                                            missing_times = n,
                                            is_it_a_temporary_worker = emp_id2job.get(emp_id,'')))

        for year, month, emp_id in set(old_dict) - new_set:  # ！
            # print('!'*20, 'DELETE!')
            self.sudo().search([
                    ('year', '=', year),
                    ('month', '=', month),
                    ('employee', '=', emp_id),
                ]).unlink()

