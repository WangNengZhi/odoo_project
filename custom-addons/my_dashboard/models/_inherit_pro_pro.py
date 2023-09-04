from odoo import api, fields, models
from datetime import date, timedelta, datetime
# import json
import itertools
from operator import itemgetter


class InheritProPro(models.Model):
    _inherit = "pro.pro"



    def get_date_of_last_week(self):
        """
        获取上周开始结束日期
        """
        today = date.today()
        begin_of_last_week = (today - timedelta(days=today.isoweekday() + 6)).strftime('%Y-%m-%d')
        end_of_last_week = (today - timedelta(days=today.isoweekday())).strftime('%Y-%m-%d')

        return  {"begin_date": begin_of_last_week, "end_date": end_of_last_week}


    def getBetweenDay(self, begin_date, end_date):
        """
        获取指定范围内的每一天
        """
        date_list = []
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += timedelta(days=1)
        return date_list


    # 获取组产值排名
    def get_group_output(self):

        # 获取上周开始结束日期
        last_week_date = self.get_date_of_last_week()

        ranking_list = []

        objs = self.sudo().search([
            ("date", ">=", last_week_date["begin_date"]),
            ("date", "<=", last_week_date["end_date"]),
            ], order="group")      # 按组别排序后查询

        for group, group_objs in itertools.groupby(objs, key=lambda x:x.group):     # 按组别分组

            group_objs_list = list(group_objs)

            tem_pro_value = 0   # 临时产值
            for group_obj in group_objs_list:
                tem_pro_value = tem_pro_value + group_obj.pro_value

            ranking_list.append({"group": group, "pro_value": tem_pro_value})

        ranking_list.sort(key=lambda x: x["pro_value"], reverse=True)     # 按产值排序


        return {"data": ranking_list, "date": last_week_date}

    # 获取组人均产值排名
    def get_group_avg_output(self):

        # 获取上周开始结束日期
        last_week_date = self.get_date_of_last_week()

        date_list = self.getBetweenDay(last_week_date["begin_date"], last_week_date["end_date"])

        tem_dict = {}

        for date_day in date_list:

            objs_list = self.sudo().read_group([
                ("date", "=", date_day),
            ], fields=['group', 'avg_value'], groupby=['group'], orderby="avg_value DESC")


            print(objs_list)

            for objs in objs_list:

                if objs["group"] in tem_dict:

                    tem_dict[objs["group"]].append(objs["avg_value"])
                else:
                    tem_dict[objs["group"]] = []
                    tem_dict[objs["group"]].append(objs["avg_value"])

        data_list = []

        for group in tem_dict:

            data_dict = {}


            # tem_dict[group] = sum(tem_dict[group]) / len(tem_dict[group])
            data_dict["group"] = group
            data_dict["avg_value"] = sum(tem_dict[group]) / len(tem_dict[group])

            data_list.append(data_dict)

        data_list = sorted(data_list, key=itemgetter('avg_value'), reverse=True)

        # print(data_list)
        return {"data": data_list, "date": last_week_date}





