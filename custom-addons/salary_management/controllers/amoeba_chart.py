from re import I
from odoo import http
import json

from collections import Counter


import datetime
import calendar

class AmoebaChart(http.Controller):


    # 获取当月第一天和最后一天
    def get_begin_and_end(self, date):
        year, month  = date.split('-')
        day = 1
        date_pinjie = year + '-' + month + '-' + str(day)

        #    这就是年月的算法，返回本月天数
        month_math = calendar.monthrange(int(year), int(month))[1]
        #  本月的最大时间
        date_end_of_the_month5 = year + '-' + str(month) + '-' + str(month_math)
        date_end_of_the_month6 = datetime.datetime.strptime(date_end_of_the_month5, '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天
        date_end = datetime.datetime.strptime(date_pinjie, '%Y-%m-%d')      # 当月第一天
        return {"begin": date_end, "end": date_end_of_the_month6}

    # 组别过滤
    def group_name_filter(self, obj):

        filter_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "整件组", "整件一组", "整件车位", "缝纫一组", "缝纫二组", "缝纫三组", "缝纫四组", "缝纫五组", "缝纫六组", "缝纫七组", "缝纫八组", "缝纫九组"]

        if "group" in obj:
            return obj["group"] in filter_list
        elif "first_level_department" in obj:

            return obj["first_level_department"][1] in filter_list

    # 组别对齐
    def group_name_aligning(self, key):

        aligning_dict = {
            "缝纫一组": "1",
            "缝纫二组": "2",
            "缝纫三组": "3",
            "缝纫四组": "4",
            "缝纫五组": "5",
            "缝纫六组": "6",
            "缝纫七组": "7",
            "缝纫八组": "8",
            "缝纫九组": "9",
            "整件车位": "整件一组",
            "整件组": "整件一组"
        }

        if key in aligning_dict:

            return aligning_dict[key]
        else:
            return key


    # 获取车间各组产值和总薪资
    @http.route('/salary_management/get_amoeba_workshop_option_data', auth='public', type='http', methods=['GET'])
    def get_amoeba_workshop_option_data(self, **kw):


        date = kw.get("date")

        begin_and_end = self.get_begin_and_end(date)
        begin_date = begin_and_end["begin"]
        end_date = begin_and_end["end"]

        group_name_list = []

        # 获取产值信息
        pro_pro_objs = http.request.env["pro.pro"].sudo().read_group([
            ("date", ">=", begin_date),
            ("date", "<=", end_date),
        ], fields=['group', 'pro_value'], groupby=['group'])

        pro_pro_objs = filter(self.group_name_filter, pro_pro_objs)
        for pro_pro_obj in pro_pro_objs:

            group_name_list.append({pro_pro_obj["group"]: [pro_pro_obj["pro_value"]]})


        payroll1_objs = http.request.env["payroll1"].sudo().read_group([
            ("date", "=", date),
        ], fields=['first_level_department', 'salary_payable2'], groupby=['first_level_department'])

        if payroll1_objs:
            for payroll1_obj in payroll1_objs:

                hr_department_obj = http.request.env["hr.department"].sudo().browse(int(payroll1_obj["first_level_department"][0]))
                payroll1_obj["first_level_department"] = (payroll1_obj["first_level_department"][0], hr_department_obj.name)

            payroll1_objs = list(filter(self.group_name_filter, payroll1_objs))


            for i in group_name_list:

                for payroll1_obj in payroll1_objs:

                    group_name = self.group_name_aligning(payroll1_obj["first_level_department"][1])

                    if group_name in i:

                        i[group_name].append(payroll1_obj["salary_payable2"])
                        break


            group_list = []
            output_value_list = []
            salary_list = []

            for group_name_obj in group_name_list:

                dict_items = list(group_name_obj.items())

                group_list.append(dict_items[0][0])
                output_value_list.append(dict_items[0][1][0])
                if len(dict_items[0][1]) != 2:
                    pass
                else:
                    salary_list.append(dict_items[0][1][1])

        
            return json.dumps({'status': "1", 'messages': "成功", 'data': {"group_list": group_list, "output_value_list": output_value_list, "salary_list": salary_list}})

        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': {}})



    # 获取后道产值和总薪资
    @http.route('/salary_management/get_amoeba_after_road_data', auth='public', type='http', methods=['GET'])
    def get_amoeba_after_road_data(self, **kw):


        date = kw.get("date")

        begin_and_end = self.get_begin_and_end(date)
        begin_date = begin_and_end["begin"]
        end_date = begin_and_end["end"]

        after_road_objs = http.request.env["posterior_passage_output_value"].sudo().search([
            ("date", ">=", begin_date),
            ("date", "<=", end_date),
        ])

        after_road_value_list = [sum(after_road_objs.mapped('pro_value'))]

        hr_department_obj = http.request.env["hr.department"].sudo().search([("name", "=", "后道部")])
        hr_department_objs_list = http.request.env["hr.department"].sudo().search([("parent_id", "=", hr_department_obj.id)]).ids
        hr_department_objs_list.append(hr_department_obj.id)

        payroll1_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("first_level_department", "in", hr_department_objs_list)
        ])
        salary_list = [sum(payroll1_objs.mapped('salary_payable2'))]


        if payroll1_objs:
            return json.dumps({'status': "1", 'messages': "成功", 'data': {"group_list": ["后道"], "after_road_value_list": after_road_value_list, "salary_list": salary_list}})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': {}})



    # 获取裁床产值和总薪资
    @http.route('/salary_management/get_amoeba_cutting_bed_data', auth='public', type='http', methods=['GET'])
    def get_amoeba_cutting_bed_data(self, **kw):


        date = kw.get("date")

        begin_and_end = self.get_begin_and_end(date)
        begin_date = begin_and_end["begin"]
        end_date = begin_and_end["end"]

        cutting_bed_objs = http.request.env["cutting_bed"].sudo().search([
            ("date", ">=", begin_date),
            ("date", "<=", end_date),
        ])

        cutting_bed_value_list = [sum(cutting_bed_objs.mapped('pro_value'))]

        hr_department_obj = http.request.env["hr.department"].sudo().search([("name", "=", "裁床部")])
        hr_department_objs_list = http.request.env["hr.department"].sudo().search([("parent_id", "=", hr_department_obj.id)]).ids
        hr_department_objs_list.append(hr_department_obj.id)

        payroll1_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("first_level_department", "in", hr_department_objs_list)
        ])
        salary_list = [sum(payroll1_objs.mapped('salary_payable2'))]


        if payroll1_objs:
            return json.dumps({'status': "1", 'messages': "成功", 'data': {"group_list": ["裁床"], "cutting_bed_value_list": cutting_bed_value_list, "salary_list": salary_list}})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': {}})


    # 获取车间总产值和总薪资
    @http.route('/salary_management/get_amoeba_total_workshop_data', auth='public', type='http', methods=['GET'])
    def get_amoeba_total_workshop_data(self, **kw):


        date = kw.get("date")

        begin_and_end = self.get_begin_and_end(date)
        begin_date = begin_and_end["begin"]
        end_date = begin_and_end["end"]

        group_name_list = []

        # 获取产值信息
        pro_pro_objs = http.request.env["pro.pro"].sudo().read_group([
            ("date", ">=", begin_date),
            ("date", "<=", end_date),
        ], fields=['group', 'pro_value'], groupby=['group'])

        pro_pro_objs = list(filter(self.group_name_filter, pro_pro_objs))


        payroll1_objs = http.request.env["payroll1"].sudo().read_group([
            ("date", "=", date),
        ], fields=['first_level_department', 'salary_payable2'], groupby=['first_level_department'])

        if payroll1_objs:
            for payroll1_obj in payroll1_objs:

                hr_department_obj = http.request.env["hr.department"].sudo().browse(int(payroll1_obj["first_level_department"][0]))
                payroll1_obj["first_level_department"] = (payroll1_obj["first_level_department"][0], hr_department_obj.name)

            payroll1_objs = list(filter(self.group_name_filter, payroll1_objs))


        # print(pro_pro_objs)pro_value
        # print(payroll1_objs)salary_payable2
            def total_workshop_value_list(item):
                return item["pro_value"]
            total_workshop_value_list = [sum(map(total_workshop_value_list, pro_pro_objs))]
            def salary_list(item):
                return item["salary_payable2"]
            salary_list = [sum(map(salary_list, payroll1_objs))]

            return json.dumps({'status': "1", 'messages': "成功", 'data': {"group_list": ["车间"], "total_workshop_value_list": total_workshop_value_list, "salary_list": salary_list}})
        else:
            return json.dumps({'status': "0", 'messages': "失败", 'data': {}})