# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class fsn_p2p(models.Model):
#     _name = 'fsn_p2p.fsn_p2p'
#     _description = 'fsn_p2p.fsn_p2p'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
