# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MaterialTable(models.Model):
    _name = "material_table"
    _description = '用料表'


    name = fields.Char(string="名称")
    specificationss = fields.Char(string="规格")
    quantity = fields.Integer(string="数量")
    measure_of_area = fields.Float(string="米/面积")
    purchase_date = fields.Date(string="采购日期")
    item_number = fields.Many2one('ib.detail', string='款号')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    consumption = fields.Float(string="用量")
    position = fields.Char(string="部位")
    materials_date = fields.Date(string="用料日期")