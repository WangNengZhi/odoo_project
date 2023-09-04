from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime

class MailMessage(models.Model):
    _inherit = 'mail.message'

    active = fields.Boolean(string="Active", default=True)


class FsnCleanMessage(models.TransientModel):
    _name = 'fsn_clean_message'
    _description = 'FSN清理消息'


    # 消息清理
    def clean_message(self, today, interval):
        # 
        today = today - timedelta(days=interval)
        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")

        mail_message_objs = self.env["mail.message"].search([
            ("date", "<", today),
            ("author_id", "=", odoobot_id),
            ("active", "=", True),
            ("model", "=", "mail.channel")
        ])

        mail_message_objs.active = False

        today = today - timedelta(days=interval)

        mail_message_objs = self.env["mail.message"].search([
            ("date", "<", today),
            ("author_id", "=", odoobot_id),
            ("active", "=", False),
            ("model", "=", "mail.channel")
        ])
        for mail_message_obj in mail_message_objs:

            mail_message_obj.unlink()


