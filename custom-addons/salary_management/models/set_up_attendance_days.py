import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class set_up_days(models.Model):
    _name = 'set.up.days'
    _description = '设置出勤天数'

    date = fields.Char(string='月份', required=True)
    day = fields.Float(string='正式工(A级管理)应出勤天数')
    day1 = fields.Float(string='正式工(B级管理)应出勤天数')
    day2 = fields.Float(string='正式工(计件工资)应出勤天数')
    day3 = fields.Float(string='临时工应出勤天数')
    day4 = fields.Float(string='实习生应出勤天数')
    day5 = fields.Float(string='外包应出勤天数')

    @api.constrains('date')
    def check_date(self):
        """   处理时间是否正确   """
        def is_valid_date(strdate):
            '''判断是否是一个有效的日期字符串'''
            try:
                if "-" in strdate:
                    if strdate.split('-')[1] in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11','12']:
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