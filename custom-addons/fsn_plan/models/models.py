# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class fsn_plan(models.Model):
#     _name = 'fsn_plan.fsn_plan'
#     _description = 'fsn_plan.fsn_plan'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
