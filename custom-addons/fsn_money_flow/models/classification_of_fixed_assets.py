from odoo import models, fields, api


class ClassificationOfFixedAssets(models.Model):
    """固定资产分类登记表"""
    _name = 'classification_of_fixed_assets'
    _description = '固定资产分类登记表'

    date = fields.Date(string='日期')
    assert_name = fields.Char(string="资产名称")
    assert_code = fields.Char(string="资产编码")
    asset_type = fields.Selection([('设备', '设备'), ('运输工具', '运输工具'), ('机械设备', '机械设备')], string="资产类型")
    use_department = fields.Many2one('hr.department', string="使用部门")
    recipients_people = fields.Many2one('hr.employee', string="使用人")
    specification_model = fields.Char(string="规格型号")
    acquisition_date = fields.Date(string='取得日期')
    original_value = fields.Float(string='原值')
    expected_service_life = fields.Float(string='预计使用年限')
    accumulated_depreciation = fields.Float(string='累计折旧')
    book_value = fields.Float(string='账面净值', compute='compute_book_value')

    @api.depends('original_value', 'accumulated_depreciation')
    def compute_book_value(self):
        for record in self:
            record.book_value = record.original_value - record.accumulated_depreciation

    notes = fields.Char(string='备注')

    # @api.model
    # def create(self, vals):
    #     """同步数据的时候不影响必填字段"""
    #     with self.env.cr.savepoint():
    #         return super(ClassificationOfFixedAssets, self).create(vals)

    def update_classification(self):
        """更新固定资产分类登记表"""
        classifications = self.env['asset_classification'].search([])

        for classification in classifications:
            existing_record = self.env['classification_of_fixed_assets'].search([
                ('date', '=', classification.date),
                ('assert_name', '=', classification.assert_name),
                ('assert_code', '=', classification.assert_code)
            ])

            if not existing_record:
                data = {
                    'date': classification.date,
                    'assert_name': classification.assert_name,
                    'assert_code': classification.assert_code,
                    'asset_type': classification.asset_type,
                    'use_department': classification.use_department.id,
                    'recipients_people': classification.recipients_people.id,
                    'specification_model': classification.specification_model,
                    'acquisition_date': classification.acquisition_date,
                }
                self.sudo().create(data)
