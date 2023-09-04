from odoo import models, fields, api


class UseRegistrationForm(models.Model):
    _name = 'use_registration_form'
    _description = '固定资产使用登记表'

    date = fields.Date(string="日期", required=True)
    assert_code = fields.Many2one("asset_classification", string="物品编码", required=True)
    assert_name = fields.Char(string="资产名称", compute="set_material_info", store=True)
    asset_type = fields.Selection([('设备', '设备'), ('运输工具', '运输工具'), ('机械设备', '机械设备')],
                                  string="资产类型", compute="set_material_info", store=True)
    use_department = fields.Many2one('hr.department', string="使用部门", compute="set_material_info", store=True)
    recipients_people = fields.Many2one('hr.employee', string="使用人", compute="set_material_info", store=True)
    acquisition_date = fields.Date(string='开始使用使用时间', compute="set_material_info", store=True)
    expected_service_life = fields.Integer(string='预计使用年限', required=True)
    on_state = fields.Selection([('良好', '良好'), ('故障', '故障'), ('报废', '报废')], string="使用状态", required=True)
    mobile_registration = fields.Char(string='移动登记')
    return_registration_date = fields.Date(string='归还登记日期')

    @api.depends('assert_code')
    def set_material_info(self):
        for record in self:
            record.assert_name = record.assert_code.assert_name
            record.asset_type = record.assert_code.asset_type
            record.use_department = record.assert_code.use_department
            record.recipients_people = record.assert_code.recipients_people
            record.acquisition_date = record.assert_code.acquisition_date
