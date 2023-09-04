from odoo import api, fields, models
from datetime import date, timedelta, datetime
# import json
import itertools


class InheritEffEff(models.Model):
    _inherit = "eff.eff"


    def get_lowest_efficiency_employee(self):

        before_day = fields.Datetime.now().date() - timedelta(days=1)

        lowest_efficiency_list = []
        count_var = 0

        while True:
            count_var = count_var + 1
            objs = self.sudo().search([("date", "=", before_day)], order="group")      # 按组别排序后查询
            if objs or count_var > 5:
            # if objs:
                break
            else:
                before_day = before_day - timedelta(days=1)

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)


            tem_list = []

            for group_obj in group_objs_list:

                if group_obj.employee:
                    
                    tem_list.append({"name": group_obj.employee.name, "efficiency": group_obj.totle_eff})
            
            tem_min_list = min(tem_list, key=lambda x:x['efficiency'])
            tem_min_list["group"] = group

            lowest_efficiency_list.append(tem_min_list)

        return {"data": lowest_efficiency_list, "date": str(before_day)}


    def get_date_of_last_week(self):
        """
        获取上周开始结束日期
        :return: str，date tuple
        """
        today = date.today()
        begin_of_last_week = (today - timedelta(days=today.isoweekday() + 6)).strftime('%Y-%m-%d')
        end_of_last_week = (today - timedelta(days=today.isoweekday())).strftime('%Y-%m-%d')
        # return begin_of_last_week, end_of_last_week
        return  {"begin_date": begin_of_last_week, "end_date": end_of_last_week}


    def get_last_week_data(self):
        # 获取上周开始结束日期
        last_week_date = self.get_date_of_last_week()

        lowest_efficiency_list = []

        objs = self.sudo().search([
            ("date", ">=", last_week_date["begin_date"]),
            ("date", "<=", last_week_date["end_date"]),
            ("employee", "!=", False),
            ], order="group")      # 按组别排序后查询

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_employee_number_list = []

            group_objs_list.sort(key=lambda x: x.employee.name, reverse=False)     # 按员工排序W

            for employee_name, employee_objs in itertools.groupby(group_objs_list, key=lambda x:x.employee.name):     # 再按员工分组
                
                employee_objs_list = list(employee_objs)

                tem_totle_eff = 0      # 临时效率

                for employee_obj in employee_objs_list:
                    tem_totle_eff = tem_totle_eff + employee_obj.totle_eff

                tem_totle_eff = tem_totle_eff / len(employee_objs_list)   # 取平均值
                
                if employee_name:
                    tem_employee_number_list.append({"name": employee_name, "efficiency": tem_totle_eff})

            if tem_employee_number_list:

                min_number_dict = min(tem_employee_number_list, key=lambda x:x['efficiency'])
                min_number_dict["group"] = group

                lowest_efficiency_list.append(min_number_dict)

        return {"data": lowest_efficiency_list, "date": last_week_date}





