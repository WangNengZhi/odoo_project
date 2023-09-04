# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class property(models.Model):
    _name = 'custom.calendar'
    _description = '自定义日历'
    _order = "date desc"
    _rec_name = 'date'


    def _set_line_ids(self):


        lines = []
        hr_department_ids = self.env["hr.department"].sudo().search([])
        for hr_department_id in hr_department_ids:

            line = {
                "department": hr_department_id.id,      # 组别
            }
            lines.append((0, 0, line))


        return lines



        # 根据sequence排序明细表中的内容
        # sort_lines = sorted(lines, key=lambda x: x[2]["sequence"], reverse=False)

        return lines

    date = fields.Date(string='日期', required=True)
    # status = fields.Selection([
    #     ("休息", "休息"),
    #     ("仅双休休息", "仅双休休息"),
    #     ("大小休休息", "大小休休息"),
    #     ],
    #     string="状态")

    reason = fields.Char(string="原因", required=True)
    # is_statutory_holiday = fields.Boolean(string="是否法定节假日")
    week_char = fields.Char(string="周", compute="_set_week_char", store=True)

    custom_calendar_line_ids = fields.One2many("custom_calendar_line", "custom_calendar_id", string="日历明细", default=_set_line_ids)

    extra_work_type = fields.Selection([
        ("法定节假日", "法定节假日"),
        ("非法定节假日", "非法定节假日"),
    ], string="加班类型")



    @api.constrains('date')
    def _check_date(self):
        
        demo = self.env[self._name].sudo().search([('date', '=', self.date)])
        if len(demo) > 1:
            raise ValidationError(f"{self.date}的记录已经存在了！不可重复创建。")



    # 设置员工信息
    @api.depends('date')
    def _set_week_char(self):
        for record in self:
            if record.date:
            
                record.week_char = record.date.weekday() + 1



class CustomCalendarLine(models.Model):
    _name = 'custom_calendar_line'
    _description = '自定义日历明细'


    custom_calendar_id = fields.Many2one("custom.calendar", string="日历")
    department = fields.Many2one("hr.department", string="部门", required=True)
    state = fields.Selection([
        ("仅双休休息", "仅双休休息"),
        ("大小休休息", "大小休休息"),
        ("休息", "休息"),
        ("上班", "上班")
        ], string="状态", required=True, default="休息")
    up_time = fields.Datetime(string="上班时间")
    down_time = fields.Datetime(string="下班时间")


    @api.constrains('up_time', 'down_time')
    def _check_up_time_and_down_time(self):

        for record in self:

            if record.up_time and not record.down_time:

                raise ValidationError(f"{record.department.name}的出勤时间必须全部填写！")
            
            elif record.down_time and not record.up_time:

                raise ValidationError(f"{record.department.name}的出勤时间必须全部填写！")









