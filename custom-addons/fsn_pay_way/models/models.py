# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class fsn_pay_way(models.Model):
#     _name = 'fsn_pay_way.fsn_pay_way'
#     _description = 'fsn_pay_way.fsn_pay_way'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
