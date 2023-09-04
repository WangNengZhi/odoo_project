from odoo import models, fields, api


class hr_hiring_personnel(models.Model):
    _name = 'hiring.personnel'
    _description = '招聘人员'
    _order = 'date desc'

    date = fields.Date('日期')
    week = fields.Selection(
        [('周一', '周一'),
         ('周二', '周二'),
         ('周三', '周三'),
         ('周四', '周四'),
         ('周五', '周五'),
         ('周六', '周六'),
         ('周日', '周日')],
        string='周')
    recruiter = fields.Char('招聘人员')
