# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class development_center(models.Model):
#     _name = 'development_center.development_center'
#     _description = 'development_center.development_center'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
