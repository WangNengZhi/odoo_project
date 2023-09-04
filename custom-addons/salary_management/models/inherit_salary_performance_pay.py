from odoo.exceptions import ValidationError
from odoo import models, fields, api


class salary(models.Model):
    _inherit = "salary"


    # 计算绩效工资
    def set_performance_pay(self):

        for record in self:

            # 获取当月第一天和最后一天
            this_month = self.set_begin_and_end()
            first_day = this_month["begin"]
            last_day = this_month["end"]

            tem_performance_pay = 0     # 临时绩效工资

            # 计算中查绩效
            tem_middle_check_performance_pay = record.calculate_middle_check_performance(first_day, last_day)

            # 计算总检绩效
            tem_always_check_performance_pay = record.calculate_always_check_performance(first_day, last_day)

            # 计算人事绩效
            tem_personnel_award_performance_pay = record.calculate_personnel_award_performance(first_day, last_day)


            # 绩效工资 = 人事绩效 - 中查绩效 - 总检绩效
            tem_performance_pay = tem_personnel_award_performance_pay - tem_middle_check_performance_pay - tem_always_check_performance_pay

            record.performance_pay = tem_performance_pay





    # 计算中查绩效 中查漏查表(日：按中查)
    def calculate_middle_check_performance(self, first_day, last_day):

        middle_check_day_leak_objs = self.env["middle_check_day_leak"].sudo().search([
            ("middle_check_principal", "like", self.name.name),     # 匹配员工姓名
            ("date", ">=", first_day),
            ("date", "<=", last_day)
        ])

        tem_middle_check_performance_pay = 0

        for middle_check_day_leak_obj in middle_check_day_leak_objs:
            tem_middle_check_performance_pay = tem_middle_check_performance_pay + middle_check_day_leak_obj.assess_index

        return tem_middle_check_performance_pay


    # 计算总检绩效 总检漏查(日)
    def calculate_always_check_performance(self, first_day, last_day):

        always_check_day_leak_objs = self.env["always_check_omission"].sudo().search([
            ("always_check_principal", "like", self.name.name),     # 匹配员工姓名
            ("dDate", ">=", first_day),
            ("dDate", "<=", last_day)
        ])

        tem_always_check_performance_pay = 0

        for always_check_day_leak_obj in always_check_day_leak_objs:
            tem_always_check_performance_pay = tem_always_check_performance_pay + always_check_day_leak_obj.assess_index

        return tem_always_check_performance_pay


    # 计算人事奖励
    def calculate_personnel_award_performance(self, first_day, last_day):

        # 计算奖励金额
        self.env["personnel_award"].sudo().action_calculate_award_money(first_day)

        # 如果是人事行政部门的，则计算人事绩效
        if self.name.department_id.name == "人事行政部":

            personnel_award_count = self.env["personnel_award"].sudo().search_count([
                ("introducer", "=", self.name.id),  # 员工id
                ("working_time", ">=", 30),     # 在职时长大于30天
                ("satisfy_date", ">=", first_day),  # 满足30天日期大于等于当月第一天
                ("satisfy_date", "<=", last_day),  # 满足30天日期小于等于当月第一天
            ])

            # tem_award_money = 0
            # for personnel_award_obj in personnel_award_objs:

            #     personnel_award_line_obj = personnel_award_obj.personnel_award_line_ids.sudo().search([
            #         ("personnel_award_id", "=", personnel_award_obj.id),
            #         ("award_month", "=", f"{first_day.year}-{'%02d' % first_day.month}")
            #     ])

            #     tem_award_money = tem_award_money + personnel_award_line_obj.award_money

            return personnel_award_count * 100

        else:
            return 0

            # personnel_award_objs = self.env["personnel_award"].sudo().search([
            #     ("introducer", "=", self.name.id),  # 员工id
            #     ("working_time", ">=", 30),     # 在职时长大于30天
            #     ("satisfy_date", ">=", first_day),  # 满足30天日期大于等于当月第一天
            #     ("satisfy_date", "<=", last_day),  # 满足30天日期小于等于当月第一天
            # ])

            # tem_award_money = 0
            # for personnel_award_obj in personnel_award_objs:

            #     personnel_award_line_obj = personnel_award_obj.personnel_award_line_ids.sudo().search([
            #         ("personnel_award_id", "=", personnel_award_obj.id),
            #         ("award_month", "=", f"{first_day.year}-{'%02d' % first_day.month}")
            #     ])

            #     tem_award_money = tem_award_money + personnel_award_line_obj.award_money

            # return (tem_award_money / 100) * 3

