from odoo import models, fields, api


class FsnDeliveryProcess(models.Model):
    _name = 'fsn_delivery_process'
    _description = 'FSN交货流程'
    _rec_name = 'delivery_stage'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    delivery_stage = fields.Selection([
        ('裁床交货', '裁床交货'),
        ('车间交货', '车间交货'),
        ('后道交货', '后道交货')
    ], string="交货阶段", required=True)
    state = fields.Selection([
        ('草稿', '草稿'),
        ('交货中', '交货中'),
        ('交货完成', '交货完成')
    ], string="状态", default="草稿")


    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", related="style_number.fsn_color", store=True)
    size = fields.Many2one("fsn_size", string="尺码", store=True, required=True)
    number = fields.Integer(string="数量")

    delivery_man = fields.Many2one('hr.employee', string="交货人", required=True)
    department_id = fields.Many2one("hr.department", string="交货人部门", compute="set_delivery_man_info", store=True)
    job_id = fields.Many2one("hr.job", string="交货人岗位", compute="set_delivery_man_info", store=True)

    @api.depends('delivery_man')
    def set_delivery_man_info(self):
        for record in self:
            if record.delivery_man:
                record.department_id = record.delivery_man.department_id.id
                record.job_id = record.delivery_man.job_id.id


    fsn_delivery_receive_staff_ids = fields.One2many('fsn_delivery_receive_staff', 'fsn_delivery_process_ids', string="接收人员明细")

    @api.depends('fsn_delivery_receive_staff_ids', 'fsn_delivery_receive_staff_ids.recipient')
    def change_state(self):
        for record in self:
            if record.delivery_stage == "裁床交货":
                pass
            


class FsnDeliveryReceiveStaff(models.Model):
    _name = 'fsn_delivery_receive_staff'
    _description = 'FSN交货接收人员明细'

    fsn_delivery_process_ids = fields.Many2one("fsn_delivery_process", string="交货流程", ondelete='cascade')

    recipient = fields.Many2one('hr.employee', string="交货人", required=True)
    department_id = fields.Many2one("hr.department", string="接收人部门", compute="set_recipient_info", store=True)
    job_id = fields.Many2one("hr.job", string="接收人岗位", compute="set_recipient_info", store=True)
    @api.depends('recipient')
    def set_recipient_info(self):
        for record in self:
            if record.recipient:
                record.department_id = record.recipient.department_id.id
                record.job_id = record.recipient.job_id.id