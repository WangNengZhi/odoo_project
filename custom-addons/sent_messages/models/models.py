from odoo import models, fields

class SentMessages(models.Model):
    _name = 'sent_messages'
    _description = '已发送消息'
    _order = "send_time desc"

    msg_type = fields.Selection([('enterprise_weixin','企业微信')], string='消息类型')
    msg_category = fields.Char(string='消息类目')
    msg_summary = fields.Text(string='消息摘要')
    send_time = fields.Datetime(string='发送时间')
    sender_uid = fields.Integer(string='发送用户')

    # comment = fields.Text(string='备注')

