from datetime import datetime
import calendar
from odoo import models, fields, api


class HardWorkingWorkersOfYear(models.Model):
    _name = 'hard_working_workers_of_year'

    _description = '全年奖'
    _order = 'year desc'

    employee = fields.Many2one('hr.employee', string='员工', readonly=True)

    year = fields.Integer(string='年度', readonly=True)
    month = fields.Integer(string='起始月份', readonly=True)

    end_year = fields.Integer(string='年', readonly=True)
    end_month = fields.Integer(string='结束月份', readonly=True)

    year_month = fields.Char('起始月份', compute="generate_year_month", store=False)
    end_year_month = fields.Char('结束月份', compute="generate_end_year_month", store=False)

    total_days_of_absence = fields.Float(string='总请假天数')
    max_days_of_absence_in_a_month = fields.Float(string='月请假最多天数')

    bonus = fields.Float(string="奖金")

    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")


    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"

        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'hard_working_workers_of_year',
            'view_id': self.env.ref('punish.hard_working_workers_of_year_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.state = "待审批"

        elif button_type == "through":
            self.state = "已审批"





    @api.depends('year', 'month')
    def generate_year_month(self):
        for rec in self:
            rec.year_month = f'{rec.year}-{rec.month:02d}'

    @api.depends('end_year', 'end_month')
    def generate_end_year_month(self):
        for rec in self:
            rec.end_year_month = f'{rec.end_year}-{rec.end_month:02d}'


    # self.stats((2021,8), (2022,7), 15, 2)
    def stats(self, start_month, end_month, absence_on_leave_total_limit, absence_on_leave_monthly_limit):
        ''' '''
        # print('*'*40, 'HardWorkingWorkersOfYear  stats')

        assert start_month <= end_month
        start_year, start_month = start_month
        end_year, end_month = end_month
        if start_year == end_year:
            months = end_month - start_month + 1
        else:  # start_year < end_year
            months = 12*(end_year-start_year-1) + (12-start_month+1) + end_month

        start_date = datetime(start_year, start_month, 1)
        _, last_day = calendar.monthrange(end_year, end_month)
        end_date = datetime(end_year, end_month, last_day)


        # entry_time <= 1st day of start_month & (NOT is_delete or is_delete_date > last day of end_month)
        emps = self.env['hr.employee'].sudo().search([
                    ('entry_time', '<=', start_date),
                    ('id', '!=', 539),  # 许总
                    '|',
                        ('is_delete', '=', False),
                        ('is_delete_date', '>', end_date),
                ])
        leaves = self.env['every.detail'].sudo().search([
                    # '|',
                        # ('end_date', '>=', start_date),

                        ('date', '<=', end_date),
                        ('date', '>=', start_date)
                ])

        # print(len(leaves))

        def get_index(start_year, start_month, year, month):
            if year == start_year:
                return month - start_month
            else:
                return 12*(year-start_year-1) + (12-start_month+1) + month - 1

        def get_hours_a_day(time_plan):
            if time_plan.startswith('8:00 - 21:00'):  # 工人
                return 11.5
            elif time_plan.startswith('9:00 - 18:00'):  # 文职
                return 8
            else:  # time_plan.startswith('8:00 - 18:00')  # 统计
                return 9

        emp_dict = {e.id: e.time_plan for e in emps}
        stats = {emp_id: [0]* months for emp_id in emp_dict}  # !

        # print(emp_dict, stats, leaves)
        for x in leaves:
            emp_id = x.leave_officer.id  # !
            # print('\t\t', x.leave_officer, emp_id)
            if emp_id not in emp_dict:
                continue

            date = x.date.date()

            i = get_index(start_year, start_month, date.year, date.month)

            stats[emp_id][i] += x.days  # hours, NOT days
            # assert len(stats[emp_id]) == months == 12

        res = []
        for emp_id, months in stats.items():

            tem_var = False

            time_plan = emp_dict[emp_id]
            hours_a_day = get_hours_a_day(time_plan)
            total = sum(months)
            if total < absence_on_leave_total_limit*hours_a_day and all(h<absence_on_leave_monthly_limit*hours_a_day for h in months):


                # ------------------------------------
                objs = self.sudo().search([("employee", "=", emp_id)])

                if objs:

                    for obj in objs:
                        if start_date.year > obj.end_year and start_date.month > obj.end_month:
                            tem_var = True

                    if tem_var:
                        res.append(emp_id)

                        self.sudo().create(dict(
                                employee = emp_id,
                                year = start_date.year,
                                month = start_date.month,
                                end_year = end_date.year,
                                end_month = end_date.month,
                                total_days_of_absence = total / hours_a_day,
                                max_days_of_absence_in_a_month = max(months) / hours_a_day
                        ))

                else:

                    res.append(emp_id)

                    self.sudo().create(dict(
                            employee = emp_id,
                            year = start_date.year,
                            month = start_date.month,
                            end_year = end_date.year,
                            end_month = end_date.month,
                            total_days_of_absence = total / hours_a_day,
                            max_days_of_absence_in_a_month = max(months) / hours_a_day
                    ))

                # ------------------------------------


        retval = self.env['hr.employee'].sudo().browse(res)
        return retval

