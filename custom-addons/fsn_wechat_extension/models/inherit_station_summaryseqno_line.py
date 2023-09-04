from odoo import models, fields, api


class StationSummaryseqnoLine(models.Model):
    """ 继承站位吊挂明细"""
    _inherit = 'station_summaryseqno_line'

    is_affirm_state = fields.Selection([
        ('有异议', '有异议'),
        ('已确认', '已确认'),
        ('系统', '系统'),
    ], string="确认状态", default="系统")

    wechat_process_confirm_id = fields.Many2one("wechat_process_confirm", string="微信工序确认")



