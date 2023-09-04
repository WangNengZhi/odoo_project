from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PlatformLinkman(models.Model):
    _name = 'platform_linkman'
    _description = '电商联系人'
    _rec_name = 'name'
    # _order = "name desc"


    platform_type = fields.Many2one("platform_type", string="平台类型", required=True)
    name = fields.Char(string="账号名称", required=True)
    amount_fans = fields.Float(string="粉丝量")
    uuid = fields.Char(string="uid")
    wechat_id = fields.Char(string="微信号")
    phone = fields.Char(string="电话")
    appellation = fields.Char(string="姓名")
    mailing_info = fields.Text(string="邮寄信息")