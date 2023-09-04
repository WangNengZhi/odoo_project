# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class suspension_system(models.Model):
#     _name = 'suspension_system.suspension_system'
#     _description = 'suspension_system.suspension_system'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
