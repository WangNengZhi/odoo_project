# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentManagement(models.Model):

    _name = "equipment_management"
    _description = '设备管理'
    _rec_name = 'asset_number'
    _order = "date desc"


    asset_number = fields.Char(string="资产编号")
    date = fields.Date(string="日期")
    asset_name = fields.Char(string="资产名称")
    equipment_type = fields.Char(string="型号")
    amount = fields.Float(string="数量")
    unit = fields.Char(string="单位")
    warehouse_amount = fields.Float(string="仓库数量")
    workshop_amount = fields.Float(string="车间数量")


    @api.constrains('asset_number')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('asset_number', '=', record.asset_number)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在序号为：{record.asset_number}的记录了！")
