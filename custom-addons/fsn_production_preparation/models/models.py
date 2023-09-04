# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class fsn_production_preparation(models.Model):
#     _name = 'fsn_production_preparation.fsn_production_preparation'
#     _description = 'fsn_production_preparation.fsn_production_preparation'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
