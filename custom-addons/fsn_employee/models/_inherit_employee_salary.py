from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"



    attendance_bonus_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="全勤奖类型", required=True)
    attendance_bonus_limit = fields.Float(string="全勤奖额度")

    meal_allowance_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="饭补类型", required=True)
    meal_allowance_limit = fields.Float(string="饭补额度")

    housing_subsidy_type = fields.Selection([
        ('薪酬之内', '薪酬之内'),
        ('薪酬之外', '薪酬之外'),
    ], string="房补类型", required=True)
    housing_subsidy_limit = fields.Float(string="房补额度")

    dimission_nature = fields.Selection([
        ('急辞', '急辞'),
        ('劝退', '劝退'),
        ('自离', '自离'),
    ], string="离职性质")

    performance_money = fields.Float(string="绩效奖金")



    # 检查补贴额度，是否为0
    @api.constrains('attendance_bonus_type', 'meal_allowance_type', 'housing_subsidy_type')
    def _check_subsidies_limit(self):

        if self.is_it_a_temporary_worker != "外包(计时)" and self.is_it_a_temporary_worker != "外包(计件)":

            if self.attendance_bonus_limit == 0:

                raise ValidationError(f"全勤奖额度不可为0！")

            if self.meal_allowance_limit == 0:

                raise ValidationError(f"饭补额度不可为0！")

            if self.housing_subsidy_limit == 0:

                raise ValidationError(f"房补额度不可为0！")

