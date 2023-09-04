
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EcVideoData(models.Model):
    _name = 'ec_video_data'
    _description = '视频数据'
    _rec_name = 'platform_account_id'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)
    topic = fields.Char(string="题目", required=True)
    author_id = fields.Many2one('hr.employee', string='作者', required=True)
    uploading_date = fields.Datetime(string="上传时间", required=True)
    amount_play_24_hours = fields.Float(string="24小时播放量")
    seeding_rate = fields.Float(string="完播率")
    broadcast_time = fields.Float(string="播放时长")
    thumb_up_rate = fields.Float(string="点赞率")
    absorption_rate = fields.Float(string="吸粉率")

    thumb_up_quantity = fields.Float(string="点赞量")
    amount_video_play = fields.Float(string="视频播放量")
    work_interaction_rate = fields.Float(string="作品互动率", compute="set_work_interaction_rate", store=True)
    @api.depends('thumb_up_quantity', 'amount_video_play')
    def set_work_interaction_rate(self):
        for record in self:
            if record.amount_video_play:
                record.work_interaction_rate = record.thumb_up_quantity / record.amount_video_play

    shake_add_cost = fields.Float(string="抖+费用")


