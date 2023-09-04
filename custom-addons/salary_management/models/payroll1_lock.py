from odoo import models, fields, api
from odoo.exceptions import ValidationError


def get_last_year_month(year, month):
    ''' 获取指定月份之前的上一个月份'''

    month -= 1

    if month == 0:
        year, month = year - 1, 12
    
    return f'{year}-{month:02}'



class SalaryLockSetting(models.Model):
    _name = "salary_lock_setting"
    _description = '薪酬可修改限制设置'

    model_id = fields.Many2one('ir.model', string='模型', required=True, ondelete='cascade')
    year_month = fields.Char(string="可操作月份")
    is_operable = fields.Boolean(string="是否可操作", default=False)



class salary(models.Model):
    _inherit = "payroll1"


    def check_salary_lock_setting(self, year_month):
        ''' 查询操作配置'''

        salary_lock_setting_obj = self.env['salary_lock_setting'].sudo().search([("model_id", "=", self.env['ir.model']._get(self._name).id)])
        if salary_lock_setting_obj:
            return salary_lock_setting_obj.is_operable
        else:
            raise ValidationError(f"未设置薪酬明细可修改限制，不可操作！")



    def check_whether_is_operable(self, year_month):
        ''' 判断是否可操作'''
        today = fields.Date.today()

        last_year_month = get_last_year_month(today.year, today.month)

        if year_month != last_year_month:

            if not self.check_salary_lock_setting(year_month):
                raise ValidationError(f"该月份数据不可执行创建、编辑、删除等操作！")


    @api.model
    def create(self, vals):

        self.check_whether_is_operable(vals['date'])

        res = super(salary, self).create(vals)

        return res


    def write(self, vals):

        self.check_whether_is_operable(self.date)

        res = super(salary, self).write(vals)

        return res
    

    def unlink(self):

        for record in self:
            record.check_whether_is_operable(record.date)

        res = super(salary, self).unlink()

        return res
