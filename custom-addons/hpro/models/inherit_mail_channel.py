from odoo import api, fields, models, _


class Channel(models.Model):
    _inherit = 'mail.channel'


    def send_messagrs(self, **kw):

        res_user_obj = self.env["res.users"].sudo().search([("id", "=", kw["user_id"])])
        sender_id = res_user_obj.partner_id.id

        channel = self.browse(self.env.ref("hpro.on_work_special_purpose").id)
        message = f"今日现场工序已经录入完成！"

        channel.sudo().message_post(body=message, author_id=sender_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel