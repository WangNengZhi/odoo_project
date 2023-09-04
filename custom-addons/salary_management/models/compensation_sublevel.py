from odoo.exceptions import ValidationError
from odoo import models, fields, api

import datetime
import calendar



class CompensationSublevel(models.Model):
    _name = 'compensation_sublevel'
    _description = '薪酬分阶'
    # _order = "date desc"
    _rec_name = 'month'


    month = fields.Char(string="月份")
    hr_employee_id = fields.Many2one('hr.employee', string='员工')
    hr_department_id = fields.Many2one("hr.department", string="部门", compute="_set_emp_message", store=True)
    contract = fields.Char(string='工种', compute="_set_emp_message", store=True)
    month_workpiece_ratio = fields.Float(string="月平均效率(%)")

    compensation = fields.Float(string="薪资", compute="_set_compensation", store=True)



    # 设置员工信息
    @api.depends('hr_employee_id')
    def _set_emp_message(self):
        for record in self:
            # 合同/工种
            record.contract = record.hr_employee_id.is_it_a_temporary_worker
            # 部门
            record.hr_department_id = record.hr_employee_id.department_id.id

    
    # 设置薪资
    @api.depends('month_workpiece_ratio')
    def _set_compensation(self):
        for record in self:

            if record.month_workpiece_ratio >= 30:
                record.compensation = 4000 + (record.month_workpiece_ratio - 30) * ((7000-4000) / (100-30))
            else:
                record.compensation = 4000
            


    # 获取当月第一天和最后一天
    def set_begin_and_end(self, year_month):

            year_month_list = year_month.split('-')
            year = year_month_list[0]
            month = year_month_list[1]
            day = 1
            date_pinjie = year + '-' + month + '-' + str(day)

            #    这就是年月的算法，返回本月天数
            month_math = calendar.monthrange(int(year), int(month))[1]

            #  本月的最大时间
            date_end_of_the_month5 = year + '-' + str(month) + '-' + str(month_math)
            date_end_of_the_month6 = datetime.datetime.strptime(date_end_of_the_month5, '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

            date_end = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')      # 当月第一天

            return {"begin": date_end, "end": date_end_of_the_month6}


    # 生成记录
    def generate_records(self, year_month):

        this_month = self.set_begin_and_end(year_month)
        first_day = this_month["begin"]
        last_day = this_month["end"]

        hr_employee_objs = self.env["hr.employee"].sudo().search([('entry_time', '<=', last_day), '|',("is_delete_date", ">", first_day), ('is_delete_date', '=', False)])

        for hr_employee_obj in hr_employee_objs:

            if hr_employee_obj.is_it_a_temporary_worker in ["正式工(计件工资)", "临时工", "实习生(计件)"]:

                obj = self.sudo().search([("month", "=", year_month), ("hr_employee_id", "=", hr_employee_obj.id)])
                if obj:
                    pass
                else:

                    self.sudo().create({
                        "month": year_month,
                        "hr_employee_id": hr_employee_obj.id,
                    })
        
        return True



    # 计算月平均效率
    def set_month_workpiece_ratio(self):

        for record in self:


            # 获取当月第一天和最后一天
            this_month = record.set_begin_and_end(record.month)
            first_day = this_month["begin"]
            last_day = this_month["end"]

            eff_eff_objs = self.env["automatic_efficiency_table"].sudo().search([
                ("date", ">=", first_day),
                ("date", "<=", last_day),
                ("employee_id", "=", record.name.id)
            ])

            if eff_eff_objs:

                record.month_workpiece_ratio = sum(eff_eff_objs.mapped('efficiency')) / len(eff_eff_objs)

            else:

                record.month_workpiece_ratio = 0
