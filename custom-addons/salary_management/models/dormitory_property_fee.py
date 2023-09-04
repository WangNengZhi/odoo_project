# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class property(models.Model):
    _name = 'dormitory.property'
    _description = '宿舍物业费'
    _rec_name = 'floor_number'

    floor = fields.Char('楼层')
    floor_number = fields.Char('房间号')
    name = fields.Many2one('hr.employee', string='姓名')
    month = fields.Char('月份')
    water_and_electricity_property_fee_deduction = fields.Float('水电物业费扣款', digits=(10, 2))
    rent_deduction = fields.Float('租金扣款', digits=(10, 2))
    subsidies_for_going_out = fields.Float('外出补贴', digits=(10, 2))

    @api.constrains('month')
    def check_date(self):
        def is_valid_date(strdate):
            '''判断是否是一个有效的日期字符串'''
            try:
                if "-" in strdate:
                    if strdate.split('-')[1] in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                                                 '12']:
                        datetime.datetime.strptime(strdate, "%Y-%m")
                        return True
                    else:
                        return False
            except:
                return False

        date = is_valid_date(self.month)
        if date:
            pass
        else:
            raise ValidationError("月份要符合类似1990-01")


    @api.constrains('name', 'month')
    def _check_unique(self):

        for record in self:

            demo = self.env[record._name].sudo().search([
                ("name", "=", record.name.id),
                ("month", "=", record.month),
                ])
            if len(demo) > 1:
                raise ValidationError(f"同一个员工在同一个月份只能有一条记录!")