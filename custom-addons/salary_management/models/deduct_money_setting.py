from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime


class DeductMoneySetting(models.Model):
    _name = 'deduct_money_setting'
    _description = '扣款设置'
    _rec_name='month'
    _order = "month desc"

    month = fields.Char(string="月份", required=True)


    absenteeism_deduct_money = fields.Selection([
        ('全部工种', '全部工种'),
        ('仅计件工种', '仅计件工种'),
        ('仅临时工', '仅临时工'),
        ('仅计件和临时工', '仅计件和临时工'),
        ('非计件工种', '非计件工种'),
        ('非临时工', '非临时工'),
        ('非计件和临时工', '非计件和非临时工'),
        ], string="旷工扣款设置", required=True)
    absenteeism_deduct_money_ratio = fields.Float(string="旷工扣款比例", default=1)

    matter_vacation_deduct_money = fields.Selection([
        ('全部工种', '全部工种'),
        ('仅计件工种', '仅计件工种'),
        ('仅临时工', '仅临时工'),
        ('仅计件和临时工', '仅计件和临时工'),
        ('非计件工种', '非计件工种'),
        ('非临时工', '非临时工'),
        ('非计件和临时工', '非计件和非临时工'),
        ], string="事假扣款设置", required=True)
    matter_vacation_deduct_money_ratio = fields.Float(string="事假扣款比例", default=1)

    sick_leave_deduct_money = fields.Selection([
        ('全部工种', '全部工种'),
        ('仅计件工种', '仅计件工种'),
        ('仅临时工', '仅临时工'),
        ('仅计件和临时工', '仅计件和临时工'),
        ('非计件工种', '非计件工种'),
        ('非临时工', '非临时工'),
        ('非计件和临时工', '非计件和非临时工'),
        ], string="病假扣款设置", required=True)
    sick_leave_deduct_money_ratio = fields.Float(string="病假扣款比例", default=1)

    be_late_deduct_money = fields.Selection([
        ('全部工种', '全部工种'),
        ('仅计件工种', '仅计件工种'),
        ('仅临时工', '仅临时工'),
        ('仅计件和临时工', '仅计件和临时工'),
        ('非计件工种', '非计件工种'),
        ('非临时工', '非临时工'),
        ('非计件和临时工', '非计件和非临时工'),
        ], string="迟到早退扣款设置", required=True)
    be_late_deduct_money_ratio = fields.Float(string="迟到早退扣款比例", default=1)

    is_dimission_subsidy = fields.Boolean(string="是否有离职补贴")




    @api.constrains('month')
    def check_date(self):
        def is_valid_date(month):
            '''判断是否是一个有效的日期字符串'''
            try:
                if "-" in month:
                    if month.split('-')[1] in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
                                                 '12']:
                        datetime.strptime(month, "%Y-%m")
                        return True
                    else:
                        return False
            except:
                return False

        month = is_valid_date(self.month)
        if month:
            pass
        else:
            raise ValidationError("日期要符合类似1990-01")