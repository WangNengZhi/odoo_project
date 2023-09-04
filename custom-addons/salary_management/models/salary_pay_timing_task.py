from odoo import api, fields, models
import datetime

class FsnDaily(models.TransientModel):
    _name = 'salary_pay_timing_task'
    _description = '薪酬模块定时任务'

    @staticmethod
    def get_before_year_month(year, month):
        ''' 获取指定月份之前的上一个月份'''

        month -= 1

        if month == 0:
            year, month = year - 1, 12
        
        return year, month
        # return f'{year}-{month:02}'


    def refresh_access_restriction_record_rule_domain_force(self, date_):
        ''' 刷新薪酬访问限制的记录规则内容'''

    

        the_01th = datetime.date(date_.year, date_.month, 1)
        the_20th = datetime.date(date_.year, date_.month, 20)

        # year, month, _ = str(date_).split("-")
        # year_month = f"{year}-{month}"

        before_year, before_month = self.get_before_year_month(date_.year, date_.month)

        before_year_month = f'{before_year}-{before_month:02}'
        before_before_year_month = False

        if the_01th <= date_ <= the_20th:

            before_before_year, before_before_month = self.get_before_year_month(before_year, before_month)

            before_before_year_month = f'{before_before_year}-{before_before_month:02}'



        list_ = [before_year_month, before_before_year_month]


        group_rule_obj01 = self.env.ref('salary_management.fsn_salary_restrict_group_rule01')
        group_rule_obj01.domain_force = f"[('date', 'in', {list_})]"


        group_rule_obj02 = self.env.ref('salary_management.fsn_salary_restrict_group_rule02')
        group_rule_obj02.domain_force = f"[('month', 'in', {list_})]"


        group_rule_obj03 = self.env.ref('salary_management.fsn_salary_restrict_group_rule03')
        group_rule_obj03.domain_force = f"[('month', 'in', {list_})]"









