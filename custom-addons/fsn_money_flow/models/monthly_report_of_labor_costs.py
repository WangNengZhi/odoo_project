from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from collections import defaultdict


class MonthlyReportOfLaborCosts(models.Model):
     _name = 'monthly_report_of_labor_costs'
     _description = '人工成本月报'

     data = fields.Date(string='日期')
     department = fields.Char(string='部门')
     number_of_employees = fields.Integer(string='部门人数')
     basic_salary = fields.Float(string='基本工资')
     overtime_pay = fields.Float(string='加班费')
     bonuse = fields.Float(string='奖金')
     welfare_expenses = fields.Float(string='福利支出')
     social_security_expenditure = fields.Float(string='社保支出')
     amount = fields.Float(string='合计')
     average_wage = fields.Float(string='平均工资', group_operator='avg')
     average_daily_wage = fields.Float(string='日均工资', group_operator='avg')
     average_salary_of_employees = fields.Float(string='在职人员平均工资')
     average_daily_salary_of_employees = fields.Float(string='在职人员日均工资', group_operator='avg')
     proportion_to_operating_costs = fields.Float(string='占营业成本比', group_operator='avg')



     def update_monthly_labor_report(self):
          """更新人工月报表"""
          # 查询各个部门本月基本工资
          all_months = set(salary_record.month for salary_record in self.env['payroll3'].search([]))

          monthly_department_salary_sum = defaultdict(dict)
          for month in all_months:
               monthly_salary_records = self.env['payroll3'].search([('month', '=', month)])

               department_employee_count = {}
               for salary_record in monthly_salary_records:
                    department_id = salary_record.first_level_department
                    department_id_name = department_id.name

                    if department_id_name in department_employee_count:
                         department_employee_count[department_id_name] += 1
                    else:
                         department_employee_count[department_id_name] = 1

               department_salary_sum = {}
               total_combined_all_departments = 0.0  # 初始化总合计金额

               department_net_salary = {}  # 初始化部门实发工资总额
               department_practical_attendance_days = {}  # 初始化部门实出勤天数总和

               active_employee_count_by_department = {}

               for salary_record in monthly_salary_records:
                    department_id = salary_record.first_level_department
                    department_id_name = department_id.name
                    # 各个部门基本工资
                    basic_wage = salary_record.basic_wage
                    # 各个部门加班费
                    overtime_pay = salary_record.overtime_wage
                    # 各个部门奖金
                    bonus_wage = salary_record.bonus
                    # 各部门福利支出
                    welfare_expenses = salary_record.subsidy
                    # 社保支出
                    retirement = salary_record.pension_individual
                    medical_treatment = salary_record.medical_personal
                    unemployment = salary_record.unemployed_individual

                    total_social_security = retirement + medical_treatment + unemployment

                    total_combined = basic_wage + overtime_pay + bonus_wage + welfare_expenses + retirement + medical_treatment + unemployment

                    department_id = salary_record.first_level_department
                    department_id_name = department_id.name
                    # 检查是否在职，如果在职则增加该部门的在职员工数量
                    if not salary_record.is_delete_date:
                         if department_id_name in active_employee_count_by_department:
                              active_employee_count_by_department[department_id_name] += 1
                         else:
                              active_employee_count_by_department[department_id_name] = 1

                    # 累计部门的实发工资总额和实出勤天数总和
                    if department_id_name in department_net_salary:
                         department_net_salary[department_id_name] += salary_record.paid_wages
                         department_practical_attendance_days[
                              department_id_name] += salary_record.practical_attendance_day
                    else:
                         department_net_salary[department_id_name] = salary_record.paid_wages
                         department_practical_attendance_days[
                              department_id_name] = salary_record.practical_attendance_day

                    # 各个部门总和
                    total_combined_all_departments += total_combined

                    if department_id_name in department_salary_sum:
                         department_salary_sum[department_id_name]['basic_wage'] += basic_wage
                         department_salary_sum[department_id_name]['overtime_pay'] += overtime_pay
                         department_salary_sum[department_id_name]['bonus_wage'] += bonus_wage
                         department_salary_sum[department_id_name]['welfare_expenses'] += welfare_expenses
                         department_salary_sum[department_id_name]['social_security'] += total_social_security
                         department_salary_sum[department_id_name]['combined'] += total_combined

                    else:
                         department_salary_sum[department_id_name] = {
                              'basic_wage': basic_wage,
                              'overtime_pay': overtime_pay,
                              'bonus_wage': bonus_wage,
                              'welfare_expenses': welfare_expenses,
                              'social_security': total_social_security,
                              'combined': total_combined,
                         }

                    department_salary_sum[department_id_name]['month'] = month  # 添加月份到字典

               for department_name, salary_info in department_salary_sum.items():
                    total_basic_wage = salary_info['basic_wage']
                    total_overtime_pay = salary_info['overtime_pay']
                    total_bonus_pay = salary_info['bonus_wage']
                    total_welfare_expenses = salary_info['welfare_expenses']
                    total_social_security = salary_info['social_security']
                    total_combined = salary_info['combined']
                    department_employee_total = department_employee_count.get(department_name, 0)
                    month = salary_info['month']  # 从字典中获取月份

                    # 计算各个部门的合计百分比
                    department_combined_percentage = (total_combined / total_combined_all_departments)

                    monthly_department_salary_sum[month][department_name] = {
                         'employee_total': department_employee_total,
                         'basic_wage': total_basic_wage,
                         'overtime_pay': total_overtime_pay,
                         'bonus_pay': total_bonus_pay,
                         'welfare_expenses': total_welfare_expenses,
                         'social_security': total_social_security,
                         'combined': total_combined,
                         'combined_percentage': department_combined_percentage,
                    }

               # 初始化在职员工平均日均工资
               average_daily_salary_of_employees = 0.0
               for month, department_data in monthly_department_salary_sum.items():
                    for department_name, data in department_data.items():
                         month_dt = datetime.strptime(month, '%Y-%m').date()
                         # 查询当月的数据是否已存在
                         record = self.search([('data', '=', month_dt), ('department', '=', department_name)])
                         if record:
                              # 数据存在，跳过
                              continue

                         # 计算各个部门的合计百分比
                         department_combined_percentage = data['combined_percentage']

                         # 创建记录时使用修改后的百分比值
                         proportion_to_operating_costs = department_combined_percentage * 100

                         average_wage = data['combined'] / data['employee_total'] if data[
                                                                                          'employee_total'] > 0 else 0

                         # 获取部门实发工资总额和实出勤天数总和
                         total_net_salary = department_net_salary.get(department_name, 0.0)
                         total_practical_attendance_days = department_practical_attendance_days.get(
                              department_name, 0)

                         # 计算每个员工的日均工资
                         employee_daily_wages = total_net_salary / total_practical_attendance_days if total_practical_attendance_days > 0 else 0
                         # 计算部门的总日均工资
                         department_daily_wages = employee_daily_wages * department_employee_count[
                              department_name] if \
                              department_employee_count[department_name] > 0 else 0

                         # 计算在职人员平均工资
                         active_employee_count = department_employee_count[department_name]
                         # 添加对 salary_record.is_delete_date 的判断
                         if not salary_record.is_delete_date:
                              average_active_wage = total_net_salary / active_employee_count if active_employee_count > 0 else 0
                         else:
                              average_active_wage = 0  # 如果员工已经离职，将在职人员平均工资设为 0

                         # # 获取在职员工数量
                         # active_employee_count = active_employee_count_by_department.get(department_name, 0)
                         # # 计算在职员工实发工资总额和实际出勤天数总和
                         # active_employee_net_salary = 0.0
                         # active_employee_practical_attendance_days = 0
                         #
                         # for salary_record in monthly_salary_records:
                         #      if not salary_record.is_delete_date and salary_record.practical_attendance_day:
                         #           active_employee_net_salary += salary_record.paid_wages
                         #           active_employee_practical_attendance_days += salary_record.practical_attendance_day
                         #
                         # # 计算在职员工平均日均工资
                         # if total_practical_attendance_days > 0 and active_employee_count > 0:
                         #      average_daily_salary_of_employees = (total_net_salary / total_practical_attendance_days) / active_employee_count
                         # else:
                         #      average_daily_salary_of_employees = 0  # 如果分母为零，将结果

                         # 获取在职员工数量
                         active_employee_count = active_employee_count_by_department.get(department_name, 0)
                         # 计算在职员工实发工资总额和实际出勤天数总和
                         active_employee_net_salary = 0.0
                         active_employee_practical_attendance_days = 0

                         for salary_record in monthly_salary_records:
                              if not salary_record.is_delete_date and salary_record.practical_attendance_day:
                                   active_employee_net_salary += salary_record.paid_wages
                                   active_employee_practical_attendance_days += salary_record.practical_attendance_day
                         print('active_employee_net_salary:', active_employee_net_salary, 'active_employee_practical_attendance_days:', active_employee_practical_attendance_days, 'active_employee_count:', active_employee_count)
                         # 计算在职员工平均日均工资
                         if active_employee_practical_attendance_days > 0 and active_employee_count > 0:
                              average_daily_salary_of_employees = (
                                                                               active_employee_net_salary / active_employee_practical_attendance_days) / active_employee_count
                         else:
                              average_daily_salary_of_employees = 0  # 如果分母为零，将结果设为0

                         date = {
                              'data': month_dt,
                              'department': department_name,
                              'number_of_employees': data['employee_total'],
                              'basic_salary': data['basic_wage'],
                              'overtime_pay': data['overtime_pay'],
                              'bonuse': data['bonus_pay'],
                              'welfare_expenses': data['welfare_expenses'],
                              'social_security_expenditure': data['social_security'],
                              'amount': data['combined'],
                              'average_wage': average_wage,
                              # 'average_daily_wage': department_daily_wages,
                              'average_daily_wage': department_daily_wages / active_employee_count if active_employee_count > 0 else 0,
                              'average_salary_of_employees': average_active_wage,
                              'average_daily_salary_of_employees': average_daily_salary_of_employees,
                              # 'average_daily_salary_of_employees': average_daily_salary_of_employees / active_employee_count if active_employee_count > 0 else 0,
                              'proportion_to_operating_costs': proportion_to_operating_costs,
                         }
                         self.sudo().create(date)
