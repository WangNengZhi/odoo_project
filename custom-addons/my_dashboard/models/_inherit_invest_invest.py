from odoo import api, fields, models
from datetime import date, timedelta, datetime
# import json
import itertools


class InheritInvestInvest(models.Model):
    _inherit = "invest.invest"


    def get_quality_worst_employee(self):

        before_day = fields.Datetime.now().date() - timedelta(days=1)

        quality_worst_list = []
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

                if group_obj.comment and group_obj.repairs_number:

                    tem_list.append({"name": group_obj.comment, "repairs_number": group_obj.repairs_number})
            
            if tem_list:
            
                tem_max_list = max(tem_list, key=lambda x:x['repairs_number'])
                tem_max_list["group"] = group

                quality_worst_list.append(tem_max_list)


        return {"data": quality_worst_list, "date": str(before_day)}


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

        quality_worst_list = []

        objs = self.sudo().search([
            ("date", ">=", last_week_date["begin_date"]),
            ("date", "<=", last_week_date["end_date"]),
            ("comment", "!=", False)
            ], order="group")      # 按组别排序后查询

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_list = []
            group_objs_list.sort(key=lambda x: x.comment, reverse=False)     # 按员工排序W

            for comment, comment_objs in itertools.groupby(group_objs_list, key=lambda x:x.comment):     # 再按员工分组

                comment_objs_list = list(comment_objs)

                tem_number = 0      # 临时件数

                for comment_obj in comment_objs_list:
                    tem_number = tem_number + comment_obj.repairs_number

                tem_number = tem_number / len(comment_objs_list)   # 取平均值

                if comment:
                    tem_list.append({"name": comment, "repairs_number": tem_number})

            
            tem_max_list = max(tem_list, key=lambda x:x['repairs_number'])
            tem_max_list["group"] = group

            quality_worst_list.append(tem_max_list)


        return {"data": quality_worst_list, "date": last_week_date}
