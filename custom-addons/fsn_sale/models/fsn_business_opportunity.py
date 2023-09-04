# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FsnBusinessOpportunity(models.Model):
    _name = 'fsn_business_opportunity'
    _description = 'FSN销售商机'
    # _rec_name = 'name'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    sales_staff_id = fields.Many2one('hr.employee', string='销售人员', required=True)
    potential_customer = fields.Char(string="潜在客户", required=True)
    contact_person = fields.Char(string="联系人", required=True)
    telephone = fields.Char(string="电话", required=True)
    address = fields.Char(string="地址", required=True)
    mailbox = fields.Char(string="邮箱")

