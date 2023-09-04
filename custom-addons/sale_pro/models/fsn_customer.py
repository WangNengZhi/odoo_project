from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FsnCustomer(models.Model):
    _name = 'fsn_customer'
    _description = 'FSN客户'
    _rec_name = 'name'
    _order = "name"


    name = fields.Char(string="客户名称", required=True)
    customer_type = fields.Selection([('公司', '公司'), ('个人', '个人')], string="类型", required=True)
    phone = fields.Char(string="电话")
    email = fields.Char(string="邮箱")
    def set_default_country_id(self):
        return self.env['res.country'].sudo().search([("name", "=", "中国")]).id
    country_id = fields.Many2one('res.country', string='国家', default=set_default_country_id)
    country_code = fields.Char(related='country_id.code')
    state_id = fields.Many2one('res.country.state', string='省份', domain="[('country_id', '=?', country_id)]")
    detailed_address = fields.Text(string="详细地址")

    type = fields.Selection([('内部', '内部'), ('外部', '外部')], string="类型", required=True)

    active = fields.Boolean(default=True, string="启用")

    fsn_customer_ids = fields.One2many("fsn_customer", "fsn_customer_id", string="员工")

    fsn_customer_id = fields.Many2one("fsn_customer", string="公司")
    
    active = fields.Boolean(default=True)

    # 检查数据唯一性
    @api.constrains('customer_number')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('name', '=', self.name),
        ])

        if len(demo) > 1:
            raise ValidationError(f"客户名称不可重复！")
