from odoo import api, fields, models
from datetime import date, timedelta, datetime
# import json
import itertools


class InheritGroupStatistical(models.Model):
    _inherit = "group_statistical"




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


    # 获取组返修率
    def get_group_repair_rate(self):


        # 获取上周开始结束日期
        last_week_date = self.get_date_of_last_week()

        ranking_list = []

        objs = self.sudo().search([
            ("dDate", ">=", last_week_date["begin_date"]),
            ("dDate", "<=", last_week_date["end_date"]),
            ], order="group")      # 按组别排序后查询

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_repair_rate = 0   # 临时返修率

            for group_obj in group_objs_list:
                tem_repair_rate = tem_repair_rate + group_obj.repair_ratio

            tem_repair_rate = tem_repair_rate / len(group_objs_list)
            
            ranking_list.append({"group": group, "repair_rate": tem_repair_rate})

        ranking_list.sort(key=lambda x: x["repair_rate"], reverse=True)     # 按产值排序

        return {"data": ranking_list, "date": last_week_date}