
from odoo import models, fields, api
from datetime import timedelta


class WechatProcessConfirm(models.Model):
    _name = 'wechat_process_confirm'
    _description = '微信工序确认'
    _rec_name = 'process_describe'
    _order = "date desc"


    date = fields.Date(string="日期")
    employee_id = fields.Many2one("hr.employee", string="员工id", compute='_set_employee_id', store=True)
    work_number = fields.Char(string="工号")
    group_id = fields.Many2one("check_position_settings", string="组别")
    position = fields.Char(string="站位")
    style_number = fields.Char(string="款号")
    process_number = fields.Char(string="工序号")
    process_describe = fields.Text(string="工序描述")

    number = fields.Float(string="件数", compute="_set_number", store=True)

    station_summaryseqno_line_objs = fields.One2many("station_summaryseqno_line", "wechat_process_confirm_id", string="吊挂工序")


    # 设置员工信息
    @api.depends('work_number')
    def _set_employee_id(self):
        for record in self:
            if record.work_number:
                hr_employee_obj = self.env["hr.employee"].sudo().search([("barcode", "=", record.work_number)])
                record.employee_id = hr_employee_obj.id

    # 计算件数
    @api.depends('station_summaryseqno_line_objs', 'station_summaryseqno_line_objs.number')
    def _set_number(self):
        for record in self:

            record.number = sum(record.station_summaryseqno_line_objs.mapped('number'))



    # 设置件数
    def set_station_summaryseqno_line_objs(self, today):

        # 日期减少一天
        today = today - timedelta(days=1)

        # 按日期查询
        wechat_process_confirm_objs = self.env["wechat_process_confirm"].sudo().search([
            ("date", "=", today)
        ])

        for record in wechat_process_confirm_objs:

            suspension_system_station_summary_objs = self.env["suspension_system_station_summary"].sudo().search([
                ("dDate", "=", record.date),    # 日期
                ("employee_id", "=", record.employee_id.id),   # 员工
                ("group", "=", record.group_id.id),     # 组别
                ("station_number", "=", int(record.position)),      # 站号
                ("style_number", "like", record.style_number),      # 款号
            ])
            for suspension_system_station_summary_obj in suspension_system_station_summary_objs:

                station_summaryseqno_line_objs = self.env["station_summaryseqno_line"].sudo().search([
                    ("seqno_id", "=", suspension_system_station_summary_obj.id),
                    ("SeqNo", "=", int(record.process_number)),
                ])

                for station_summaryseqno_line_obj in station_summaryseqno_line_objs:
                    station_summaryseqno_line_obj.wechat_process_confirm_id = record.id



