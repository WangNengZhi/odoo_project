from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"



    def create_fsn_customer(self):
        for record in self:
            fsn_customer_obj = self.env['fsn_customer'].sudo().search([("name", "=", record.name)])
            if not fsn_customer_obj:
                fsn_customer_obj = self.env['fsn_customer'].sudo().create({
                    "name": record.name,
                    "customer_type": "公司" if record.company_type == "company" else "个人",
                    "type": "外部"
                })
                
            fsn_customer_obj.res_partner_id = record.id


    @api.model
    def create(self, vals):

        rec = super(ResPartner, self).create(vals)

        rec.create_fsn_customer()

        return rec





class FsnCustomer(models.Model):
    ''' 继承FSN客户'''
    _inherit = "fsn_customer"

    res_partner_id = fields.Many2one("res.partner", string="销售客户")
