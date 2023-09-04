from odoo import api, fields, models
from datetime import date, timedelta, datetime
# import json
import itertools


class SuspensionSystemStationSummary(models.Model):
    _inherit = "suspension_system_station_summary"

    # 获取最近一天的数据
    def fsn_dashboard_search(self):

        before_day = fields.Datetime.now().date() - timedelta(days=1)

        min_number_list = []
        count_var = 0

        while True:
            count_var = count_var + 1
            objs = self.sudo().search([("dDate", "=", before_day), ("group", "!=", "后整")], order="group")      # 按组别排序后查询
            if objs or count_var > 5:
                break
            else:
                before_day = before_day - timedelta(days=1)

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_employee_number_list = []

            group_objs_list.sort(key=lambda x: x.employee_id, reverse=False)     # 按员工排序

            for employee_id, employee_objs in itertools.groupby(group_objs_list, key=lambda x:x.employee_id):     # 再按员工分组
                
                # print(group.group, employee_id.name, list(employee_objs))
                employee_objs_list = list(employee_objs)

                tem_number = 0      # 临时件数

                for employee_obj in employee_objs_list:
                    tem_number = tem_number + employee_obj.total_quantity
                
                if employee_id:
                    tem_employee_number_list.append({"name": employee_id.name, "number": tem_number})

            min_number_dict = min(tem_employee_number_list, key=lambda x:x['number'])
            min_number_dict["group"] = group.group

            min_number_list.append(min_number_dict)
            
        return {"data": min_number_list, "date": str(before_day)}


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

        objs = self.sudo().search([
            ("dDate", ">=", last_week_date["begin_date"]),
            ("dDate", "<=", last_week_date["end_date"]),
            ("group", "!=", "后整"),
            ("employee_id", "!=", False),
            ], order="group")      # 按组别排序后查询

        min_number_list = []

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_employee_number_list = []
            group_objs_list.sort(key=lambda x: x.employee_id.name, reverse=False)     # 按员工排序W

            for employee_name, employee_objs in itertools.groupby(group_objs_list, key=lambda x:x.employee_id.name):     # 再按员工分组
                
                employee_objs_list = list(employee_objs)

                tem_number = 0      # 临时件数

                for employee_obj in employee_objs_list:
                    tem_number = tem_number + employee_obj.total_quantity

                tem_number = tem_number / len(employee_objs_list)   # 取平均值
                
                if employee_name:
                    tem_employee_number_list.append({"name": employee_name, "number": tem_number})

            if tem_employee_number_list:

                min_number_dict = min(tem_employee_number_list, key=lambda x:x['number'])
                min_number_dict["group"] = group.group

                min_number_list.append(min_number_dict)

        return {"data": min_number_list, "date": last_week_date}
