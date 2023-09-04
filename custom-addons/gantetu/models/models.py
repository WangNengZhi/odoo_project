# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Gantetu(models.Model):
    _name = 'gantetu_gantetu'
    _description = '甘特图测试模型'

    name = fields.Char(u'任务编号')
    plan_start_time = fields.Date(u'计划开始时间', required=True)
    plan_work_hours = fields.Integer(u'工时(小时)', required=True)
    plan_end_time = fields.Date(u'计划结束时间')
    employee_id = fields.Many2one(
        'hr.employee',
        string=u'人力资源',
    )
    department = fields.Many2one('hr.department', string="部门")
    pre_work_bd_id = fields.Many2one('gantetu_gantetu', string=u'前置任务')
    work_remark = fields.Text(u'任务说明', size=200)


