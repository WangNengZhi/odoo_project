from odoo import models, fields, api


class MaintenanceRecords(models.Model):
    _name = 'maintenance_records'
    _description = '固定资产维护保养记录'

    assert_code = fields.Many2one("asset_classification", string="资产编号", required=True)
    assert_name = fields.Char(string="资产名称", compute="set_material_info", store=True)
    asset_type = fields.Selection([('设备', '设备'), ('运输工具', '运输工具'), ('机械设备', '机械设备')],
                                  string="资产类型", compute="set_material_info", store=True)
    maintenance_time = fields.Date(string="保养时间", required=True)
    maintenance_personnel = fields.Many2one('hr.employee', string="保养人员", required=True)
    maintenance_content = fields.Char(string='保养内容', required=True)
    maintenance_results = fields.Char(string='保养结果', required=True)
    problem_description = fields.Char(string='问题描述', required=True)
    maintenance_measures = fields.Char(string='维修措施', required=True)
    maintenance_costs = fields.Char(string='维修费用', required=True)
    notes = fields.Char(string='备注')

    @api.depends('assert_code')
    def set_material_info(self):
        for record in self:
            record.assert_name = record.assert_code.assert_name
            record.asset_type = record.assert_code.asset_type
