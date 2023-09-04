from odoo.exceptions import ValidationError
from odoo import models, fields, api


class ApprovalProcessConfig(models.Model):
    _name = 'approval_process_config_type'
    _description = '审批流程配置类型'
    _rec_name = 'name'
    # _order = 'month desc'

    name = fields.Char(string="审批类型名称", required=True)



class ApprovalProcessConfig(models.Model):
    _name = 'approval_process_config'
    _description = '审批流程配置'
    _rec_name = 'type'
    # _order = 'month desc'
    
    type = fields.Many2one("approval_process_config_type", string="审批类型")
    approval_process_config_line_ids = fields.One2many("approval_process_config_line", "approval_process_config_id", string="审批流程明细")



class ApprovalProcessConfigLine(models.Model):
    _name = 'approval_process_config_line'
    _description = '审批流程配置'

    approval_process_config_id = fields.Many2one("approval_process_config", string="审批流程设置")
    sequence = fields.Integer(string="序号")
    emp_id = fields.Many2one('hr.employee', string='审批人')










