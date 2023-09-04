from odoo import models, fields, api


class BackChannelProgressJobSetting(models.Model):
    _name = 'back_channel_progress_job_setting'
    _description = '后整进度表岗位设置'
    _rec_name = 'key'
    _order = "key"


    key = fields.Char(string='Key', required=True)
    values = fields.Many2many("hr.job", string="岗位", required=True)