from odoo import models, fields, api


class WechatExtensionGroup(models.Model):
    _name = 'wechat_extension_group'
    _description = '微信小程序权限组'


    name = fields.Char(string="组名", required=True)

    job_ids = fields.Many2many("hr.job", string="岗位")











