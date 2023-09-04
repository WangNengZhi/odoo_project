from odoo.exceptions import ValidationError
from odoo import models, fields, api


class EfficiencyWagesSetting(models.Model):
    _name = 'efficiency_wages_setting'
    _description = 'FSN效率薪资设置'

    date = fields.Char(string='月份', required=True)
    type = fields.Selection([('通用', '通用'), ('大烫', '大烫'), ('裁床主刀', '裁床主刀')], string="状态")
    lowest_efficiency = fields.Float(string="最低效率")
    growth_numerical = fields.Float(string="增长数值")
    lowest_efficiency_wages = fields.Float(string="最低效率薪资")
    first_month_min_wages = fields.Float(string="正式工首月最低效率薪资")
    lowest_efficiency_following_wages = fields.Float(string="最低效率以下薪资")

    


    @api.constrains('date')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([
                ('date', '=', record.date),
                ('type', '=', record.type)
                ])
            if len(demo) > 1:
                raise ValidationError(f"已经存在该月份效率薪资设置配置信息了！")


class GroupLeaderWagesSetting(models.Model):
    _name = 'group_leader_wages_setting'
    _description = 'FSN组长效率薪资设置'

    
    employees_number = fields.Integer(string="员工人数")
    salary_quota = fields.Float(string="薪酬额度")


    @api.constrains('employees_number')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('employees_number', '=', record.employees_number)])
            if len(demo) > 1:
                raise ValidationError(f"员工人数重复，不可操作！")