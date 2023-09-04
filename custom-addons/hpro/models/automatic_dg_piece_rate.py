from odoo.exceptions import ValidationError
from odoo import models, fields, api


class DgPieceRate(models.Model):
    _name='dg_piece_rate'
    _description = '吊挂计件工资'
    _order = 'date desc'


    date = fields.Date('日期')
    employee_id = fields.Many2one('hr.employee', string="员工")
    contract_type = fields.Char(string="合同/工种", compute="set_contract_type", store=True)
    group_id = fields.Many2one("check_position_settings", string="组别")
    cost = fields.Float('计件工资', compute="set_cost", store=True)
    automatic_scene_process_ids = fields.One2many("automatic_scene_process", "dg_piece_rate_id", string="自动现场工序")


    # 设置工种，在职状态
    @api.depends('employee_id')
    def set_contract_type(self):
        for record in self:
            record.contract_type = record.employee_id.is_it_a_temporary_worker


    # 设置计件工资
    @api.depends('automatic_scene_process_ids', 'automatic_scene_process_ids.process_wages')
    def set_cost(self):
        for record in self:

            record.cost = sum(record.automatic_scene_process_ids.mapped('process_wages'))

