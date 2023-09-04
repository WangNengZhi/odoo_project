import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class set_up_days(models.Model):
    _name = 'set.up.base'
    _description = '设置基本信息'

    date = fields.Char(string='日期')
    base_pay = fields.Float(string='基本工资')
    housing_supplement = fields.Float(string='租房津贴')
    rice_tonic = fields.Float(string='饭补')
    perfect_attendance = fields.Float(string="全勤奖励")

    @api.constrains('date')
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

        date = is_valid_date(self.date)
        if date:
            pass
        else:
            raise ValidationError("日期要符合类似1990-01")


