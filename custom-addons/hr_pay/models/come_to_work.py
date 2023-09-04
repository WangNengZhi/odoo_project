#
import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class come_to_work(models.Model):
    _name = 'come.to.work'
    _description = '上下班时间'
    _order = 'date desc'

    date = fields.Date(string='日期')
    name = fields.Many2one('hr.employee', string='姓名')
    time = fields.Char(string='出勤时间')
    minutes_late = fields.Float(string='迟到总时间')
    total_time_early = fields.Float(string='早退总时间')
    comment = fields.Char('备注')


    @api.model
    def create(self, val):

        demo = self.env['come.to.work'].sudo().search([('date', '=', val['date']), ('name', '=',val['name'])])
        if demo:
            demo.sudo().unlink()
        return super(come_to_work, self).create(val)

    @api.constrains('date', 'name')
    def _check_something(self):
        # for record in self:
        demo = self.env['come.to.work'].sudo().search(
            [('date', '=', self.date), ('name', '=', self.name.id)])
        if len(demo) > 1:
            raise ValidationError("迟到早退记录中同一个人同一天不能有多个记录")


    def come_to(self):
        # 转化成分钟
        def t2s(t):
            h, m, s = str(t).strip().split(":")
            return int(h) * 60 + int(m) + int(s) / 60

        #  得到当前的时间
        now_date = datetime.datetime.now() + datetime.timedelta(hours=8) - datetime.timedelta(days=1)
        #  查询线上考勤的记录
        demo = self.env['punch.in.record'].sudo().search([('date', '=', now_date)])
        for record in demo:
        #    遍历所有的这一天的记录
            # 查询一下对方是什么工作时间
            work_time = self.env['hr.employee'].sudo().search([('id', '=', record.employee.id)]).time_plan
            if work_time:
                time = work_time
                comment = ''
                minutes_late = 0
                total_time_early = 0
                #      实际时间
                actual_time = record.check_sign
                if actual_time:
                    #     早上的时间
                    morning_time = work_time.split('-')[0].strip()
                    #      实际早上的时间
                    morning_actual_time = actual_time.split(' ')[0].strip()
                    if morning_actual_time == '--:--':
                        comment = '早上没有打卡'

                    else:
                        morning_actual_time_date = datetime.datetime.strptime(morning_actual_time, '%H:%M')
                        morning_time_date = datetime.datetime.strptime(morning_time, '%H:%M')
                        if morning_actual_time_date > morning_time_date:
                            date = morning_actual_time_date - morning_time_date
                            minutes_late = t2s(date)
                        else:
                            minutes_late = 0


                    #     晚上的时间
                    evening_time = work_time.split('-')[1].split(',')[0].strip()
                    #      实际晚上的时间
                    evening_actual_time = actual_time.split(' ')[1]
                    if evening_actual_time == '--:--':
                        comment = '晚上没有打卡'
                    else:
                        evening_actual_time_date = datetime.datetime.strptime(evening_actual_time, '%H:%M')
                        evening_time_date = datetime.datetime.strptime(evening_time, '%H:%M')
                        if evening_time_date > evening_actual_time_date:
                            date = evening_time_date - evening_actual_time_date
                            total_time_early = t2s(date)
                        else:
                            total_time_early = 0

                    if morning_actual_time == '--:--' and evening_actual_time == '--:--':
                        comment = '没有打卡'
                    #   创建一个对象
                    #   判断是否存在。然后看看是创建还是删除  todo
                    demo_old = self.env['come.to.work'].sudo().search([('date', '=', now_date), ('name', '=', record.employee.id)])
                    if demo_old:
                        demo_old.sudo().write({
                            'time': time,
                            'minutes_late': minutes_late,
                            'total_time_early': total_time_early,
                            'comment': comment
                        })
                    else:
                        self.env['come.to.work'].sudo().create({
                            'date': now_date,
                            'name': record.employee.id,
                            'time': time,
                            'minutes_late': minutes_late,
                            'total_time_early': total_time_early,
                            'comment': comment
                        })

