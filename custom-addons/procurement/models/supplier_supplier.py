from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SupplierSupplier(models.Model):
    _name = 'supplier_supplier'
    # _inherit = ['adyen.address.mixin']
    _description = '供应商'
    _rec_name = 'supplier_name'
    _order = "priority desc"


    supplier_name = fields.Char(string="供应商名称", required=True)
    supplier_use = fields.Selection([
        ('机修设备', '机修设备'),
        ('办公室用品', '办公室用品'),
        ('面辅料', '面辅料')
        ], string="供应商分类")
    processing_type = fields.Char(string="加工类型", required=True)
    contact = fields.Char(string="联系方式", required=True)
    country_id = fields.Many2one('res.country', string='国家', required=True)
    country_code = fields.Char(related='country_id.code')
    state_id = fields.Many2one('res.country.state', string='省份', domain="[('country_id', '=?', country_id)]", required=True)
    detailed_address = fields.Text(string="详细地址", required=True)

    priority = fields.Float(string='优先级', default=50, required=True)
    is_activity = fields.Boolean(string="启用", default=True)

    active = fields.Boolean(default=True)


    note = fields.Text(string="备注")

    fsn_customer_id = fields.Many2one("fsn_customer", string="FSN客户")

    def create_fsn_customer(self):
        for record in self:
            fsn_customer_obj = self.env['fsn_customer'].sudo().search([("name", "=", record.supplier_name)])
            if not fsn_customer_obj:
                fsn_customer_obj = self.env['fsn_customer'].sudo().create({"name": record.supplier_name, "type": "外部", "customer_type": "公司"})

            record.fsn_customer_id = fsn_customer_obj.id



    @api.model
    def create(self, vals):

        res = super(SupplierSupplier,self).create(vals)

        if res.supplier_use == "面辅料":
            res.create_fsn_customer()

        return res