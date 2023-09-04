from odoo import models, fields, api
from odoo.exceptions import ValidationError



class StationTwiceSendBack(models.Model):
    _name = 'station_twice_send_back'
    _description = '车位二次退回'
    _rec_name = 'dDate'
    _order = "dDate desc"

    dDate = fields.Date(string="日期", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    gGroup = fields.Char('组别', required=True)

    employee_name = fields.Char(string="员工", required=True)
    inspector = fields.Char(string="检查员", required=True)

    repair_number = fields.Integer(string="退修数")
    twice_repair_number = fields.Integer(string="二次退回数")
    twice_repair_ratio = fields.Float(string="二次退回率", compute="set_repair_ratio", store=True)

    repair_type = fields.Char(string="返修类型")


    # 设置返修率
    @api.depends('repair_number', 'twice_repair_number')
    def set_repair_ratio(self):
        for record in self:
            if record.repair_number:
                record.twice_repair_ratio = (record.twice_repair_number / record.repair_number) * 100
            else:

                record.twice_repair_ratio = 0
    

