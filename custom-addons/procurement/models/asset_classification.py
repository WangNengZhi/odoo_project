from odoo import models, fields, api


class AssetClassification(models.Model):
    """固定资产分类登记表"""
    _name = 'asset_classification'
    _description = '固定资产分类登记表'
    _rec_name = 'assert_code'

    date = fields.Date(string='日期', required=True)
    assert_code = fields.Char(string="资产编码")
    assert_name = fields.Char(string="资产名称", required=True)
    asset_type = fields.Selection([('设备', '设备'), ('运输工具', '运输工具'), ('机械设备', '机械设备')], string="资产类型")
    use_department = fields.Many2one('hr.department', string="使用部门", required=True)
    recipients_people = fields.Many2one('hr.employee', string="使用人", required=True)
    specification_model = fields.Char(string="规格型号", required=True)
    acquisition_date = fields.Date(string='取得日期 ')

    @api.model
    def create(self, vals):
        vals['assert_code'] = self.env['ir.sequence'].next_by_code('office_object_instance')

        return super(AssetClassification, self).create(vals)
