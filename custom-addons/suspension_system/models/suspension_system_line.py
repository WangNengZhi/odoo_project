from odoo import api, fields, models

class SuspensionSystemLine(models.Model):
    _name = 'suspension_system_line'
    _description = '吊挂系统流水线'
    _rec_name = 'line_number'
    _order = "sequence"

    sequence = fields.Integer()
    line_number = fields.Char(string="线号", required=True)
    line_guid = fields.Char(string="流水线唯一标识", required=True)