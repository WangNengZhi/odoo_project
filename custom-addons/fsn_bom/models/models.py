# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class fsn_bom(models.Model):
#     _name = 'fsn_bom.fsn_bom'
#     _description = 'fsn_bom.fsn_bom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
