from odoo import models, fields, api


class PostPerformanceSetting(models.Model):
    _name = 'post_performance_setting'
    _description = 'FSN岗位绩效设置'


    job_id = fields.Many2one('hr.job', string='岗位', required=True)
    frequency_distribution = fields.Integer(string="发放频率（每几个月一次发放一次）")
    starting_month = fields.Char(string="启始月份", required=True)
