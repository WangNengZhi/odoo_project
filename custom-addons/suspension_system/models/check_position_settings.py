from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CheckPositionSettings(models.Model):
    _name = 'check_position_settings'
    _description = '组别设置'
    _rec_name = 'group'
    _order = "sequence"


    sequence = fields.Integer()
    suspension_system_line_id = fields.Many2one("suspension_system_line", string="流水线")
    line_number = fields.Char(string="线号", compute="set_suspension_system_line_info", store=True)
    line_guid = fields.Char(string="流水线唯一标识", compute="set_suspension_system_line_info", store=True)
    @api.depends('suspension_system_line_id', 'suspension_system_line_id.line_number', 'suspension_system_line_id.line_guid')
    def set_suspension_system_line_info(self):
        for record in self:
            record.line_number = record.suspension_system_line_id.line_number
            record.line_guid = record.suspension_system_line_id.line_guid

    group = fields.Char(string="组别")

    check_position_settings_id = fields.Many2one("check_position_settings")
    true_group_ids = fields.One2many("check_position_settings", "check_position_settings_id", string="真实组别")


    position = fields.Integer(string="站位")
    position_line_ids = fields.One2many("position_lines", "check_position_settings_ids", string="站位明细")
    department_id = fields.Selection([
        ('车间', '车间'),
        ('裁床', '裁床'),
        ('后道', '后道'),
    ], string='部门')

    repair_fulcrum = fields.Integer(string="返修支点站位")
    repair_group = fields.Many2one("check_position_settings", string="返修组别")
    repair_group_position_lines_id = fields.One2many("repair_group_position_lines", "check_position_settings_ids", string="返修组别站位明细")

    active = fields.Boolean(default=True)

    @api.constrains('group')
    def _check_unique(self):

        for record in self:

            demo = self.env[record._name].sudo().search([
                ("line_number", "=", record.line_number),
                ])

            if len(demo) > 1:
                raise ValidationError(f"已经存在该组的记录了！不可重复创建！")




class PositionLines(models.Model):
    _name = 'position_lines'
    _description = '组别站位明细'
    _rec_name = 'position'


    check_position_settings_ids = fields.Many2one("check_position_settings", string="组别设置")
    position = fields.Integer(string="站位", required=True)
    type = fields.Selection([('中查', '中查'), ('总检', '总检'), ('尾查', '尾查')], string="站位类型", required=True)



class RepairGroupPositionLines(models.Model):
    _name = 'repair_group_position_lines'
    _description = '返修组别站位明细'
    _rec_name = 'position'


    check_position_settings_ids = fields.Many2one("check_position_settings", string="组别设置")
    position = fields.Integer(string="站位", required=True)




