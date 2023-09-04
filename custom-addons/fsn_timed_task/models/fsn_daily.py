
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from utils import weixin_utils

import calendar
from datetime import timedelta, datetime, date
from functools import reduce
import itertools

from decimal import *

import logging
_logger = logging.getLogger(__name__)

class FsnDaily(models.TransientModel):
    _name = 'fsn_daily'
    _description = 'FSN日报'


    # 计算月的第一天和最后一天
    def compute_start_and_end(self, date_year, date_month):

        last_day = calendar.monthrange(date_year, date_month)[1]        # 最后一天
        start_date = date(date_year, date_month, 1)
        end_date = date(date_year, date_month, last_day)

        return start_date, end_date


    def get_examine_customer_delivery_time_messages(self, today):
        ''' 订单超过计划完成日期'''

        abnormal_list = []
        sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search_read([
            ("date", ">=", "2022-09-01"),
            ("is_finish", "not in", ['已完成', '退单']),
            ("customer_delivery_time", "<", today)
        ], ["date", "order_number", "processing_type", "customer_delivery_time", "attribute", "customer_id"], order='customer_delivery_time desc')
        for sale_pro_obj in sale_pro_objs:

            objs = self.env['schedule_production'].sudo().search_read(
                [("order_number", "=", sale_pro_obj["id"]), ("lock_state", "=", "未审批"), ("state", "!=", "退单")],
                ["quantity_order", "qualified_stock", "defective_number", "quantity_goods", "cutting_number", "no_accomplish_number", "lose_quantity"]
            )

            order_number_value, qualified_stock, defective_good_number, quantity_goods, cutting_number, no_accomplish_number, lose_quantity = \
                reduce(lambda s, x: (s[0]+x["quantity_order"], s[1]+x["qualified_stock"], s[2]+x["defective_number"], s[3]+x["quantity_goods"], s[4]+x["cutting_number"], s[5]+x["no_accomplish_number"], s[6]+x["lose_quantity"]), objs, (0,0,0,0,0,0,0))

            difference = int(qualified_stock - order_number_value)

            if difference < 0:

                abnormal_list.append({
                    "date": sale_pro_obj['date'],
                    "order_number": sale_pro_obj['order_number'],
                    "order_attribute": sale_pro_obj['attribute'][-1] if sale_pro_obj['attribute'] else "未设置",
                    "style_number_base": self.env["sale_pro.sale_pro"].sudo().browse(sale_pro_obj["id"]).sale_pro_line_ids[0].style_number.style_number_base_id.name,
                    "customer_delivery_time": sale_pro_obj['customer_delivery_time'],
                    "processing_type": sale_pro_obj['processing_type'],
                    "order_number_value": order_number_value,
                    "defective_good_number": defective_good_number,
                    "qualified_stock": qualified_stock,
                    "difference": difference,
                    "quantity_goods": quantity_goods,
                    "cutting_number": cutting_number,
                    "no_accomplish_number":no_accomplish_number,
                    "customer_name": sale_pro_obj["customer_id"][-1],
                    "lose_quantity": lose_quantity
                })
        
        return {"date": today, "message_content": abnormal_list}



    def get_dg_average_monthly_production_value(self, today, group_id):
        ''' 获取吊挂月均产值信息'''
        start_date, _ = self.compute_start_and_end(today.year, today.month)

        suspension_system_summary_list = self.env["suspension_system_summary"].read_group(
            [("dDate", ">=", start_date), ("dDate", "<=", today), ("group", "=", group_id)],
            fields=["production_value"],
            groupby=['dDate:day'],
        )
        if suspension_system_summary_list:
            return sum(i["production_value"] for i in suspension_system_summary_list) / len(suspension_system_summary_list)
        else:
            return 0
    

    def get_dg_yesterday_production_value(self, today):
        ''' 获取吊挂昨天总产值'''
        suspension_system_summary_list = self.env["suspension_system_summary"].sudo().read_group(
            [("dDate", "=", today)],
            fields=["group", "production_value", "total_quantity"],
            groupby="group"
        )

        for i in suspension_system_summary_list:
            if i.get("group"):
                if i.get("group")[-1] == "后整":
                    job_ids_list = self.env['hr.job'].sudo().search([("name", "in", ["中查", "现场IE", "后道主管", "流水车位"])]).ids

                    suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                        ("dDate", "=", today), ("group.group", "like", "后整"), ("job_id", "not in", job_ids_list)
                    ])

                    i["people_num"] = len(suspension_system_station_summary_objs.mapped("employee_id"))

                i["dg_month_avg_value"] = self.get_dg_average_monthly_production_value(today, i.get("group")[0])

        return suspension_system_summary_list


    def encapsulation_dg_production_value(self, today):
        ''' 封装吊挂产值信息 '''
        today = today - timedelta(days=1)

        return {
            "date": today,
            # "dg_average_monthly_production_value": self.get_dg_average_monthly_production_value(today),
            "dg_yesterday_production_value": self.get_dg_yesterday_production_value(today)
        }
        

    # 获取日清日毕消息内容
    def get_day_qing_day_bi_messages(self, today):

        group_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "整件一组", "后道", "裁床"]

        that_day = today    # 当天

        def get_before_todays(specify_date, n):
            ''' 获取指定日期之前的n个日期'''

            for _ in range(n):

                specify_date = specify_date - timedelta(days=1)

                yield specify_date


        while True:
            today = today - timedelta(days=1)
            day_qing_day_bi_objs = self.env["day_qing_day_bi"].sudo().read_group(
                [("date", "=", today), ("group", "in", group_list)],
                fields=["group", "plan_number"],
                groupby=['group']
            )
            if any(i["plan_number"] for i in day_qing_day_bi_objs):
                break
        
        todays_lst = list(get_before_todays(today, 3))

        day_qing_day_bi_objs = []


        for day in todays_lst:

            day_qing_day_bi_group_list = self.env["day_qing_day_bi"].sudo().read_group(
                [("date", "=", day), ("group", "in", group_list)],
                fields=["group", "avg_value", "stranded_number", "plan_difference", "deductions", "dg_number", "dg_avg_value", "num_people", "number"],
                groupby=['group']
            )

            for day_qing_day_bi_group_record in day_qing_day_bi_group_list:
                day_qing_day_bi_group_record['date'] = day

            day_qing_day_bi_objs.extend(day_qing_day_bi_group_list)

        for day_qing_day_bi_obj in day_qing_day_bi_objs:
            plan_stage_list = self.env["day_qing_day_bi"].sudo().search([
                ("date", "=", day_qing_day_bi_obj['date']),
                ("group", "=", day_qing_day_bi_obj["group"])
            ]).mapped("plan_stage")

            if "开款第一天" in plan_stage_list:
                day_qing_day_bi_obj["plan_stage"] = "开款第一天"

                
            elif "开款第二天" in plan_stage_list:
                day_qing_day_bi_obj["plan_stage"] = "开款第二天"
            else:
                day_qing_day_bi_obj["plan_stage"] = "正常"

        day_qing_day_bi_objs.sort(key=lambda x: x['group'], reverse=False)

        return {"date": that_day, "message_content": day_qing_day_bi_objs}


    # 获取单件用料表消息内容
    def get_sheet_materials_messages(self, today):

        message_content_list = []

        sale_pro_line_objs = self.env["sale_pro_line"].sudo().search([
            ("sale_pro_id", "!=", False),
            ("style_number", "!=", False),
            ("sale_pro_id.date", "<", today - timedelta(days=1)),
            ("sale_pro_id.date", ">=", "2023-01-01")
        ])

        for sale_pro_line_obj in sale_pro_line_objs:
            if sale_pro_line_obj.style_number_base:
                style_number_prefix = sale_pro_line_obj.style_number.style_number[:4]

                # sheet_materials_obj = self.env["sheet_materials"].sudo().search([("style_number", "=", sale_pro_line_obj.style_number.id)],)
                sheet_materials_obj = self.env["sheet_materials"].sudo().search([("style_number", "like", style_number_prefix + "%"),])
                if not sheet_materials_obj:
                    message_content_list.append({
                        "order_date": sale_pro_line_obj.sale_pro_id.date,
                        "customer_delivery_time": sale_pro_line_obj.sale_pro_id.customer_delivery_time,
                        "order_number": sale_pro_line_obj.sale_pro_id.order_number,
                        "style_number": sale_pro_line_obj.style_number.style_number
                    })

        message_content_list.sort(key=lambda x: x["customer_delivery_time"], reverse=False)
        return {"date": today, "message_content": message_content_list}


    # 获取日清日毕计划设置情况
    def get_plan_set_messages(self, today):

        group_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "裁床", "后道"]

        day_qing_day_bi_objs = self.env["day_qing_day_bi"].sudo().search([
            ("date", "=", today), ("group", "in", group_list), ("plan_stage", "!=", False)
        ], order="group")

        def approval_filter(day_qing_day_bi_obj):

            if day_qing_day_bi_obj.group in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                group_name = f"{day_qing_day_bi_obj.group}组"
            else:
                group_name = day_qing_day_bi_obj.group

            planning_slot_obj = self.env['planning.slot'].sudo().search([
                ("dDate", "=", day_qing_day_bi_obj.date),
                ("staff_group", "=", group_name),
                ("style_number", "=", day_qing_day_bi_obj.style_number.id),
                ("product_size", "=", day_qing_day_bi_obj.product_size.id),
                ("lock_state", "=", "已审批"),
            ])

            return not planning_slot_obj


        day_qing_day_bi_objs = list(filter(approval_filter, day_qing_day_bi_objs))



        if day_qing_day_bi_objs:

            _logger.info(f'{today}获取日清日毕计划设置情况:查询数据成功！')
            group_name_list = []
            for group, group_objs in itertools.groupby(day_qing_day_bi_objs, key=lambda x:x.group):     # 按组别分组

                group_objs_list = list(group_objs)

                num_people_list = []
                plan_stage = ""
                for group_obj in group_objs_list:
                    if group_obj.plan_stage:
                        num_people_list.append(group_obj.num_people)
                    if not plan_stage:
                        plan_stage = group_obj.plan_stage
                    elif plan_stage == "开款第一天":
                        pass
                    elif plan_stage == "正常":
                        if group_obj.plan_stage in ["开款第一天", "开款第二天"]:
                            plan_stage = group_obj.plan_stage
                    elif plan_stage == "开款第二天":
                        if group_obj.plan_stage == "开款第一天":
                            plan_stage = group_obj.plan_stage

                style_number_base_list = []
                group_objs_list.sort(key=lambda x: x.style_number.style_number_base, reverse=True)     # 按款号
                for style_number_base, style_number_base_objs in itertools.groupby(group_objs_list, key=lambda x:x.style_number.style_number_base):     # 按款号分组
                    style_number_base_objs_list = list(style_number_base_objs)

                    style_number_base_list.append({
                        "style_number_base": style_number_base,
                        "plan_value": sum(style_number_base_obj.plan_avg_value for style_number_base_obj in style_number_base_objs_list),
                        "plan_total_value": sum(style_number_base_obj.plan_value for style_number_base_obj in style_number_base_objs_list),
                    })

                group_name_list.append({
                    "group_name": group,    # 组别
                    "num_people": max(num_people_list), # 人数
                    "style_number_base_messages": style_number_base_list,
                    "plan_stage": plan_stage,
                })

            _logger.info('获取日清日毕计划设置情况:数据分组成功！')

            def check_plan_exception(group_name_obj):

                if group_name_obj["group_name"] in ["后道", "裁床"]:
                    total_plan_value = 0
                    for record in group_name_list:
                        if record['group_name'] not in ['裁床', '后道']:
                            total_plan_value += sum(i['plan_total_value'] for i in record['style_number_base_messages'])
                    if group_name_obj["group_name"] == "后道":
                        return sum(i['plan_total_value'] for i in group_name_obj['style_number_base_messages']) < (total_plan_value * 2.0)
                    elif group_name_obj["group_name"] == "裁床":
                        return sum(i['plan_total_value'] for i in group_name_obj['style_number_base_messages']) < (total_plan_value * 1.5)

                else:
                    num_people = group_name_obj["num_people"]
                    if num_people:
                        # 四舍五入
                        per_capita_gdp = round(sum(style_number_base_obj["plan_value"] for style_number_base_obj in group_name_obj["style_number_base_messages"]))

                        if group_name_obj["plan_stage"] == "正常":
                            return per_capita_gdp < 560
                            
                        elif group_name_obj["plan_stage"] == "开款第二天":
                            return per_capita_gdp < 500

                        elif group_name_obj["plan_stage"] == "开款第一天":
                            return  per_capita_gdp < 450


            plan_exception_list = []

            total_plan_value = 0


            # [{'group_name': '2', 'num_people': 8.0, 'style_number_base_messages': [{'style_number_base': '6131', 'plan_value': 4478.5}], 'plan_stage': '正常'}]
            for plan_exception_obj in filter(check_plan_exception, group_name_list):
                
                if plan_exception_obj["group_name"] in ['裁床', '后道']:
                    total_plan_value = 0
                    for record in group_name_list:
                        if record['group_name'] not in ['裁床', '后道']:
                            total_plan_value += sum(i['plan_total_value'] for i in record['style_number_base_messages'])

                    plan_total_value = sum(i['plan_total_value'] for i in plan_exception_obj['style_number_base_messages'])
                    group_plan_total_value = total_plan_value * 1.5
                    
                else:
                    plan_total_value = 0
                    group_plan_total_value = 0
                plan_exception_list.append({
                    "group_name": plan_exception_obj["group_name"],
                    "num_people": plan_exception_obj["num_people"],
                    "style_number_base": "，".join(style_number_base_obj["style_number_base"] for style_number_base_obj in plan_exception_obj["style_number_base_messages"]),
                    "plan_value_sum": format(sum(style_number_base_obj["plan_value"] for style_number_base_obj in plan_exception_obj["style_number_base_messages"]), '0.2f'),
                    "plan_stage": plan_exception_obj["plan_stage"],

                    "plan_total_value": plan_total_value,
                    "group_plan_total_value": group_plan_total_value
                })
            _logger.info('获取日清日毕计划设置情况:数据过滤并组合成功！')
            return  {"date": today, "message_content": plan_exception_list}
        else:

            _logger.info(f'{today}没有查询到当天信息！')


    def cycle_get_plan_set_messages(self, today):
        # 日期减少两天
        today = today - timedelta(days=2)
        all_in_list = []
        while True:

            today_messages = self.get_plan_set_messages(today)
            if today_messages:
                all_in_list.append(today_messages)
            if str(today) == '2022-08-01':

                break

            today = today - timedelta(days=1)

        return all_in_list


    # 获取面辅料入库异常信息
    def get_fabric_exception_info(self, today, table_name):

        fsn_customer_id = self.env["fsn_customer"].sudo().search([("name", "=", "风丝袅")]).id

        plus_material_enter_objs = self.env[table_name].sudo().search([
            ("material_coding", "!=", False),
            "|", ("client_id", "=", False), ("client_id", "=", fsn_customer_id)
        ])
        fabric_exception_list = []
        for plus_material_enter_obj in plus_material_enter_objs:

            if plus_material_enter_obj.material_coding.material_code:

                fabric_ingredients_procurement_obj = self.env["fabric_ingredients_procurement"].sudo().search_read([
                    ("material_code", "=", plus_material_enter_obj.material_coding.material_code.id)
                    ], ["id"])

                if not fabric_ingredients_procurement_obj:
                    fabric_exception_list.append(plus_material_enter_obj.material_coding.material_code.name)

        return {"date": today, "message_content": fabric_exception_list}


    # 获取上一天员工情况信息
    def get_yesterday_employee_situation_info(self, today):
        # 日期减少一天（上一天）
        today = today - timedelta(days=1)
        yesterday_list = self.env["hr.employee"].sudo().search([("is_delete", "=", False), ("entry_time", "<=", "today")])

        # 昨天离职员工列表
        departure_list = [{"name": i.name, "job_name": i.job_id.name} for i in self.env['hr.employee'].sudo().search([("is_delete_date", "=", today)])]

        # 昨天入职员工列表
        induction_list = [{"name": i.name, "job_name": i.job_id.name} for i in self.env['hr.employee'].sudo().search([("entry_time", "=", today)])]

        return {"date": today, "message_content": {"yesterday_list": yesterday_list, "departure_list": departure_list, "induction_list": induction_list}}


    # 获取销售订单计划完成日期
    def get_sales_order_abnormal_plan_date_info(self, today):

        sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search([
            ("date", ">=", "2022-08-01"),
            ("is_finish", "not in", ['已完成', '退单'])
        ], order='customer_delivery_time desc')

        group_transformation_dict = {
            "1": "缝纫一组",
            "2": "缝纫二组",
            "3": "缝纫三组",
            "4": "缝纫四组",
            "5": "缝纫五组",
            "6": "缝纫六组",
            "7": "缝纫七组",
            "8": "缝纫八组",
            "9": "缝纫九组",
            "后道": "后道部",
            "裁床": "裁床部",
            "整件一组": "整件组",
        }
        
        anomaly_list = []
        for sale_pro_obj in sale_pro_objs:

            def add_anomaly_list(real_date):
                return {
                    "date": sale_pro_obj.date,
                    "customer_delivery_time": sale_pro_obj.customer_delivery_time,
                    "order_number": sale_pro_obj.order_number,
                    "planned_completion_date": sale_pro_obj.planned_completion_date,
                    "processing_type": sale_pro_obj.processing_type,
                    "real_date": real_date,
                    "customer_goods_time": sale_pro_obj.customer_delivery_time
                }

            group_name_list = sale_pro_obj.production_group_ids.mapped("name")
            group_name_list = [group_transformation_dict[i] for i in group_name_list if i in group_transformation_dict]
            # 组在职人数
            group_number = self.env["hr.employee"].sudo().search_count([
                ("entry_time", "<=", sale_pro_obj.date),
                "|", ("is_delete_date", ">=", sale_pro_obj.date), ("is_delete", "=", False),
                ("department_id.name", "in", group_name_list)
            ])

            if group_number and sale_pro_obj.date and sale_pro_obj.planned_completion_date:

                number_days = round(((float(sale_pro_obj.order_price) * sum(sale_pro_obj.sale_pro_line_ids.mapped('voucher_count'))) / (560 * group_number)) * 1.3)
                real_date = sale_pro_obj.date + timedelta(days=number_days)

                if sale_pro_obj.planned_completion_date > real_date:
                    anomaly_list.append(add_anomaly_list(real_date))

            else:
                anomaly_list.append(add_anomaly_list("无法获取组人数！"))


        return {"date": today, "message_content": anomaly_list}


    # 获取统计汇总异常信息
    def get_statistical_summary_abnormal_messages_content(self, today):

        abnormal_list = []
        fsn_month_plan_objs = self.env['fsn_month_plan'].sudo().search_read([("production_delivery_time", "<", today)], ['order_number', 'style_number'])

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("order_number", "in", [i['order_number'][0] for i in fsn_month_plan_objs]),
            ("style_number", "in", [i['style_number'][0] for i in fsn_month_plan_objs]),
        ])
        for style_number_summary_obj in style_number_summary_objs:

            def add_info(exception_info, difference, jobs_list):
                abnormal_list.append({
                    "order_number": style_number_summary_obj.order_number.order_number,
                    "style_number": style_number_summary_obj.style_number.style_number,
                    "exception_info": exception_info,
                    "jobs_list": jobs_list,
                    "difference": difference
                })

            # if style_number_summary_obj.cutting_bed < style_number_summary_obj.workshop:
            #     add_info("裁床数小于车间数", style_number_summary_obj.workshop - style_number_summary_obj.cutting_bed, ["裁床主管", "车间主任"])

            # if style_number_summary_obj.workshop < style_number_summary_obj.posterior_passage:
            #     add_info("车间数小于后道数", style_number_summary_obj.posterior_passage - style_number_summary_obj.workshop, ["车间主任", "后道主管"])

            if (style_number_summary_obj.posterior_passage + style_number_summary_obj.defective_good_number) < style_number_summary_obj.enter_warehouse:
                add_info("后道+报次数小于入库数", style_number_summary_obj.enter_warehouse - (style_number_summary_obj.posterior_passage + style_number_summary_obj.defective_good_number), ["后道主管", "成衣主管"])
            
            # if style_number_summary_obj.enter_warehouse < style_number_summary_obj.out_of_warehouse:
            #     add_info("入库数小于出库数", style_number_summary_obj.out_of_warehouse - style_number_summary_obj.enter_warehouse, ["成衣主管"])
            
            if style_number_summary_obj.enter_warehouse > style_number_summary_obj.cutting_bed:
                add_info(f"入库数大于裁床数", style_number_summary_obj.enter_warehouse - style_number_summary_obj.cutting_bed, ["成衣主管", "裁床主管"])
            
        return {"date": today, "message_content": abnormal_list}


    # 获取面辅料采购后七天没有仓库入库的记录
    def get_fabric_procurement(self, today):

        fabric_ingredients_procurement_objs = self.env["fabric_ingredients_procurement"].sudo().search([
            ("state", "=", "待采购"),
            ("material_code", "!=", False),
        ])

        return {"date": today, "message_content": [i.material_code.name for i in fabric_ingredients_procurement_objs if (i.date + timedelta(days=3)) < today]}

    # 获取两个日期间的所有日期 
    def getEveryDay(self, begin_date, end_date): 
        date_list = [] 
        while begin_date <= end_date: 
            date_list.append(begin_date) 
            begin_date += timedelta(days=1) 
        return date_list

    # 获取月计划异常信息
    def get_monthly_plan_abnormal_messages_content(self, today):
        
        fsn_month_plan_objs = self.env["fsn_month_plan"].sudo().search([], order='customer_delivery_time desc')

        monthly_plan_abnormal_list = []

        for fsn_month_plan_obj in fsn_month_plan_objs:

            def add_monthly_plan_abnormal_list(real_date):
                return {
                    "order_date": fsn_month_plan_obj.order_number_date,
                    "customer_delivery_time": fsn_month_plan_obj.customer_delivery_time,
                    "order_number": fsn_month_plan_obj.order_number.order_number,
                    "style_number": fsn_month_plan_obj.style_number.style_number,
                    "plan_online_date": fsn_month_plan_obj.plan_online_date,
                    "production_delivery_time": fsn_month_plan_obj.production_delivery_time,
                    "real_date": real_date
                }

            if fsn_month_plan_obj.people_number:
                number_days = ((float(fsn_month_plan_obj.order_number.order_price) * fsn_month_plan_obj.plan_number) / (560 * fsn_month_plan_obj.people_number)) * 1.3
                number_days = int(number_days + 1)

                real_date = fsn_month_plan_obj.plan_online_date + timedelta(days=number_days)

                for every_day in self.getEveryDay(fsn_month_plan_obj.plan_online_date, real_date):
                    if every_day.isoweekday() == 7:
                        real_date += timedelta(days=1)

                if fsn_month_plan_obj.production_delivery_time > real_date:
                    monthly_plan_abnormal_list.append(add_monthly_plan_abnormal_list(real_date))
            else:
                monthly_plan_abnormal_list.append(add_monthly_plan_abnormal_list("无法获取组人数！"))

        return {"date": today, "message_content": monthly_plan_abnormal_list}



    # 获取产前准备计划物料异常
    def get_raw_materials_order_abnormal_info(self, today):
        
        abnormal_list = []

        sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search([
            ("processing_type", "!=", "返修"),
            ("is_finish", "!=", "退单"),
            ("date", ">=", "2022-09-01"),
            ("date", "<=", today - timedelta(days=2))
        ], order="customer_delivery_time desc")
        

        for sale_pro_obj in sale_pro_objs:

            temp_dict = {"order_number_date": sale_pro_obj.date, "customer_delivery_time": sale_pro_obj.customer_delivery_time}
            
            if sale_pro_obj.raw_materials_order_id:
                if not all(sale_pro_obj.raw_materials_order_id.mapped("total_amount")) and not any(i == "退单" for i in sale_pro_obj.sale_pro_line_ids.mapped("state")):
                    temp_dict.update({"order_number": sale_pro_obj.order_number, "cause": "总用量存在异常！"})
                else:
                    continue
            else:
                
                temp_dict.update({"order_number": sale_pro_obj.order_number, "cause": "无记录！"})

            abnormal_list.append(temp_dict)
        
        
        return {"date": today, "message_content": abnormal_list}

        """ for sale_pro_obj in sale_pro_objs:

            temp_dict = {"order_number_date": sale_pro_obj.date, "customer_delivery_time": sale_pro_obj.customer_delivery_time}
            
            if sale_pro_obj.raw_materials_order_id:
                if not all(sale_pro_obj.raw_materials_order_id.mapped("total_amount")):
                    temp_dict.update({"order_number": sale_pro_obj.order_number, "cause": "总用量存在异常！"})
                else:
                    continue
            else:
                
                temp_dict.update({"order_number": sale_pro_obj.order_number, "cause": "无记录！"})

            abnormal_list.append(temp_dict)
        
        
        return {"date": today, "message_content": abnormal_list} """

    # 获取销售订单外发没有创建外发订单的
    def get_outbound_order_abnormal_info(self, today):

        abnormal_list = []

        sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search([("processing_type", "=", "外发"), ("is_finish", "!=", "退单")], order="customer_delivery_time desc")
        order_ids_list = self.env["outsource_order"].sudo().search([]).mapped('order_id.id')

        for sale_pro_obj in sale_pro_objs:
            if sale_pro_obj.id not in order_ids_list:
                abnormal_list.append({"order_number_date": sale_pro_obj.date, "order_number": sale_pro_obj.order_number, "customer_delivery_time": sale_pro_obj.customer_delivery_time})

        return {"date": today, "message_content": abnormal_list}


    # 获取物料汇总数据异常的
    def get_material_summary_sheet_abnormal_info(self, today):

        material_summary_sheet_objs = self.env["material_summary_sheet"].sudo().search_read([("date_contract", "!=", False), ('state', '=', '未确认')], ['order_id', 'style_number', 'material_name', 'actual_dosage', 'inventory_dosage', 'outbound_dosage', 'return_goods_dosage'])
        # 库存量 + 出库量 - 退回量 != 实际用量
        abnormal_list = [{"order_id": i['order_id'][-1], "order_obj_id": i['order_id'][0], "style_number": i['style_number'][-1], "material_name": i['material_name']} for i in material_summary_sheet_objs if Decimal(str(i['actual_dosage'])) != Decimal(str(i['inventory_dosage'])) + Decimal(str(i['outbound_dosage'])) - Decimal(str(i['return_goods_dosage']))]

        for abnormal in abnormal_list:
            sale_pro_obj = self.env['sale_pro.sale_pro'].sudo().browse(abnormal['order_obj_id'])
            abnormal['order_number_date'] = sale_pro_obj.date
            abnormal['customer_delivery_time'] = sale_pro_obj.customer_delivery_time
        abnormal_list.sort(key=lambda x: x['customer_delivery_time'], reverse=False)

        return {"date": today, "message_content": abnormal_list}


    # 获取月计划上线日期前一天面辅料齐备异常的
    def get_monthly_plan_material_ready_abnormal_info(self, today):
        # 日期增加一天（下一天）
        query_date = today + timedelta(days=1)
        fsn_month_plan_list = self.env["fsn_month_plan"].sudo().search_read([("plan_online_date", "<=", query_date)], ['order_number'])
        order_number_id_list = [i['order_number'][0] for i in fsn_month_plan_list]

        abnormal_list = self.env['fabric_ingredients_procurement'].sudo().search_read(
            [("order_id", "in", order_number_id_list), ("state", "!=", "已采购")],
            ['order_id', 'style_number', 'material_code', 'material_name']
        )
        for abnormal in abnormal_list:
            sale_pro_obj = self.env['sale_pro.sale_pro'].sudo().browse(abnormal['order_id'][0])
            abnormal['order_number_date'] = sale_pro_obj.date
            abnormal['customer_delivery_time'] = sale_pro_obj.customer_delivery_time

        abnormal_list.sort(key=lambda x: x['customer_delivery_time'], reverse=False)

        return {"date": today, "message_content": abnormal_list}


    # 获取月计划上线日期前一天裁床产量异常的
    def get_monthly_plan_cutting_bed_production_abnormal_info(self, today):
        # 日期增加一天（下一天）
        query_date = today + timedelta(days=1)
        fsn_month_plan_info_list = self.env["fsn_month_plan"].sudo().search_read(
            [("plan_online_date", "<=", query_date), ("order_number.processing_type", "!=", "返修"), ("is_external_clipping", "=", False), ("lock_state", "=", "未审批")],
            ['order_number_date', 'customer_delivery_time', 'order_number', 'style_number', 'plan_number', 'processing_type'], order="customer_delivery_time desc")

        abnormal_list = []

        for fsn_month_plan_info in fsn_month_plan_info_list:

            cutting_bed_production_list = self.env["cutting_bed_production"].sudo().search_read(
                [("order_number", "=", fsn_month_plan_info['order_number'][0]), ("style_number", "=", fsn_month_plan_info['style_number'][0])],
                ['complete_productionp', 'lock_state']
            )

            if not all(i['lock_state'] == "已审批" for i in cutting_bed_production_list):

                cutting_bed_production = sum(i['complete_productionp'] for i in cutting_bed_production_list)

                sale_pro_line_obj = self.env['sale_pro_line'].sudo().search([("sale_pro_id", "=", fsn_month_plan_info['order_number'][0]), ("style_number", "=", fsn_month_plan_info['style_number'][0])])

                if cutting_bed_production < fsn_month_plan_info['plan_number']:

                    abnormal_list.append({
                        "order_date": fsn_month_plan_info['order_number_date'],
                        "order_number": fsn_month_plan_info['order_number'][-1],
                        "contract_date": fsn_month_plan_info['customer_delivery_time'],
                        "style_number": fsn_month_plan_info['style_number'][-1],
                        "order_quantity": sale_pro_line_obj.voucher_count,
                        "plan_number": fsn_month_plan_info['plan_number'],
                        "cutting_bed_production": cutting_bed_production,
                        "processing_type": fsn_month_plan_info['processing_type']
                    })
                
        return {"date": today, "message_content": abnormal_list}


    # 获取销售订单创建后第二天没有月计划的记录
    def get_sales_order_no_month_plan(self, today):

        sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search([("date", ">=", "2022-10-01"), ("date", "<=", today - timedelta(days=1))])
        abnormal_list = []

        for sale_pro_obj in sale_pro_objs:
            for sale_pro_line in sale_pro_obj.sale_pro_line_ids:
                if sale_pro_line.state != "退单":
                    if not self.env["fsn_month_plan"].sudo().search([("order_number", "=", sale_pro_obj.id), ("style_number", "=", sale_pro_line.style_number.id)]):

                        abnormal_list.append({"order_number": sale_pro_obj.order_number, "style_number": sale_pro_line.style_number.style_number, "cause": "无月计划！"})


        return {"date": today, "message_content": abnormal_list}


    # B2B展厅退货和返修模块客仓对比
    def get_b2b_return_and_client_ware(self, today):

        abnormal_list = []
        # b2b_return_data_list = self.env['b2b_return'].sudo().search_read(
        #     [("quality", "=", "次品")],
        #     ["date", "style_number", "number", "quality"]
        # )

        # b2b_return_data_list.sort(key=lambda x: (x["style_number"][0]), reverse=False)     # 按款号排序
        # for (style_number_id, quality), b2b_return_data_list_objs in itertools.groupby(b2b_return_data_list, key=lambda x:(x["style_number"][0], x['quality'])):     # 再款号分组

        #     number = sum(i['number'] for i in b2b_return_data_list_objs)
            
        #     client_ware_client_ware_list = self.env['client_ware'].sudo().search([
        #         ("check_type", "=", "客户"),
        #         ("style_number", "=", style_number_id),
        #     ]).mapped("repair_number")
        #     cangkujianshu = sum(client_ware_client_ware_list)

        #     if number != cangkujianshu:
        #         abnormal_list.append({
        #             "style_number": self.env["ib.detail"].sudo().browse(style_number_id).style_number,
        #             "number": number,
        #             "quality": quality,
        #             "cangkujianshu": cangkujianshu
        #         })

        return {"date": today, "message_content": abnormal_list}



    # B2B展厅退货和仓库入库对比
    def get_b2b_return_and_finished_product_ware(self, today):
        abnormal_list = []
        # b2b_return_data_list = self.env['b2b_return'].sudo().search_read(
        #     domain=[("quality", "=", "次品")],
        #     fields=["date", "style_number", "number", "quality"],
        # )

        # b2b_return_data_list.sort(key=lambda x: x["style_number"][0], reverse=False)     # 按款号排序
        # for style_number_id, b2b_return_data_list_objs in itertools.groupby(b2b_return_data_list, key=lambda x:x["style_number"][0]):     # 再款号分组

        #     style_number_list = list(b2b_return_data_list_objs)
        #     style_number_list.sort(key=lambda x: x["quality"], reverse=False)     # 按质量排序

        #     for quality, style_number_list_objs in itertools.groupby(style_number_list, key=lambda x:x["quality"]):     # 再质量分组

        #         number = sum(i['number'] for i in style_number_list_objs)

        #         finished_product_ware_line_number_list = self.env["finished_product_ware_line"].sudo().search([
        #             ("type", "=", "入库"),
        #             ("style_number", "=", style_number_id),
        #             ("quality", "=", quality),
        #             ("character", "=", "退货")
        #         ]).mapped("number")
                    
        #         cangkujianshu = sum(finished_product_ware_line_number_list)

        #         if number != cangkujianshu:
        #             abnormal_list.append({
        #                 "style_number": self.env["ib.detail"].sudo().browse(style_number_id).style_number,
        #                 "number": number,
        #                 "quality": quality,
        #                 "cangkujianshu": cangkujianshu
        #             })

        return {"date": today, "message_content": abnormal_list}


    # 销售售后退货和仓库入库对比
    def get_fsn_sales_return_and_finished_product_ware(self, today):

        abnormal_list = []
        fsn_sales_return_objs = self.env['fsn_sales_return'].sudo().search_read(
            [("quality", "=", "次品")],
            ["date", "order_id", "style_number", "number", "quality"]
        )
        fsn_sales_return_objs.sort(key=lambda x: x["order_id"][0], reverse=False)     # 按订单号排序
        for order_id, order_id_objs in itertools.groupby(fsn_sales_return_objs, key=lambda x: x["order_id"][0]):     # 再订单号分组
            order_id_objs_list = list(order_id_objs)

            order_id_objs_list.sort(key=lambda x: x["style_number"][0], reverse=False)     # 按款号排序
            for style_number_id, style_number_objs in itertools.groupby(order_id_objs_list, key=lambda x:x["style_number"][0]):     # 再款号分组

                style_number_objs_list = list(style_number_objs)
                style_number_objs_list.sort(key=lambda x: x["quality"], reverse=False)     # 按质量排序

                for quality, quality_objs in itertools.groupby(style_number_objs_list, key=lambda x:x["quality"]):     # 再质量分组


                    number = sum(i['number'] for i in quality_objs)
         
                    finished_product_ware_line_number_list = self.env["finished_product_ware_line"].sudo().search([
                        ("type", "=", "入库"),
                        ("order_number", "=", order_id),
                        ("style_number", "=", style_number_id),
                        ("quality", "=", quality),
                        ("character", "=", "返修")
                    ]).mapped("number")


                    cangkujianshu = sum(finished_product_ware_line_number_list)

                    if number != cangkujianshu:

                        abnormal_list.append({
                            "order_id": self.env["sale_pro.sale_pro"].sudo().browse(order_id).order_number,
                            "style_number": self.env["ib.detail"].sudo().browse(style_number_id).style_number,
                            "number": number,
                            "quality": quality,
                            "cangkujianshu": cangkujianshu
                        })

        
        return {"date": today, "message_content": abnormal_list}


    # 销售售后退货和B2B展厅退货
    def after_sales_return_goods(self, today):
        abnormal_list = []
        # yesterday = today - timedelta(days=1)
        # fsn_sales_return_objs = self.env['fsn_sales_return'].sudo().search([("create_date", ">=", yesterday), ("create_date", "<=", today)])

        # for fsn_sales_return_obj in fsn_sales_return_objs:
        #     abnormal_list.append({
        #         "type": "销售售后退货",
        #         "customer_name": fsn_sales_return_obj.customer_id.name,
        #         "style_number": fsn_sales_return_obj.style_number.style_number,
        #         "number": fsn_sales_return_obj.number,
        #         "quality": fsn_sales_return_obj.quality
        #     })

        
        # b2b_return_objs = self.env['b2b_return'].sudo().search([("date", "=", today)])
        # for b2b_return_obj in b2b_return_objs:
        #     abnormal_list.append({
        #         "type": "B2B展厅退货",
        #         "customer_name": b2b_return_obj.customer_name,
        #         "style_number": b2b_return_obj.style_number.style_number,
        #         "number": b2b_return_obj.number,
        #         "quality": b2b_return_obj.quality
        #     })

        return {"date": today, "message_content": abnormal_list}


    # 产前准备人工核算和面辅料出库对比
    def get_production_drop_documents_warehouse(self, today):
        
        production_drop_documents_objs = self.env['production_drop_documents'].sudo().search([("order_number.is_finish", "=", "已完成")])

        abnormal_list = []

        for production_drop_documents_obj in production_drop_documents_objs:
            for production_drop_documents_material_line_obj in production_drop_documents_obj.production_drop_documents_material_line_ids:
                if production_drop_documents_material_line_obj.type == "面料":
                    
                    plus_material_outbound_number_list = self.env['plus_material_outbound'].sudo().search([
                        ("order_id", "=", production_drop_documents_obj.order_number.id),
                        ("style_number", "=", production_drop_documents_obj.style_number.id),
                        ("material_name", "=", production_drop_documents_material_line_obj.material_id.material_name)
                    ]).mapped("amount")

                    cangkshuliang = sum(plus_material_outbound_number_list)

                    if production_drop_documents_material_line_obj.planned_dosage != cangkshuliang:
                        abnormal_list.append({
                            "type": production_drop_documents_material_line_obj.type,
                            "order_id": production_drop_documents_obj.order_number.order_number,
                            "style_number": production_drop_documents_obj.style_number.style_number,
                            "material_name": production_drop_documents_material_line_obj.material_id.material_name,
                            "planned_dosage": production_drop_documents_material_line_obj.planned_dosage,
                            "cangkshuliang": cangkshuliang
                        })
                
                else:

                    warehouse_bom_outbound_number_list = self.env['warehouse_bom_outbound'].sudo().search([
                        ("order_id", "=", production_drop_documents_obj.order_number.id),
                        ("style_number", "=", production_drop_documents_obj.style_number.id),
                        ("material_name", "=", production_drop_documents_material_line_obj.material_id.material_name)
                    ]).mapped("amount")

                    cangkshuliang = sum(warehouse_bom_outbound_number_list)

                    if production_drop_documents_material_line_obj.planned_dosage != cangkshuliang:
                        abnormal_list.append({
                            "type": production_drop_documents_material_line_obj.type,
                            "order_id": production_drop_documents_obj.order_number.order_number,
                            "style_number": production_drop_documents_obj.style_number.style_number,
                            "material_name": production_drop_documents_material_line_obj.material_id.material_name,
                            "planned_dosage": production_drop_documents_material_line_obj.planned_dosage,
                            "cangkshuliang": cangkshuliang
                        })

        return {"date": today, "message_content": abnormal_list}



    def get_schedule_production_abnormal_info(self, today):
        ''' 获取生产进度表裁床数和存量不符记录'''
        schedule_production_objs = self.env['schedule_production'].sudo().search_read(
            [("date_order", ">=", "2022-09-01"), ("lock_state", "=", "未审批"), ("date_contract", "<", today), ("state", "!=", "退单")],
            ["date_order", "date_contract", "processing_type", "order_number", "style_number", "size", "quantity_order", "quantity_cutting", "quality_department_inventory", "quantity_delivery", "qualified_stock", "defective_number", "cutting_number", "no_accomplish_number"],
            order='date_contract desc'
        )
        print('内容:', schedule_production_objs)
        abnormal_list = []

        for i in schedule_production_objs:

            # 如果外部裁剪就跳过
            if not self.env['fsn_month_plan'].sudo().search([("order_number", "=", i['order_number'][0]),("style_number", "=", i['style_number'][0]),("is_external_clipping", "=", True)]):

                if i['quantity_cutting']:
                    if i["quantity_cutting"] != i["qualified_stock"]:
                        
                        abnormal_list.append({
                            "date_order": i['date_order'],
                            "date_contract": i['date_contract'],
                            "order_number": i['order_number'][-1],
                            "processing_type": i['processing_type'],
                            "style_number": i['style_number'][-1],
                            "size": i['size'][-1],
                            "quantity_order": i['quantity_order'],
                            "quantity_cutting": i["quantity_cutting"],
                            "warehouse": i["qualified_stock"],
                            "defective_number": i['defective_number'],
                            "cutting_number": i['cutting_number'],
                            "no_accomplish_number": i['no_accomplish_number'],
                        })

                else:
                    if i['quantity_order'] != i["qualified_stock"]:

                        abnormal_list.append({
                            "date_order": i['date_order'],
                            "date_contract": i['date_contract'],
                            "order_number": i['order_number'][-1],
                            "processing_type": i['processing_type'],
                            "style_number": i['style_number'][-1],
                            "size": i['size'][-1],
                            "quantity_order": i['quantity_order'],
                            "quantity_cutting": i["quantity_cutting"],
                            "warehouse": i["qualified_stock"],
                            "defective_number": i['defective_number'],
                            "cutting_number": i['cutting_number'],
                            "no_accomplish_number": i['no_accomplish_number'],
                        })


        return {"date": today, "message_content": abnormal_list}

    # 中查日清日毕
    def middle_check_day_qing_day_bi_info(self, today):

        today = today - timedelta(days=1)
        abnormal_list = []

        check_position_settings_objs = self.env['check_position_settings'].sudo().search([("department_id", "=", "车间")])
        for check_position_settings_obj in check_position_settings_objs:
            station_list = check_position_settings_obj.position_line_ids.filtered(lambda x: x.type == "中查").mapped("position")
            if len(station_list) == 1:
                dg_record_objs = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", "=", today),
                    ("group", "=", check_position_settings_obj.id),
                    ("station_number", "=", station_list[0]),
                ])

                if dg_record_objs:

                    dg_record_objs = list(dg_record_objs)
                    dg_record_objs.sort(key=lambda x: x.MONo, reverse=False)     # 按款号排序
                    for style, dg_style_objs in itertools.groupby(dg_record_objs, key=lambda x:x.MONo):     # 按款号分组
                        dg_style_objs_list = list(dg_style_objs)

                        for dg_style_record in dg_style_objs_list:
                            process_record_list = list(dg_style_record.line_lds)
                            process_record_list.sort(key=lambda x: x.SeqNo, reverse=False)
                            # process_record_list[0].SeqNo, process_record_list[0].number

                            last_process_record = self.env['station_summaryseqno_line'].sudo().search([
                                ("seqno_id.dDate", "=", today),
                                ("seqno_id.MONo", "=", dg_style_record.MONo),
                                ("SeqNo", "=", process_record_list[0].SeqNo-1),
                            ])

                            if last_process_record:

                                if process_record_list[0].number < last_process_record[0].number:
                                    abnormal_list.append({
                                        "date": today,
                                        "group": dg_style_record.group.group,
                                        "style_number": dg_style_record.MONo,
                                        "middle_check_number": process_record_list[0].number,
                                        "last_process_number": last_process_record[0].number
                                    })
                            

        return {"date": today, "message_content": abnormal_list}


    # 发送日报
    def send_fsn_daily(self, today=None, message_group=False, send_out_group=False, after_the_road=False, internal_message_type="all"):
        if not today:
            today = fields.Date.today()
        message_content = {}
        # 获取检查客户货期消息内容
        examine_customer_delivery_time_message_content = self.get_examine_customer_delivery_time_messages(today)
        message_content["examine_customer_delivery_time_message_content"] = examine_customer_delivery_time_message_content
        _logger.info("获取检查客户货期消息内容成功！")

        # 获取吊挂产值信息
        encapsulation_dg_production_value_message_content = self.encapsulation_dg_production_value(today)
        message_content["encapsulation_dg_production_value_message_content"] = encapsulation_dg_production_value_message_content
        _logger.info("获取吊挂产值信息内容成功！")

        # 获取日期日毕消息内容
        day_qing_day_bi_messages_content = self.get_day_qing_day_bi_messages(today)
        message_content["day_qing_day_bi_messages_content"] = day_qing_day_bi_messages_content
        _logger.info("获取日清日毕消息内容成功！")

        # 获取销售订单中的订单明细中的款，没有单件用料表的
        sheet_materials_messages_content = self.get_sheet_materials_messages(today)
        message_content["sheet_materials_messages_content"] = sheet_materials_messages_content
        _logger.info('获取销售订单中的订单明细中的款，没有单件用料表的成功！')

        # 获取日清日毕计划设置情况
        # plan_set_messages_messages_content = self.cycle_get_plan_set_messages(today)
        # message_content["plan_set_messages_messages_content"] = plan_set_messages_messages_content
        # _logger.info('获取日清日毕计划设置情况成功！')

        # 日计划异常
        day_plan_abnormal_info_content = self.get_day_plan_abnormal_info(today)
        message_content["day_plan_abnormal_info_content"] = day_plan_abnormal_info_content
        _logger.info('获取日清日毕计划设置情况成功！')


        # 获取面料入库异常信息
        fabric_exception_messages_content = self.get_fabric_exception_info(today, "plus_material_enter")
        message_content["fabric_exception_messages_content"] = fabric_exception_messages_content
        _logger.info('获取面料入库异常信息成功！')

        # 取辅料入库异常信息
        supplementary_material_messages_content = self.get_fabric_exception_info(today, "warehouse_bom")
        message_content["supplementary_material_messages_content"] = supplementary_material_messages_content
        _logger.info('获取辅料入库异常信息成功！')

        # 获取上一天员工情况信息
        yesterday_employee_situation_messages_content = self.get_yesterday_employee_situation_info(today)
        message_content["yesterday_employee_situation_messages_content"] = yesterday_employee_situation_messages_content
        _logger.info('获取上一天员工情况信息成功！')

        # 获取销售订单计划完成日期
        sales_order_abnormal_plan_date_messages_content = self.get_sales_order_abnormal_plan_date_info(today)
        message_content["sales_order_abnormal_plan_date_messages_content"] = sales_order_abnormal_plan_date_messages_content
        _logger.info('获取销售订单计划完成日期成功！')

        # 获取统计汇总异常信息
        # statistical_summary_abnormal_messages_content = self.get_statistical_summary_abnormal_messages_content(today)
        # message_content["statistical_summary_abnormal_messages_content"] = statistical_summary_abnormal_messages_content
        # _logger.info('获取统计汇总异常信息成功！')

        # 获取面辅料采购后两天没有仓库入库的记录
        fabric_procurement_messages_content = self.get_fabric_procurement(today)
        message_content["fabric_procurement_messages_content"] = fabric_procurement_messages_content
        _logger.info('获取面辅料采购后两天没有仓库入库的记录成功！')

        # 获取月计划异常信息
        monthly_plan_abnormal_messages_content = self.get_monthly_plan_abnormal_messages_content(today)
        message_content["monthly_plan_abnormal_messages_content"] = monthly_plan_abnormal_messages_content
        _logger.info('获取获取月计划异常信息成功！')

        # 获取产前准备计划物料异常
        raw_materials_order_abnormal_info = self.get_raw_materials_order_abnormal_info(today)
        message_content["raw_materials_order_abnormal_info"] = raw_materials_order_abnormal_info
        _logger.info('获取产前准备计划物料异常成功！!')

        # 获取销售订单外发没有创建外发订单的
        outbound_order_abnormal_info = self.get_outbound_order_abnormal_info(today)
        message_content["outbound_order_abnormal_info"] = outbound_order_abnormal_info
        _logger.info('获取销售订单外发没有创建外发订单的成功!')

        # 获取物料汇总数据异常的
        material_summary_sheet_abnormal_info = self.get_material_summary_sheet_abnormal_info(today)
        message_content["material_summary_sheet_abnormal_info"] = material_summary_sheet_abnormal_info
        _logger.info('获取物料汇总数据异常的记录成功！')

        # 获取月计划上线日期前一天面辅料齐备异常的
        monthly_plan_material_ready_abnormal_info = self.get_monthly_plan_material_ready_abnormal_info(today)
        message_content["monthly_plan_material_ready_abnormal_info"] = monthly_plan_material_ready_abnormal_info
        _logger.info('获取月计划上线日期前一天面辅料齐备异常的记录成功！')

        # 获取月计划上线日期前一天裁床产量异常的
        monthly_plan_cutting_bed_production_abnormal_info = self.get_monthly_plan_cutting_bed_production_abnormal_info(today)
        message_content["monthly_plan_cutting_bed_production_abnormal_info"] = monthly_plan_cutting_bed_production_abnormal_info
        _logger.info('获取月计划上线日期前一天裁床产量异常的的记录成功！')

        # 获取销售订单创建后第二天没有月计划的记录
        sales_order_no_month_plan_abnormal_info = self.get_sales_order_no_month_plan(today)
        message_content["sales_order_no_month_plan_abnormal_info"] = sales_order_no_month_plan_abnormal_info
        _logger.info('获取销售订单创建后第二天没有月计划的记录成功！')

        # B2B展厅退货和返修模块客仓对比
        b2b_return_and_client_ware_abnormal_info = self.get_b2b_return_and_client_ware(today)
        message_content["b2b_return_and_client_ware_abnormal_info"] = b2b_return_and_client_ware_abnormal_info
        _logger.info('获取B2B展厅退货和返修模块客仓对比记录成功！')

        # B2B展厅退货和仓库入库对比
        b2b_return_and_finished_product_ware_info = self.get_b2b_return_and_finished_product_ware(today)
        message_content["b2b_return_and_finished_product_ware_info"] = b2b_return_and_finished_product_ware_info
        _logger.info('获取B2B展厅退货和仓库入库对比记录成功！')

        # 销售售后退货和仓库入库对比异常
        fsn_sales_return_and_finished_product_ware_info = self.get_fsn_sales_return_and_finished_product_ware(today)
        message_content["fsn_sales_return_and_finished_product_ware_info"] = fsn_sales_return_and_finished_product_ware_info
        _logger.info('获取销售售后退货和仓库入库对比异常记录成功！')

        # 销售售后退货和B2B展厅退货
        after_sales_return_goods_info = self.after_sales_return_goods(today)
        message_content["after_sales_return_goods_info"] = after_sales_return_goods_info
        _logger.info('获取销售售后退货和B2B展厅退货记录成功！')

        # 产前准备人工核算和面辅料出库对比
        production_drop_documents_warehouse_info = self.get_production_drop_documents_warehouse(today)
        message_content["production_drop_documents_warehouse_info"] = production_drop_documents_warehouse_info
        _logger.info('获取产前准备人工核算和面辅料出库对比异常记录成功！')


        # 获取生产进度表裁床数和仓库不符记录
        schedule_production_abnormal_info = self.get_schedule_production_abnormal_info(today)
        message_content["schedule_production_abnormal_info"] = schedule_production_abnormal_info
        _logger.info('获取生产进度表裁床数和仓库不符记录成功！')

        # 中查日清日毕异常
        middle_check_day_qing_day_bi_info = self.middle_check_day_qing_day_bi_info(today)
        message_content["middle_check_day_qing_day_bi_info"] = middle_check_day_qing_day_bi_info
        _logger.info('获取中查日清日毕业异常记录成功！')

        # 外发误期
        message_content["outsource_order_delay_time_info"] = self.set_outsource_order_delay_time_info(today)
        _logger.info('获取外发异常记录成功！')

        # 客仓客户退货信息
        message_content["client_ware_customer_return_info"] = self.get_client_ware_customer_return_info(today)
        _logger.info('获取客仓客户退货记录成功！')

        message_content["recruitment_info"] = self.set_recruitment_info(today)
        _logger.info('获取招聘信息成功！')

        message_content["general_inspection_abnormal_info"] = self.get_general_inspection_abnormal_info(today)
        _logger.info('获取总检异常信息成功！')

        message_content["prenatal_preparation_progress_anomaly_info"] = self.get_prenatal_preparation_progress_anomaly_info(today)
        _logger.info('获取总检异常信息成功！')

        message_content["time_limit_not_recruitment_record"] = self.get_time_limit_not_recruitment_record(today)
        _logger.info('获取期限无招聘信息的招聘专员信息成功！')

        message_content["monthly_plan_overdue_info"] = self.get_monthly_plan_overdue_info(today)
        _logger.info(' 获取月计划 逾期信息')

        message_content["first_eight_pieces_abnormal_info"] = self.get_first_eight_pieces_abnormal_info(today)
        _logger.info(' 获取月计划 上线2天后没有首八件的记录')

        message_content["the_number_of_each_department"] = self.get_the_number_of_each_department(today)
        _logger.info('获取所有部门人数')

        message_content['material_summary_sheet_abnormal_info2'] = self.get_material_summary_sheet_abnormal_info2(today)
        _logger.info('获取物料用量 计划用量和实际用量异常记录')

        message_content['outsource_order_no_person_charge'] = self.get_outsource_order_no_person_charge(today)
        _logger.info('获取外发订单 无负责人的记录')

        # 发送系统内部消息
        self.send_to_system_internal(message_content, internal_message_type)

        _logger.info('发送系统内部消息成功！')

        if message_group:

            self.send_to_enterprise_wechat(message_content, message_group)

        _logger.info('发送企业微信管理群成功！')

        if send_out_group:

            self.send_wechat_messages_send_out_group(message_content)

        _logger.info('发送企业微信外发群成功！')

        if after_the_road:
            self.send_wechat_messages_after_the_road_group(message_content)

        _logger.info('发送企业微信后道群成功！')

        


    def send_wechat_messages_send_out_group(self, message_content):
        ''' 发送企业微信消息(外发群)'''

        messages_list = []
        markdown = f"{message_content['outsource_order_delay_time_info']['date']}:\n{len(message_content['outsource_order_delay_time_info']['message_content'])}个外发逾期异常记录！\n"
        for message in message_content["outsource_order_delay_time_info"]["message_content"]:
            markdown += f"客户货期：{message['contract_date']}，下单日期：{message['date_order']}，负责人：{message['responsible_person']}，\
                工厂：{message['processing_plant']}，订单：{message['order_number']}，订单数量：{message['order_quantity']}，实际交货数：{message['actual_delivered_quantity']}，\
                    存量：{message['stock']}，报次件数：{message['defective_goods']}，逾期件数:{message['number']}，逾期天数：{message['overdue']}\n"
        messages_list.append(markdown)

        for messages in messages_list:
            weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.SEND_OUT)   # 外发群


    def send_wechat_messages_after_the_road_group(self, message_content):
        ''' 发送企业微信消息（后道群）'''

        messages_list = []

        day_qing_day_bi_messages_content = f"{message_content['day_qing_day_bi_messages_content']['date']}_{len(message_content['day_qing_day_bi_messages_content']['message_content'])}个组的日清日毕信息:\n"
        for content in message_content["day_qing_day_bi_messages_content"]["message_content"]:
            if content['group'] == "后道":

                day_qing_day_bi_messages_content += f"组别:{content['group']}\日期:{content['date']}\n{format(content['number'] / content['num_people'], '0.2f') if content['num_people'] else '人数为0!' }\n吊挂人均件数:{format(content['dg_number'] / content['num_people'], '0.2f') if content['num_people'] else '人数为0!' }\n滞留数:{int(content['stranded_number'])}\n计划差值:{int(content['plan_difference'])}\n计划阶段:{content['plan_stage']}\n"

        messages_list.append(day_qing_day_bi_messages_content)

        for messages in messages_list:
            weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.AFTER_THE_ROAD)   # 后道


    def send_to_enterprise_wechat(self, message_content, message_group):
        ''' 发送企业微信消息(管理群)'''

        messages_list = []

        markdown = f"{message_content['examine_customer_delivery_time_message_content']['date']}:\n{len(message_content['examine_customer_delivery_time_message_content']['message_content'])}个订单已经超过计划完成日期！\n"
        for message in message_content["examine_customer_delivery_time_message_content"]["message_content"]:
            markdown += f"合同日期:{message['customer_delivery_time']}，下单日期：{message['date']}，\
                订单号:{message['order_number']}，\
                属性:{message['order_attribute']}，\
                款号:{message['style_number_base']}，\
                加工类型:{message['processing_type']}，\
                订单数:{message['order_number_value']}，\
                交货数:{message['quantity_goods']}，\
                报次:{message['defective_good_number']}，\
                存量:{message['qualified_stock']}，\
                裁片:{message['cutting_number']}，\
                半成品:{message['no_accomplish_number']}\n"
        messages_list.append(markdown)

        encapsulation_dg_production_value_message_content = f"{message_content['encapsulation_dg_production_value_message_content']['date']}:各组吊挂产值信息！\n"
        # if message_content["encapsulation_dg_production_value_message_content"]["dg_yesterday_production_value"] < 15000:
            # encapsulation_dg_production_value_message_content += f"当天吊挂总产值为：{format(message_content['encapsulation_dg_production_value_message_content']['dg_yesterday_production_value'], '0.2f')}\n"
        # encapsulation_dg_production_value_message_content += f"当月平均吊挂产值为：{format(message_content['encapsulation_dg_production_value_message_content']['dg_average_monthly_production_value'], '0.2f')}\n"
        for i in message_content["encapsulation_dg_production_value_message_content"]["dg_yesterday_production_value"]:
            encapsulation_dg_production_value_message_content += f"组别：{i['group'][-1]}\n当天吊挂总产值为：{format(i['production_value'], '0.2f')}\n当月平均吊挂产值：{format(i['dg_month_avg_value'], '0.2f')}\n"
        messages_list.append(encapsulation_dg_production_value_message_content)

        day_qing_day_bi_messages_content = f"{message_content['day_qing_day_bi_messages_content']['date']}_{len(message_content['day_qing_day_bi_messages_content']['message_content'])}个组的日清日毕信息:\n"
        for content in message_content["day_qing_day_bi_messages_content"]["message_content"]:
            if content['group'] == "后道":
                day_qing_day_bi_messages_content += f"组别:{content['group']}\n日期:{content['date']}\n{format(content['number'] / content['num_people'], '0.2f') if content['num_people'] else '人数为0!' }\n吊挂人均件数:{format(content['dg_number'] / content['num_people'], '0.2f') if content['num_people'] else '人数为0!' }\n滞留数:{int(content['stranded_number'])}\n计划差值:{int(content['plan_difference'])}\n计划阶段:{content['plan_stage']}\n"
            else:
                day_qing_day_bi_messages_content += f"组别:{content['group']}\n日期:{content['date']}\n人均产值:{format(content['avg_value'], '0.2f')}\n吊挂人均产值:{format(content['dg_avg_value'], '0.2f')}\n滞留数:{int(content['stranded_number'])}\n计划差值:{int(content['plan_difference'])}\n计划阶段:{content['plan_stage']}\n"
        messages_list.append(day_qing_day_bi_messages_content)

        sheet_materials_messages_content = f"{message_content['sheet_materials_messages_content']['date']}_{len(message_content['sheet_materials_messages_content']['message_content'])}个缺少单件用料表的销售订单信息:\n"
        for message in message_content["sheet_materials_messages_content"]["message_content"]:
            sheet_materials_messages_content += f"客户货期：{message['customer_delivery_time']}，订单日期：{message['order_date']}，订单:{message['order_number']}，款号:{message['style_number']}\n"
        messages_list.append(sheet_materials_messages_content)

        the_number_of_each_department = f"{message_content['the_number_of_each_department']['date']}_{len(message_content['the_number_of_each_department']['message_content'])}各部门所有人数:\n"
        for message in message_content["the_number_of_each_department"]["message_content"]:
            department = message['department']
            number = message['number']
            the_number_of_each_department += f"{department}：部门人数{number}人<br/>"
        messages_list.append(the_number_of_each_department)

        # plan_set_messages_messages_content = f"共有{len(message_content['plan_set_messages_messages_content'])}条存在组的计划产值有异常:\n"
        # for day_messages in message_content["plan_set_messages_messages_content"]:
        #     for message in day_messages["message_content"]:
        #         plan_set_messages_messages_content += f"日期:{day_messages['date']}\n组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，计划人均产值:{message['plan_value_sum']}，计划阶段:{message['plan_stage']}\n"
        # messages_list.append(plan_set_messages_messages_content)


        day_plan_abnormal_info_content = f"{message_content['day_plan_abnormal_info_content']['date']}共有{len(message_content['day_plan_abnormal_info_content']['message_content'])}条日计划异常记录:\n"
        for message in message_content["day_plan_abnormal_info_content"]["message_content"]:
            if message['group_name'] == '裁床':
                if "plan_total_value" in message and "group_plan_total_value" in message:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划总产值:{message['plan_total_value']}，组上计划总产值:{message['group_plan_total_value']}，计划阶段:{message['plan_stage']}\n"
                else:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！\n"
            elif message['group_name'] == '后道':
                if "plan_number" in message:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划件数:{message['plan_number']}\n"
                else:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！\n"
            else:
                if "plan_value_sum" in message:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划人均产值:{message['plan_value_sum']}，计划阶段:{message['plan_stage']}\n"
                else:
                    day_plan_abnormal_info_content += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！\n"
                    
        messages_list.append(day_plan_abnormal_info_content)


        fabric_exception_messages_content = f"{message_content['fabric_exception_messages_content']['date']}共有{len(message_content['fabric_exception_messages_content']['message_content'])}条无采购记录的面料入库:\n"
        for message in message_content["fabric_exception_messages_content"]["message_content"]:
            fabric_exception_messages_content += f"物料编码:{message}\n"
        messages_list.append(fabric_exception_messages_content)


        supplementary_material_messages_content = f"{message_content['supplementary_material_messages_content']['date']}共有{len(message_content['supplementary_material_messages_content']['message_content'])}条无采购记录的辅料入库:\n"
        for message in message_content["supplementary_material_messages_content"]["message_content"]:
            supplementary_material_messages_content += f"物料编码:{message}\n"
        messages_list.append(supplementary_material_messages_content)
        

        yesterday_employee_situation_messages_content = f"{message_content['yesterday_employee_situation_messages_content']['date']}\n"
        yesterday_employee_situation_messages_content += f"入职人数:{len(message_content['yesterday_employee_situation_messages_content']['message_content']['induction_list'])}\n"
        for induction in message_content['yesterday_employee_situation_messages_content']['message_content']['induction_list']:
            yesterday_employee_situation_messages_content += f"{induction['name']}，{induction['job_name']}\n"
        yesterday_employee_situation_messages_content += f"离职人数:{len(message_content['yesterday_employee_situation_messages_content']['message_content']['departure_list'])}\n"
        for departure in message_content['yesterday_employee_situation_messages_content']['message_content']['departure_list']:
            yesterday_employee_situation_messages_content += f"{departure['name']}，{departure['job_name']}\n"
        yesterday_employee_situation_messages_content += f"在职人数:{len(message_content['yesterday_employee_situation_messages_content']['message_content']['yesterday_list'])}\n"
        messages_list.append(yesterday_employee_situation_messages_content)


        sales_order_abnormal_plan_date_messages_content = f"{message_content['sales_order_abnormal_plan_date_messages_content']['date']}共有{len(message_content['sales_order_abnormal_plan_date_messages_content']['message_content'])}条销售订单计划完成日期存在问题！\n"
        for message in message_content["sales_order_abnormal_plan_date_messages_content"]["message_content"]:
            if message['processing_type'] == "外发":
                if not message['customer_goods_time']:
                    sales_order_abnormal_plan_date_messages_content += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，加工类型:{message['processing_type']}，无客户货期！\n"
            else:
                sales_order_abnormal_plan_date_messages_content += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，计划日期:{message['planned_completion_date']}，计算日期:{message['real_date']}, 加工类型:{message['processing_type']}\n"
        messages_list.append(sales_order_abnormal_plan_date_messages_content)


        # statistical_summary_abnormal_messages_content = f"{message_content['statistical_summary_abnormal_messages_content']['date']}共有{len(message_content['statistical_summary_abnormal_messages_content']['message_content'])}条统计汇总存在问题！\n"
        # for message in message_content["statistical_summary_abnormal_messages_content"]["message_content"]:
        #     statistical_summary_abnormal_messages_content += f"订单号:{message['order_number']}，款号:{message['style_number']}，异常信息:{message['exception_info']}， 差值：{message['difference']}\n"
        # messages_list.append(statistical_summary_abnormal_messages_content)


        fabric_procurement_messages_content = f"{message_content['fabric_procurement_messages_content']['date']}共有{len(message_content['fabric_procurement_messages_content']['message_content'])}条面辅料采购后三天没有仓库入库的记录！\n"
        for message in message_content["fabric_procurement_messages_content"]["message_content"]:
            fabric_procurement_messages_content += f"单据编号:{message}\n"
        messages_list.append(fabric_procurement_messages_content)


        monthly_plan_abnormal_messages_content = f"{message_content['monthly_plan_abnormal_messages_content']['date']}共有{len(message_content['monthly_plan_abnormal_messages_content']['message_content'])}条月计划异常信息记录！\n"
        for message in message_content["monthly_plan_abnormal_messages_content"]["message_content"]:
            monthly_plan_abnormal_messages_content += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['order_date']}，订单编号:{message['order_number']}，款号:{message['style_number']}，计划上线日期:{message['plan_online_date']}，计划交货日期:{message['production_delivery_time']}，计算交货日期:{message['real_date']}\n"
        messages_list.append(monthly_plan_abnormal_messages_content)


        raw_materials_order_abnormal_info = f"{message_content['raw_materials_order_abnormal_info']['date']}共有{len(message_content['raw_materials_order_abnormal_info']['message_content'])}个订单的产前准备计划物料异常！\n"
        for message in message_content["raw_materials_order_abnormal_info"]["message_content"]:
            raw_materials_order_abnormal_info += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_number']}，原因:{message['cause']}\n"
        messages_list.append(raw_materials_order_abnormal_info)


        outbound_order_abnormal_info = f"{message_content['outbound_order_abnormal_info']['date']}共有{len(message_content['outbound_order_abnormal_info']['message_content'])}个订单未创建外发订单！\n"
        for message in message_content["outbound_order_abnormal_info"]["message_content"]:
            outbound_order_abnormal_info += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_number']}\n"
        messages_list.append(outbound_order_abnormal_info)


        material_summary_sheet_abnormal_info = f"{message_content['material_summary_sheet_abnormal_info']['date']}共有{len(message_content['material_summary_sheet_abnormal_info']['message_content'])}个物料汇总数据异常的记录！\n"
        for message in message_content["material_summary_sheet_abnormal_info"]["message_content"]:
            material_summary_sheet_abnormal_info += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_id']}，款号:{message['style_number']}，物料名称：{message['material_name']}\n"
        messages_list.append(material_summary_sheet_abnormal_info)
        

        monthly_plan_material_ready_abnormal_info = f"{message_content['monthly_plan_material_ready_abnormal_info']['date']}共有{len(message_content['monthly_plan_material_ready_abnormal_info']['message_content'])}个月计划上线日期前一天面辅料齐备异常的采购记录！\n"
        for message in message_content["monthly_plan_material_ready_abnormal_info"]["message_content"]:
            monthly_plan_material_ready_abnormal_info += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_id'][-1]}，款号:{message['style_number'][-1]}，物料编号:{message['material_code'][-1]}，物料名称：{message['material_name']}\n"
        messages_list.append(monthly_plan_material_ready_abnormal_info)


        monthly_plan_cutting_bed_production_abnormal_info = f"{message_content['monthly_plan_cutting_bed_production_abnormal_info']['date']}共有{len(message_content['monthly_plan_cutting_bed_production_abnormal_info']['message_content'])}个月计划上线日期前一天裁床产量异常的采购记录！\n"
        for message in message_content["monthly_plan_cutting_bed_production_abnormal_info"]["message_content"]:
            monthly_plan_cutting_bed_production_abnormal_info += f"合同日期:{message['contract_date']}，订单日期:{message['order_date']}，订单编号:{message['order_number']}，\
                加工类型:{message['processing_type']}，款号:{message['style_number']}，订单件数{message['order_quantity']}，计划件数:{message['plan_number']}，完成件数：{message['cutting_bed_production']}\n"
        messages_list.append(monthly_plan_cutting_bed_production_abnormal_info)


        sales_order_no_month_plan_abnormal_info = f"{message_content['sales_order_no_month_plan_abnormal_info']['date']}共有{len(message_content['sales_order_no_month_plan_abnormal_info']['message_content'])}个销售订单创建后第二天没有月计划的记录！\n"
        for message in message_content["sales_order_no_month_plan_abnormal_info"]["message_content"]:
            sales_order_no_month_plan_abnormal_info += f"订单编号:{message['order_number']}，款号:{message['style_number']}，原因：{message['cause']}\n"
        messages_list.append(sales_order_no_month_plan_abnormal_info)


        fsn_sales_return_and_finished_product_ware_info = f"{message_content['fsn_sales_return_and_finished_product_ware_info']['date']}共有{len(message_content['fsn_sales_return_and_finished_product_ware_info']['message_content'])}个销售售后退货和仓库入库件数不相符的记录！\n"
        for message in message_content["fsn_sales_return_and_finished_product_ware_info"]["message_content"]:
            fsn_sales_return_and_finished_product_ware_info += f"订单号:{message['order_id']}，款号:{message['style_number']}，质量：{message['quality']}，件数：{message['number']}，仓库件数：{message['cangkujianshu']}\n"
        messages_list.append(fsn_sales_return_and_finished_product_ware_info)


        recruitment_info = f"{message_content['recruitment_info']['date']}共有{len(message_content['recruitment_info']['message_content'])}个人事招聘信息\n"
        for message in message_content["recruitment_info"]["message_content"]:
            recruitment_info += f"招聘者：{message['recruiter']}，面试人:{message['interviewer']}，面试岗位:{message['job_name']}，是否合格:{message['eligibility']}\n"
        messages_list.append(recruitment_info)


        prenatal_preparation_progress_anomaly_info = f"{message_content['prenatal_preparation_progress_anomaly_info']['date']}共有{len(message_content['prenatal_preparation_progress_anomaly_info']['message_content'])}个计划上线前一天产前准备进度表异常！\n"
        for message in message_content["prenatal_preparation_progress_anomaly_info"]["message_content"]:
            prenatal_preparation_progress_anomaly_info += f"订单号：{message['订单号']}，款号：{message['款号']}，异常项目:{'，'.join(message['demo_list'])}\n"
        messages_list.append(prenatal_preparation_progress_anomaly_info)


        def send_weixin_messages(messages):
            if message_group == "管理群":
                weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.ADMIN_GROUP)   # 管理群

            elif message_group == "测试群":
                weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.DEVELOPMENT_AND_TEST)   # 开发测试群

        for messages in messages_list:
            send_weixin_messages(messages)


    # 发送系统内部消息
    def send_to_system_internal(self, message_content, internal_message_type):

        if internal_message_type == "all":
            # 系统内部发送消息
            self.env["mail.channel"].sudo().send_daily_messages(message_content)

            # 发送产前准备频道
            self.env["mail.channel"].sudo().send_advance_preparation_messages(message_content)

            # 发送产后准备频道
            self.env["mail.channel"].sudo().send_postpartum_messages(message_content)

            # 发送人事部准备频道
            self.env["mail.channel"].sudo().fsn_hr_inspect_channel_messages(message_content)

            # 发送后道专用频道
            self.env["mail.channel"].sudo().fsn_after_the_road_inspect_channel_messages(message_content)
        
        elif internal_message_type == "only_daily":
            # 系统内部发送消息
            self.env["mail.channel"].sudo().send_daily_messages(message_content)
