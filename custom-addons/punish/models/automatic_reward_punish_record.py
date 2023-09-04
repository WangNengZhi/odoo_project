
from odoo import models, fields, api
from datetime import datetime, timedelta, date
import calendar
import itertools
from dateutil.relativedelta import relativedelta

import threading

import logging
_logger = logging.getLogger(__name__)

"""自动生成reward_punish_record（每天执行）"""

class RewardPunishRecord(models.Model):
    _inherit = "reward_punish_record"


    def query_plan_date(self, today):
        
        planning_slot_obj = self.env["planning.slot"].sudo().search([("dDate", "!=", today), ("dDate", "!=", False)], order="dDate desc", limit=1)

        return planning_slot_obj.dDate


    # 根据日清日毕生成reward_punish_record
    def day_qing_day_bi_automatic_reward_punish_record(self, today):
        new_date = today
        # 日期减少一天
        today = self.query_plan_date(today) - timedelta(days=1)
        group_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "后道", "裁床"]

        day_qing_day_bi_objs = self.env["day_qing_day_bi"].sudo().read_group(
            [("date", "=", today), ("group", "in", group_list)],
            fields=["group", "stranded_number", "plan_difference", "plan_stranded"],
            groupby=['group']
        )

        for day_qing_day_bi_obj in day_qing_day_bi_objs:

            group = day_qing_day_bi_obj.get('group')

            stranded_number = day_qing_day_bi_obj.get("stranded_number")
            if stranded_number:  # 组上滞留
                if not self.sudo().search([("event_date", "=", today), ("event_type", "=", f"{day_qing_day_bi_obj.get('group')}组group_leader_retention")]):

                    if group == "后道":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}部group_leader_retention",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": stranded_number * 2,
                            "record_matter": f"{today}, {group}部，因没有做到日清日毕，滞留{stranded_number}件，违反了《后道主管岗位职责》。"
                        })
                    elif group == "裁床":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}部group_leader_retention",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": stranded_number,
                            "record_matter": f"{today}, {group}部，因没有做到日清日毕，滞留{stranded_number}件，违反了《裁床主管岗位职责》。"
                        })
                    else:
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}组group_leader_retention",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": stranded_number * 5,
                            "record_matter": f"{today}, {group}组，因没有做到日清日毕，滞留{stranded_number}件，违反了《组长岗位职责》。"
                        })



            plan_difference = day_qing_day_bi_obj.get("plan_difference")
            if plan_difference:  # 计划差值
                if not self.sudo().search([("event_date", "=", today), ("event_type", "=", f"{day_qing_day_bi_obj.get('group')}组group_leader_difference")]):

                    if group == "后道":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}部group_leader_difference",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": plan_difference * 2,
                            "record_matter": f"{today}, {group}部，因未完成计划产值，相差{plan_difference}件，违反了《后道主管岗位职责》。"
                        })
                    elif group == "裁床":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}部group_leader_difference",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": plan_difference,
                            "record_matter": f"{today}, {group}部，因未完成计划产值，相差{plan_difference}件，违反了《裁床主管岗位职责》。"
                        })
                    else:

                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}组group_leader_difference",
                            "declare_time": new_date,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": plan_difference * 5,
                            "record_matter": f"{today}, {group}组，因未完成计划产值，相差{plan_difference}件，违反了《组长岗位职责》。"
                        })



            plan_stranded = day_qing_day_bi_obj.get("plan_stranded")
            if plan_difference and plan_stranded < 0:
                if not self.sudo().search([("event_date", "=", today), ("event_type", "=", f"{day_qing_day_bi_obj.get('group')}组group_leader_over_budget")]):

                    if group == "后道":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}部group_leader_over_budget",
                            "declare_time": new_date,
                            "record_type": "reward",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": abs(plan_stranded * 2),
                            "record_matter": f"{today}, {group}部，因超额完成计划产值，超出{abs(plan_stranded)}件，根据《后道主管岗位职责》。"
                        })
                    elif group == "裁床":
                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}组group_leader_over_budget",
                            "declare_time": new_date,
                            "record_type": "reward",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": abs(plan_stranded),
                            "record_matter": f"{today}, {group}组，因超额完成计划产值，超出{abs(plan_stranded)}件，根据《裁床主管岗位职责》。"
                        })
                    else:

                        self.sudo().create({
                            "is_automatic": True,
                            "event_date": today,
                            "event_type": f"{group}组group_leader_over_budget",
                            "declare_time": new_date,
                            "record_type": "reward",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": abs(plan_stranded * 5),
                            "record_matter": f"{today}, {group}组，因超额完成计划产值，超出{abs(plan_stranded)}件，根据《组长岗位职责》。"
                        })


    # 根据中查漏查表生成reward_punish_record
    def middle_check_day_leak_automatic_reward_punish_record(self, today):
        # 日期减少一天
        today = self.query_plan_date(today) - timedelta(days=1)

        middle_check_day_leak_objs = self.env["middle_check_day_leak"].sudo().search([
            ("date", "=", today),
        ])
        for middle_check_day_leak_obj in middle_check_day_leak_objs:
            if middle_check_day_leak_obj.assess_index:
                emp_id = self.env["hr.employee"].sudo().search([("name", "=", middle_check_day_leak_obj.middle_check_principal)]).id
                if not self.sudo().search([("event_date", "=", today), ("event_type", "=", f"{emp_id}middle_check_omit")]):
                    style_number_list = middle_check_day_leak_obj.mapped('style_number_line_ids.name.style_number')
                    self.sudo().create({
                        "is_automatic": True,
                        "event_date": today,
                        "event_type": f"{emp_id}middle_check_omit",
                        "declare_time": fields.Datetime.now(),
                        "emp_id": emp_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": middle_check_day_leak_obj.assess_index,
                        "record_matter": f"{today}, {middle_check_day_leak_obj.middle_check_principal}，{'，'.join(style_number_list)}，\
总返修率{round(middle_check_day_leak_obj.repair_ratio, 2)}%，超过3%，\
当日返修{middle_check_day_leak_obj.repair_quantity}件，违反了《中查岗位职责》。"
                    })


    # 根据总检漏查表生成reward_punish_record
    def always_check_omission_automatic_reward_punish_record(self, today):
        # 日期减少一天
        today = self.query_plan_date(today) - timedelta(days=1)

        always_check_omission_objs = self.env["always_check_omission"].sudo().search([
            ("dDate", "=", today),
        ])
        for always_check_omission_obj in always_check_omission_objs:

            if always_check_omission_obj.assess_index:
                emp_id = self.env["hr.employee"].sudo().search([("name", "=", always_check_omission_obj.always_check_principal)]).id
                if not self.sudo().search([("event_date", "=", today), ("event_type", "=", f"{emp_id}always_check_omit")]):
                    style_number_list = always_check_omission_obj.mapped('style_number_line_ids.name.style_number')
                    self.sudo().create({
                        "is_automatic": True,
                        "event_date": today,
                        "event_type": f"{emp_id}always_check_omit",
                        "declare_time": fields.Datetime.now(),
                        "emp_id": emp_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": always_check_omission_obj.assess_index,
                        "record_matter": f"{today}, {always_check_omission_obj.always_check_principal}，{'，'.join(style_number_list)}，\
总返修率{round(always_check_omission_obj.repair_ratio, 2)}%，超过3%，\
当日返修{always_check_omission_obj.repair_quantity}件，违反了《总检岗位职责》。"
                    })

    # 根据日报异常客户货期生成reward_punish_record
    def fsn_daily_examine_customer_delivery_automatic_reward_punish_record(self, today):
        
        # 根据客户货期生成
        record_list = self.env["fsn_daily"].sudo().get_examine_customer_delivery_time_messages(today).get("message_content")
        factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id
        workshop_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "车间主任"), ("is_delete", "=", False)], limit=1, order="entry_time").id
        assistant_factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "副厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record in record_list:

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": factory_director_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 200,
                "record_matter": f"订单{record['order_number']}已经超过客户货期！差值:{record['difference']} 报次:{record['not_goods']}，违反了《厂长岗位职责》。"
            })

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": assistant_factory_director_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 100,
                "record_matter": f"订单{record['order_number']}已经超过客户货期！差值:{record['difference']} 报次:{record['not_goods']}，违反了《厂长岗位职责》。"
            })

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": workshop_director_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 100,
                "record_matter": f"订单{record['order_number']}已经超过客户货期！差值:{record['difference']} 报次:{record['not_goods']}，违反了《车间主任岗位职责》。"
            })



    # 根据日报日清日毕生成reward_punish_record
    def fsn_daily_day_qing_day_bi_automatic_reward_punish_record(self, today):

        # 根据日报日清日毕生成
        record_list = self.env["fsn_daily"].sudo().get_day_qing_day_bi_messages(today).get("message_content")
        emp_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "车间主任"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record in record_list:
            
            def create_record():
                if not self.sudo().search([("event_date", "=", record['date']), ("event_type", "=", f"{record['group']}always_check_omit")]):
                    self.sudo().create({
                        "is_automatic": True,
                        "event_date": record['date'],
                        "event_type": f"{record['group']}always_check_omit",
                        "declare_time": today,
                        "emp_id": emp_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 100,
                        "record_matter": f"{record['date']}日清日毕，{record['group']}组人均产值{round(record['avg_value'], 2)}，未完成人均产值要求，违反了《车间主任岗位职责》。计划阶段:{record['plan_stage']}"
                    })

            if record['group'] in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "整件一组"]:
                
                if record["plan_stage"] == "开款第一天":
                    if record['avg_value'] < 450:
                        create_record()
                elif record["plan_stage"] == "开款第二天":
                    if record['avg_value'] < 500:
                        create_record()
                else:
                    if record['avg_value'] < 560:
                        create_record()


    # 根据日报日清日毕计划异常生成reward_punish_record
    def fsn_daily_day_cycle_get_plan_set_messages(self, today):


        record_list = self.env["fsn_daily"].sudo().cycle_get_plan_set_messages(today)
        emp_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "生产统计员"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record_day_list in record_list:
            for record_group in record_day_list["message_content"]:

                if not self.sudo().search([("emp_id", "=", emp_id), ("money_amount", "=", 20), ("record_matter", "like", f"{record_day_list['date']}，{record_group['group_name']}组")]):
            
                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": emp_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 20,
                        "record_matter": f"{record_day_list['date']}，{record_group['group_name']}组，计划人均产值{record_group['plan_value_sum']}，计划阶段为{record_group['plan_stage']}。计划不合格！"
                    })


    # 根据日报统计汇总异常信息生成reward_punish_record
    def fsn_daily_statistical_summary_set_messages(self, today):

        objs = self.env["fsn_daily"].sudo().get_statistical_summary_abnormal_messages_content(today).get("message_content")
        for obj in objs:
            for job_name in obj["jobs_list"]:
                emp_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", job_name), ("is_delete", "=", False)], limit=1, order="entry_time").id
                self.sudo().create({
                    "is_automatic": True,
                    # "event_date": today,
                    # "event_type": f"{emp_id}middle_check_omit",
                    "declare_time": today,
                    "emp_id": emp_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 100,
                    "record_matter": f"统计汇总异常！订单号:{obj['order_number']}，款号:{obj['style_number']}，{obj['exception_info']}，差值:{obj['difference']}"
                })





    # 获取当月第一天和最后一天
    def set_begin_and_end(self, today):

        this_month_start = datetime(today.year, today.month, 1)
        this_month_end = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1]) + timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

        return this_month_start, this_month_end


    # 根据返修模块：组返修统计：查货数量 != 吊挂数量 罚款100  返修数量 < 滞留数量 罚款50   查询当前月份的全部记录
    def based_on_group_statistical_abnormal_data(self, today):

        qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id
        
        this_month_start, this_month_end = self.set_begin_and_end(today)

        group_statistical_objs = self.env["group_statistical"].search_read(
            [("dDate", ">=", this_month_start), ("dDate", "<=", this_month_end)],
            fields=["dDate", "group", "invest", "style_number", "repair_quantity", "check_quantity", "dg_number", "hang_the_stranded"],
            order='dDate'
        )


        for dDate, dDate_record_objs in itertools.groupby(group_statistical_objs, key=lambda x:x["dDate"]):     # 按日期分组

            dDate_record_objs = list(dDate_record_objs)

            dDate_record_objs.sort(key=lambda x: x['invest'], reverse=False)     # 按员工排序


            for invest, invest_record_objs in itertools.groupby(dDate_record_objs, key=lambda x:x['invest']):     # 再按员工分组

                invest_record_objs = list(invest_record_objs)

                employee_list = self.env["hr.employee"].search_read([("name", "=", invest)], ['id'])
                invest_id = employee_list[0]['id'] if employee_list else False

                check_quantity = dg_number = repair_quantity = hang_the_stranded = 0
                style_number_list = []

                for record in invest_record_objs:

                    check_quantity += record['check_quantity']
                    dg_number += record['dg_number']
                    repair_quantity += record['repair_quantity']
                    hang_the_stranded += record['hang_the_stranded']

                    style_number_list.append(record['style_number'][-1])
                
                style_number_str = ",".join(style_number_list)

                if check_quantity < dg_number:

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": invest_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 100,
                        "record_matter": f"{invest}, {dDate},在组返修统计表中，{style_number_str}存在查货数量小于吊挂数量的记录！"
                    })

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": qc_supervisor_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 100,
                        "record_matter": f"{invest}, {dDate},在组返修统计表中，{style_number_str}存在查货数量小于吊挂数量的记录！"
                    })


                if repair_quantity < hang_the_stranded:

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": invest_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 50,
                        "record_matter": f"{invest}, {dDate},在组返修统计表中，{style_number_str}存在返修数量小于滞留数量的记录！"
                    })

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": qc_supervisor_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 50,
                        "record_matter": f"{invest}, {dDate},在组返修统计表中，{style_number_str}存在返修数量小于滞留数量的记录！"
                    })


    # 销售订单创建后 无月计划自动罚单
    def sales_order_no_month_plan(self, today):

        record_list = self.env["fsn_daily"].sudo().get_sales_order_no_month_plan(today).get("message_content")

        factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record in record_list:

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": factory_director_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": f"订单{record['order_number']}，款号{record['style_number']}，无月计划！违反了《厂长岗位职责》。"
            })


    # BOM面辅料汇总异常 自动罚单
    def bom_material_summary_sheet_abnormal_info(self, today):


        record_list = self.env["fsn_daily"].sudo().get_material_summary_sheet_abnormal_info(today).get("message_content")

        employee_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "面辅料主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record in record_list:

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": employee_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": f"订单{record['order_id']}，款号{record['style_number']}，物料名称{record['material_name']}，物料汇总异常！违反了《面辅料主管岗位职责》。"
            })

    # 超过月计划计划完成日期
    def fsn_daily_get_monthly_plan_abnormal_messages_content(self, today):
        
        factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        assistant_factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "副厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id
        abnormal_list = []

        fsn_month_plan_data_list = self.env['fsn_month_plan'].sudo().search_read(
            [("production_delivery_time", "<", today)],
            ["order_number", "style_number"])
        
        for fsn_month_plan_data in fsn_month_plan_data_list:
            # {'id': 13, 'order_number': (444, '2208051'), 'style_number': (885, '8051-2-CC')}
            objs = self.env["style_number_summary"].sudo().search_read(
                [("order_number", "=", fsn_month_plan_data["order_number"][0]), ("style_number", "=", fsn_month_plan_data["style_number"][0])],
                ["cutting_bed", "enter_warehouse", "defective_good_number"])
            
            for obj in objs:
                if obj['cutting_bed'] > obj['enter_warehouse'] + obj['defective_good_number']:

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": factory_director_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 100,
                        "record_matter": f"订单{fsn_month_plan_data['order_number'][-1]}款号{fsn_month_plan_data['style_number'][-1]}已经超过月计划日期！违反了《厂长岗位职责》。"
                    })

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": assistant_factory_director_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"订单{fsn_month_plan_data['order_number'][-1]}款号{fsn_month_plan_data['style_number'][-1]}已经超过月计划日期！违反了《厂长岗位职责》。"
                    })
  


    # 销售售后退货和B2B展厅退货
    def fsn_daily_after_sales_return_goods(self, today):

        record_list = self.env["fsn_daily"].sudo().after_sales_return_goods(today).get("message_content")
        qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id
        for record in record_list:

            if record['quality'] == "次品":
                self.sudo().create({
                    "is_automatic": True,
                    "declare_time": today,
                    "emp_id": qc_supervisor_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "qulity_control",
                    "money_amount": record['number'] * 2,
                    "record_matter": f"{record['customer_name']}, {record['type']}, {record['number']}件{record['quality']}退货！"
                })


    def outsource_order_automatic_reward_punish_record(self, today):
        ''' 外发订单绩效考核'''

        abnormal_list = []
        outsource_order_objs = self.env['outsource_order'].sudo().search([
            ("approval_state", "=", "待审批"),
            ("state", "not in", ['已完成', '退单']),
            ("responsible_person", "!=", False),
            ("customer_delivery_time", "<", today)
        ])

        for outsource_order_obj in outsource_order_objs:

            days = (today - outsource_order_obj.customer_delivery_time).days

            difference = outsource_order_obj.order_quantity - outsource_order_obj.stock

            self.sudo().create({
                "is_automatic": True,
                "declare_time": today,
                "emp_id": outsource_order_obj.responsible_person.id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 5 * difference,
                "record_matter": f"外发{outsource_order_obj.outsource_plant_id.name}，订单为{outsource_order_obj.order_id.order_number}，{difference}件已经超过客户货期{days}天！违反了《外发岗位职责》。"
            })

    def encapsulation_dg_production_value_automatic_reward_punish_record(self, today):
        ''' 获取昨天后道吊挂人均产量记录，不足100件，则生成记录'''
        encapsulation_dg_production_value_info = self.env["fsn_daily"].sudo().encapsulation_dg_production_value(today)


        posterior_channel_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "后道主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        for record in encapsulation_dg_production_value_info["dg_yesterday_production_value"]:
            if record.get("group")[1] == "后整":
                avg_quantity = record['total_quantity'] / record['people_num']
                if avg_quantity < 100:

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": posterior_channel_supervisor_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 50,
                        "record_matter": f"{encapsulation_dg_production_value_info['date']}, 后道人均产量{format(avg_quantity, '0.2f')}, 不足100！"
                    })

                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": today,
                        "emp_id": posterior_channel_supervisor_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": 0,
                        "record_matter": f"{encapsulation_dg_production_value_info['date']}, 后道人均产量{format(avg_quantity, '0.2f')}, 不足100！，需要加班到11点！"
                    })


    def general_inspection_abnormal_info_automatic_reward_punish_record(self, generate_date):
        ''' 总检交货返修数量异常 自动绩效考核'''
        general_inspection_abnormal_info = self.env["fsn_daily"].sudo().get_general_inspection_abnormal_info(generate_date)

        general_inspection_list = []

        for i in general_inspection_abnormal_info['message_content']:

            if (i['general_number'] != i['dg_general_number']) or (i['repair_number'] != i['dg_repair_number']):
                general_inspection_list.append(i['general1'])

        if general_inspection_list:
            qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id


            self.sudo().create({
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": qc_supervisor_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "qulity_control",
                "money_amount": 50,
                "record_matter": f"{general_inspection_abnormal_info['date']}, 总检:{','.join(general_inspection_list)},交货数或返修数与吊挂不符！",
                "event_date": general_inspection_abnormal_info['date'],
                "event_type": "品控主管general_inspection_abnormal",
            })

            # posterior_channel_supervisor_id = self.env["hr.employee"].sudo().search([("name", "=", general_inspection_list), ("is_delete", "=", False)], limit=1, order="entry_time").id
            for name in general_inspection_list:
                qc_name = self.env["hr.employee"].sudo().search([("name", "=", name), ("is_delete", "=", False)])

                self.sudo().create({
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": qc_name.id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "qulity_control",
                    "money_amount": 50,
                    "record_matter": f"{general_inspection_abnormal_info['date']}, 总检:{','.join(qc_name.name)},交货数或返修数与吊挂不符！",
                    "event_date": general_inspection_abnormal_info['date'],
                    "event_type": "后道主管general_inspection_abnormal",
                })


    def get_client_ware_customer_return_info_automatic_reward_punish_record(self, generate_date):
        ''' 客仓退货，自动绩效考核'''

        client_ware_customer_return_info = self.env["fsn_daily"].sudo().get_client_ware_customer_return_info(generate_date)
        
        client_ware_customer_return_info['message_content'].sort(key=lambda x: x['dDate'], reverse=False)

        for date_, objs in itertools.groupby(client_ware_customer_return_info['message_content'], key=lambda x: x['dDate']):

            objs_list = list(objs)
            total = sum(i['repair_number'] for i in objs_list)

            record_matter = ','.join(f"款号:{i['style_number']},退货{i['repair_number']}件" for i in objs_list)

            if not self.sudo().search([("event_date", "=", date_), ("event_type", "=", "client_ware_customer_return")]):

                qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

                posterior_channel_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "后道主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

                def create_record(emp_id, quota):
                    self.sudo().create({
                        "is_automatic": True,
                        "declare_time": client_ware_customer_return_info['date'],
                        "emp_id": emp_id,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "qulity_control",
                        "money_amount": quota * total,
                        "record_matter": f"{date_},客仓退货：{record_matter}",
                        "event_date": date_,
                        "event_type": "client_ware_customer_return",
                    })

                if qc_supervisor_id:
                    create_record(qc_supervisor_id, 8)

                if posterior_channel_supervisor_id:
                    create_record(posterior_channel_supervisor_id, 5)


    def get_examine_customer_delivery_time_messages_automatic_reward_punish_record(self, generate_date):
        ''' 订单逾期，自动绩效考核'''

        examine_customer_delivery_time_messages = self.env["fsn_daily"].sudo().get_examine_customer_delivery_time_messages(generate_date)

        for i in examine_customer_delivery_time_messages['message_content']:
            if i['customer_delivery_time'] >= date(2023, 5, 1):
                if i['order_number_value'] > i['qualified_stock']:

                    factory_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "厂长"), ("is_delete", "=", False)], limit=1, order="entry_time").id
                    production_director_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "生产总监"), ("is_delete", "=", False)], limit=1, order="entry_time").id
                    quality_control_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id
                    number = i['order_number_value'] - i['qualified_stock']

                    def create_record(emp_id, quota):
                        self.sudo().create({
                            "is_automatic": True,
                            "declare_time": examine_customer_delivery_time_messages['date'],
                            "emp_id": emp_id,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "qulity_control",
                            "money_amount": quota * number,
                            "record_matter": f"订单：{i['order_number']}，客户名称：{i['customer_name']}，客户货期：{i['customer_delivery_time']}，逾期{number}件！{(fields.Date.today() - i['customer_delivery_time']).days}天！",
                        })

                    if factory_director_id:
                        create_record(factory_director_id, 8)
                    
                    if production_director_id:
                        create_record(production_director_id, 5)

                    if quality_control_supervisor_id:
                        create_record(quality_control_supervisor_id, 5)


    def get_prenatal_preparation_progress_anomaly_info_automatic_reward_punish_record(self, generate_date):
        ''' 产前准备异常，自动绩效考核'''
        prenatal_preparation_progress_anomaly_info = self.env["fsn_daily"].sudo().get_prenatal_preparation_progress_anomaly_info(generate_date)

        for i in prenatal_preparation_progress_anomaly_info['message_content']:

            technical_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "技术部主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

            self.sudo().create({
                "is_automatic": True,
                "declare_time": prenatal_preparation_progress_anomaly_info['date'],
                "emp_id": technical_supervisor_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "qulity_control",
                "money_amount": 100 * len(i['demo_list']),
                "record_matter": f"订单：{i['订单号']}，款号：{i['款号']}，计划上线前一天，产前准备进度表异常，{'，'.join(i['demo_list'])}",
            })
            qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id
            self.sudo().create({
                "is_automatic": True,
                "declare_time": prenatal_preparation_progress_anomaly_info['date'],
                "emp_id": qc_supervisor_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "qulity_control",
                "money_amount": 100 * len(i['demo_list']),
                "record_matter": f"订单：{i['订单号']}，款号：{i['款号']}，计划上线前一天，产前准备进度表异常，{'，'.join(i['demo_list'])}",
            })

    def get_time_limit_not_recruitment_record_automatic_reward_punish_record(self, generate_date):
        ''' 获取期限无招聘信息的招聘专员，自动绩效考核'''

        time_limit_not_recruitment_record = self.env["fsn_daily"].sudo().get_time_limit_not_recruitment_record(generate_date)

        for i in time_limit_not_recruitment_record['message_content']:

            emp_obj = self.env["hr.employee"].sudo().search([("name", "=", i['name'])])

            self.sudo().create({
                "is_automatic": True,
                "declare_time": time_limit_not_recruitment_record['date'],
                "emp_id": emp_obj.id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "qulity_control",
                "money_amount": 100,
                "record_matter": f"人事招聘专员：{emp_obj.name}，连续三天，无招聘数据记录！",
            })


    def get_monthly_plan_overdue_info_automatic_reward_punish_record(self, generate_date):
        ''' 获取月计划 逾期信息，自动绩效考核'''

        monthly_plan_overdue_info = self.env["fsn_daily"].sudo().get_monthly_plan_overdue_info(generate_date)

        for i in monthly_plan_overdue_info['message_content']:
            
            if i['difference_delivery'] > 0:

                fsn_staff_team_obj = self.env['fsn_staff_team'].sudo().search([("name", "=", i['group'])])

                emp_obj = self.env["hr.employee"].sudo().search([
                    ("job_id.name", "=", "流水组长"),
                    ("department_id", "=", fsn_staff_team_obj.department_id.id),
                    ("is_delete", "=", False)
                ], limit=1, order="entry_time")

                self.sudo().create({
                    "is_automatic": True,
                    "declare_time": monthly_plan_overdue_info['date'],
                    "emp_id": emp_obj.id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": i['difference_delivery'] * 2,
                    "record_matter": f"根据月计划，订单：{i['order_number']}，款号：{i['style_number']}，由{i['group']}组负责生产，车间逾期{i['difference_delivery']}件数！{(fields.Date.today() - i['customer_delivery_time']).days}天！",
                })


                posterior_channel = i['factory_delivery_variance'] - i['difference_delivery']
            else:
                posterior_channel = i['factory_delivery_variance']


            if posterior_channel > 0:

                posterior_channel_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "后道主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

                self.sudo().create({
                    "is_automatic": True,
                    "declare_time": monthly_plan_overdue_info['date'],
                    "emp_id": posterior_channel_supervisor_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": posterior_channel * 2,
                    "record_matter": f"根据月计划，订单：{i['order_number']}，款号：{i['style_number']}，后道逾期{posterior_channel}件数！{(fields.Date.today() - i['customer_delivery_time']).days}天！",
                })


    def get_group_efficiency_exception_record_automatic_reward_punish_record(self, generate_date):
        ''' 获取各组效率异常记录 自动生成罚单'''
        group_efficiency_exception_record = self.env["fsn_daily"].sudo().get_group_efficiency_exception_record(generate_date)
        for i in group_efficiency_exception_record['message_content']:
                
            emp_obj = self.env["hr.employee"].sudo().search([
                ("job_id.name", "=", "流水组长"),
                ("department_id.name", "=", i['group'].replace('车缝', '缝纫')),
                ("is_delete", "=", False)
            ], limit=1, order="entry_time")

            self.sudo().create({
                "is_automatic": True,
                "declare_time": group_efficiency_exception_record['date'],
                "emp_id": emp_obj.id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 0,
                "record_matter": f"{generate_date.year}年{generate_date.month}月，截至到{generate_date}前，{i['group']}月平均效率为{i['efficiency']}%，没有达到50%，需要加班到11点！"
            })



    def get_first_eight_pieces_abnormal_info(self, generate_date):
        ''' 获取首八件异常信息 自动生成罚单'''

        first_eight_pieces_abnormal_info = self.env["fsn_daily"].sudo().get_first_eight_pieces_abnormal_info(generate_date)


        for i in first_eight_pieces_abnormal_info['message_content']:
            
            qc_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "品控主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

            self.sudo().create({
                "is_automatic": True,
                "declare_time": first_eight_pieces_abnormal_info['date'],
                "emp_id": qc_supervisor_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 100,
                "record_matter": f"订单{i['order_number']}，款号{i['style_number']}，上线日期为{i['plan_online_date']}，上线两天后无首八件！"
            })

    def get_performance_appraisal_data(self, generate_date):
        """绩效考核"""
        order_completed = self.env["fsn_daily"].sudo().order_completed(generate_date)

        for order in order_completed:

            # qc_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", order['invest'])], limit=1, order="entry_time")
            qc_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", '中查'), ("is_delete", "=", False)], limit=1,
                                                          order="entry_time").id

            data = {
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": qc_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": abs(order['difference_delivery']) * 2,
                "record_matter": f"订单{order['order_number']}，款号{order['style_number']}, 订单完成后，车间交货差异为{order['difference_delivery']}件 ！"
            }
            self.sudo().create(data)


    def get_sale_order_not_paid_record_automatic_reward_punish_record(self, generate_date):
        ''' 获取销售订单大于30天未付款, 自动生成绩效考核'''
        sale_order_not_paid = self.env["mail.channel"].sudo().get_sale_order_not_paid()

        print(sale_order_not_paid)

        sales_specialist_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "销售专员"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        self.sudo().create({
            "is_automatic": True,
            "declare_time": generate_date,
            "emp_id": sales_specialist_obj_id,
            "record_type": "punish",
            "punish_type": "绩效",
            "matter_type": "production",
            "money_amount": len(sale_order_not_paid) * 20,
            "record_matter": f"销售订单：{'，'.join(i['name'] for i in sale_order_not_paid)}大于30天，未付款！",
        })

    def suspend_and_generate_a_ticket(self, generate_date):
        """吊挂生成罚单"""
        hanging_abnormal_data = self.env["fsn_daily"].sudo().obtain_hanging_date()

        # 查询IE
        ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
                                                          limit=1, order="entry_time").id

        record_date = [ret['date'] for ret in hanging_abnormal_data]
        if len(hanging_abnormal_data) > 0:
                data = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": ie_obj_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": int(50),
                    "record_matter": f"{record_date[0]}日，存在计件员工吊挂效率为0.1，存在在异常！",
                }
                self.sudo().create(data)

    def manual_efficiency_generation_of_tickets(self, generate_date):
        """生成手动效率罚单"""
        manual_efficiency_data = self.env["fsn_daily"].sudo().personal_productivity()
        # 查询IE
        ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
                                                          limit=1, order="entry_time").id

        record_date = [ret['date'] for ret in manual_efficiency_data]
        for manual in manual_efficiency_data:
            if len(manual['efficiency']) == 0:
                data = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": ie_obj_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": int(50),
                    "record_matter": f"{record_date[0]}日，手工效率未录入系统，存在在异常！",
                }
                self.sudo().create(data)


    def get_time_limit_not_business_opportunity_record_automatic_reward_punish_record(self, generate_date):
        ''' 获取期限无商机销售人员，自动生成绩效考核'''
        time_limit_not_business_opportunity_record = self.env["mail.channel"].sudo().get_time_limit_not_business_opportunity_record(generate_date)
        for i in time_limit_not_business_opportunity_record['message_content']:

            self.sudo().create({
                "is_automatic": True,
                "declare_time": time_limit_not_business_opportunity_record['date'],
                "emp_id": i['emp_id'],
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": f"销售专员：{i['name']}，连续三天，无商机数据记录！",
            })

    def bom_ticket_generation(self, generate_date):
        """bom罚单生成"""
        material_summary_sheet_abnormal_info = self.env["fsn_daily"].sudo().get_material_summary_sheet_abnormal_info2(generate_date)

        # 查询各个负责人
        technology_name = self.env['hr.employee'].search([('job_id', '=', '技术部主管'), ('is_delete', '=', False)]).id
        fabric_name = self.env['hr.employee'].search([('job_id', '=', '面料仓仓管'), ('is_delete', '=', False)]).id
        accessories_name = self.env['hr.employee'].search([('job_id', '=', '面辅料主管'), ('is_delete', '=', False)]).id

        for material in material_summary_sheet_abnormal_info['message_content']:
            # if material['plan_dosage'] == 0:
            #     date = {
            #         "is_automatic": True,
            #         "declare_time": material_summary_sheet_abnormal_info['date'],
            #         "emp_id": technology_name,
            #         "record_type": "punish",
            #         "punish_type": "绩效",
            #         "matter_type": "production",
            #         "money_amount": 50,
            #         "record_matter": f"下单时间:{material['date']}，"
            #                          f"款号:{material['style_number']}，"
            #                          f"订单号:{material['order_id']}，bom物料计划用量为0，存在异常！",
            #     }
            #     self.sudo().create(date)

            if material['material_type'] == "面料":
                if material['actual_usage'] != 0 and material['plan_dosage'] != 0:
                    if material['actual_usage'] > material['plan_dosage']:
                       percentage_diff = material['actual_usage'] / material['plan_dosage']
                    elif material['actual_usage'] < material['plan_dosage']:
                       percentage_diff = -(material['actual_usage'] / material['plan_dosage'])
                    date = {
                        "is_automatic": True,
                        "declare_time": material_summary_sheet_abnormal_info['date'],
                        "emp_id": fabric_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{material['date']}，"
                                         f"款号:{material['style_number']}，"
                                         f"订单号:{material['order_id']}，bom面料实际用量大于或者小于计划用量的{round(percentage_diff, 2)}%，存在异常！",
                    }
                    self.sudo().create(date)
                    #print(date)

                # elif material['actual_usage'] == 0 and material['plan_dosage'] == 0:
                #     date = {
                #         "is_automatic": True,
                #         "declare_time": material_summary_sheet_abnormal_info['date'],
                #         "emp_id": fabric_name,
                #         "record_type": "punish",
                #         "punish_type": "绩效",
                #         "matter_type": "production",
                #         "money_amount": 50,
                #         "record_matter": f"下单时间:{material['date']}，"
                #                          f"款号:{material['style_number']}，"
                #                          f"订单号:{material['order_id']}，bom面料实际用量与计划用量的均为0，存在异常！",
                #     }
                #     self.sudo().create(date)

            if material['material_type'] == "辅料":
                if material['actual_usage'] != 0 and material['plan_dosage'] != 0:
                    if material['actual_usage'] > material['plan_dosage']:
                       percentage_diff = material['actual_usage'] / material['plan_dosage']
                    elif material['actual_usage'] < material['plan_dosage']:
                       percentage_diff = -(material['actual_usage'] / material['plan_dosage'])
                    date = {
                        "is_automatic": True,
                        "declare_time": material_summary_sheet_abnormal_info['date'],
                        "emp_id": accessories_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{material['date']}，"
                                         f"款号:{material['style_number']}，"
                                         f"订单号:{material['order_id']}，bom面料实际用量大于或者小于计划用量的{round(percentage_diff, 2)}%，存在异常！",
                    }
                    self.sudo().create(date)
                    #print(date)

                # elif material['actual_usage'] == 0 and material['plan_dosage'] == 0:
                #     date = {
                #         "is_automatic": True,
                #         "declare_time": material_summary_sheet_abnormal_info['date'],
                #         "emp_id": accessories_name,
                #         "record_type": "punish",
                #         "punish_type": "绩效",
                #         "matter_type": "production",
                #         "money_amount": 50,
                #         "record_matter": f"下单时间:{material['date']}，"
                #                          f"款号:{material['style_number']}，"
                #                          f"订单号:{material['order_id']}，bom面料实际用量与计划用量的均为0，存在异常！",
                #     }
                #     self.sudo().create(date)
    
    def bom_not_ticket_generation(self, generate_date):
        """bom采购数量和入库数量不符合罚单"""
        material_summary_sheet_datas = self.env["material_summary_sheet"].sudo().search([('order_id.is_finish','=','已完成')])

        # 查询各个负责人
        technology_name = self.env['hr.employee'].search([('job_id', '=', '技术部主管'), ('is_delete', '=', False)]).id
        fabric_name = self.env['hr.employee'].search([('job_id', '=', '面料仓仓管'), ('is_delete', '=', False)]).id
        accessories_name = self.env['hr.employee'].search([('job_id', '=', '面辅料主管'), ('is_delete', '=', False)]).id

        for material_summary_sheet_data in material_summary_sheet_datas:
            if abs(material_summary_sheet_data.enter_dosage - material_summary_sheet_data.actual_dosage) > 1:
                if material_summary_sheet_data.actual_dosage != 0 and material_summary_sheet_data.enter_dosage != 0:
                    ratio = (material_summary_sheet_data.enter_dosage - material_summary_sheet_data.actual_dosage) / material_summary_sheet_data.actual_dosage
                else:
                    ratio = 1
                if material_summary_sheet_data.material_type == "面料":
                    if material_summary_sheet_data.enter_dosage > material_summary_sheet_data.actual_dosage:
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": fabric_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，面料入库量{material_summary_sheet_data.enter_dosage}大于采购量{material_summary_sheet_data.actual_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
                    elif material_summary_sheet_data.enter_dosage < material_summary_sheet_data.actual_dosage:
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": fabric_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，面料入库量{material_summary_sheet_data.enter_dosage}小于采购量{material_summary_sheet_data.actual_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)

                if material_summary_sheet_data.material_type == "辅料":
                    if material_summary_sheet_data.enter_dosage > material_summary_sheet_data.actual_dosage:
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": accessories_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，辅料入库量{material_summary_sheet_data.enter_dosage}大于采购量{material_summary_sheet_data.actual_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
                    elif material_summary_sheet_data.enter_dosage < material_summary_sheet_data.actual_dosage:
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": accessories_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，辅料入库量{material_summary_sheet_data.enter_dosage}小于采购量{material_summary_sheet_data.actual_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
     
    
    def purchasing_not_equal_outbound_plus_inventory(self, generate_date):
        """bom采购数量不等于出库数+库存数罚单"""
        sale_pro_sale_pro_objs = self.env["sale_pro.sale_pro"].sudo().search([('is_finish','=','已完成')])
        material_summary_sheet_datas = self.env["material_summary_sheet"].sudo().search([('order_id.is_finish','=','已完成')])
        # 查询各个负责人
        fabric_name = self.env['hr.employee'].search([('job_id', '=', '面料仓仓管'), ('is_delete', '=', False)]).id
        accessories_name = self.env['hr.employee'].search([('job_id', '=', '面辅料主管'), ('is_delete', '=', False)]).id

        for material_summary_sheet_data in material_summary_sheet_datas:
            if material_summary_sheet_data.actual_dosage != (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage):
                if (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage) != 0:
                    ratio = (material_summary_sheet_data.actual_dosage - (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage)) / (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage)
                else:
                    ratio = 1
                if material_summary_sheet_data.material_type == "面料":
                    if material_summary_sheet_data.actual_dosage > (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage):
                        if (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage) != 0:
                            ratio = (material_summary_sheet_data.actual_dosage - (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage)) / (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage)
                        else:
                            ratio = 1
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": fabric_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，面料采购量{material_summary_sheet_data.actual_dosage}大于出库量{material_summary_sheet_data.outbound_dosage}加库存量{material_summary_sheet_data.inventory_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
                    elif material_summary_sheet_data.actual_dosage < (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage):
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": fabric_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，面料采购量{material_summary_sheet_data.actual_dosage}小于出库量{material_summary_sheet_data.outbound_dosage}加库存量{material_summary_sheet_data.inventory_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)

                if material_summary_sheet_data.material_type == "辅料":
                    if material_summary_sheet_data.actual_dosage > (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage):
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": accessories_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，辅料采购量{material_summary_sheet_data.actual_dosage}大于出库量{material_summary_sheet_data.outbound_dosage}加库存量{material_summary_sheet_data.inventory_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
                    elif material_summary_sheet_data.actual_dosage < (material_summary_sheet_data.inventory_dosage + material_summary_sheet_data.outbound_dosage):
                        #print('订单号:',material_summary_sheet_data.order_id.order_number,'款号:',material_summary_sheet_data.style_number.style_number,'面料入库量与采购量不符')
                        date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": accessories_name,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "production",
                            "money_amount": 50,
                            "record_matter": f"订单号:{material_summary_sheet_data.order_id.order_number}，款号:{material_summary_sheet_data.style_number.style_number}，辅料采购量{material_summary_sheet_data.actual_dosage}小于出库量{material_summary_sheet_data.outbound_dosage}加库存量{material_summary_sheet_data.inventory_dosage}的{round(ratio * 100, 2)}%，存在异常",
                        }
                        self.sudo().create(date)
                        #print(date)
               

    def recruitment_generated_ticked(self, generate_date):
        """三天内入职人数小于1人生成罚单"""
        has_no_onboarding_information = self.env["fsn_daily"].sudo().hr_has_no_onboarding_information()

        for onboarding in has_no_onboarding_information:
            date = {
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": onboarding['name'],
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": "三天入职人数小于1人，存在异常！",
            }
            self.sudo().create(date)

    def bom_warehouse_generates_ticket(self, generate_date):
        """bom生成罚单"""

        bom_exception = self.env['fsn_daily'].sudo().obtain_bom_exception_information()


        # 查询各个负责人
        fabric_name = self.env['hr.employee'].search([('job_id', '=', '面料仓仓管'), ('is_delete', '=', False)]).id
        accessories_name = self.env['hr.employee'].search([('job_id', '=', '面辅料主管'), ('is_delete', '=', False)]).id


        for bom in bom_exception['exception_list']:
            if bom['type'] == '面料':
                if bom['actual_usage'] != 0 and bom['outbound_dosage'] != 0:
                    if bom['actual_usage'] > bom['outbound_dosage']:
                       percentage_difference = bom['actual_usage'] / bom['outbound_dosage']
                    elif bom['actual_usage'] < bom['outbound_dosage']:
                       percentage_difference = -(bom['actual_usage'] / bom['outbound_dosage'])
                    date = {
                        "is_automatic": True,
                        "declare_time": generate_date,
                        "emp_id": fabric_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{bom['date_order']}，"
                                         f"款号:{bom['style_number']}，"
                                         f"订单号:{bom['order_id']}，bom面料实际用量大于或者小于出库用量的{round(percentage_difference, 2)}%，存在异常",
                    }
                    self.sudo().create(date)
                    #print(date)

                # elif bom['actual_usage'] == 0 and bom['outbound_dosage'] == 0:
                #     date = {
                #         "is_automatic": True,
                #         "declare_time": generate_date,
                #         "emp_id": fabric_name,
                #         "record_type": "punish",
                #         "punish_type": "绩效",
                #         "matter_type": "production",
                #         "money_amount": 50,
                #         "record_matter": f"下单时间:{bom['date_order']}，"
                #                          f"款号:{bom['style_number']}，"
                #                          f"订单号:{bom['order_id']}，bom物料实际用量与出库用量均为0，存在异常",
                #     }
                #     self.sudo().create(date)

            if bom['type'] == '辅料':
                if bom['actual_usage'] != 0 and bom['outbound_dosage'] != 0:
                    if bom['actual_usage'] > bom['outbound_dosage']:
                       percentage_difference = bom['actual_usage'] / bom['outbound_dosage']
                    elif bom['actual_usage'] < bom['outbound_dosage']:
                       percentage_difference = -(bom['actual_usage'] / bom['outbound_dosage'])
                    date = {
                        "is_automatic": True,
                        "declare_time": generate_date,
                        "emp_id": accessories_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{bom['date_order']}，"
                                         f"款号:{bom['style_number']}，"
                                         f"订单号:{bom['order_id']}，bom物料实际用量大于或者小于出库用量的{round(percentage_difference, 2)}%，存在异常",
                    }
                    self.sudo().create(date)
                    #print(date)
                    
                # elif bom['actual_usage'] == 0 and bom['outbound_dosage'] == 0:
                #     date = {
                #         "is_automatic": True,
                #         "declare_time": generate_date,
                #         "emp_id": fabric_name,
                #         "record_type": "punish",
                #         "punish_type": "绩效",
                #         "matter_type": "production",
                #         "money_amount": 50,
                #         "record_matter": f"下单时间:{bom['date_order']}，"
                #                          f"款号:{bom['style_number']}，"
                #                          f"订单号:{bom['order_id']}，bom物料实际用量与出库用量均为0，存在异常",
                #     }

                #     self.sudo().create(date)


    def nosignature_warehouse_generates_ticket(self, generate_date):
        ''' 总监未签名 自动生成罚单'''

        commissioner_name = self.env['hr.employee'].sudo().search([('job_id', '=', '生产总监'), ('is_delete', '=', False)]).id
        person_change = self.env['fsn_daily'].sudo().get_outsource_order_no_person_charge(generate_date)
        message_content = person_change["message_content"]
        if len(message_content) !=0:
            for message in message_content:
                date = {
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": commissioner_name,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": f"订单号:{message['order_number']}，外发订单未填写负责人！",
                }
                self.sudo().create(date)



    def abnormal_procurement_ticked(self, generate_date):
        """bom采购用量不等于库存量+出库量生成罚单"""
        # 查询各个负责人
        fabric_name = self.env['hr.employee'].search([('job_id', '=', '面料仓仓管'), ('is_delete', '=', False)]).id
        accessories_name = self.env['hr.employee'].search([('job_id', '=', '面辅料主管'), ('is_delete', '=', False)]).id

        abnormal_bom = self.env['fsn_daily'].sudo().abnormal_bom_procurement_usage()

        if len(abnormal_bom['abnormal_procurement']) > 0:
            for abnormal in abnormal_bom['abnormal_procurement']:
                if abnormal['type'] == '面料':
                    date = {
                        "is_automatic": True,
                        "declare_time": generate_date,
                        "emp_id": fabric_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{abnormal['date_order']}，"
                                         f"款号:{abnormal['style_number']}，"
                                         f"订单号:{abnormal['order_id']}，bom物料库存量与出库量之和不等于采购用量，存在异常！",
                    }
                    self.sudo().create(date)

                if abnormal['type'] == '辅料':
                    date = {
                        "is_automatic": True,
                        "declare_time": generate_date,
                        "emp_id": accessories_name,
                        "record_type": "punish",
                        "punish_type": "绩效",
                        "matter_type": "production",
                        "money_amount": 50,
                        "record_matter": f"下单时间:{abnormal['date_order']}，"
                                         f"款号:{abnormal['style_number']}，"
                                         f"订单号:{abnormal['order_id']}，bom物料库存量与出库量之和不等于采购用量，存在异常！",
                    }
                    self.sudo().create(date)

    def generate_penalty_from_original_unit_price(self, generate_date):
        """工时工序单价与工时单原单价不符生成罚单"""
        ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
                                                          limit=1, order="entry_time").id
        obtain_work = self.env['fsn_daily'].sudo().obtain_work_hours_operation()
        if len(obtain_work['result']) > 0 :
            for obtain in obtain_work['result']:
                data = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": ie_obj_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 50,
                    "record_matter": f"订单号：{obtain['order_no']}，款号：{obtain['style_number']}，工序号：{obtain['employee_id']}，"
                                     f"现场工序原单价：{obtain['standard_price']}，工时单原单价：{obtain['timesheet_standard_price']}，"
                                     f"现场工序原单价与工时单原单价不符，存在异常！"
                }
                self.sudo().create(data)

    def late_delivery_production_penalty(self, generate_date):
        """后道未交货生成罚单"""
        posterior_channel_supervisor_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "后道主管"), ("is_delete", "=", False)], limit=1, order="entry_time").id

        obtain_sub = self.env['fsn_daily'].sudo().obtain_subsequent_delivery_information()
        if len(obtain_sub) == 0:
            data = {
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": posterior_channel_supervisor_id,
                "record_type": "punish",
                "punish_type": "品控",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter":f"{generate_date},未查询到前一天后道交货记录"
            }
            self.sudo().create(data)

    def generate_penalty_note_for_process_quantity(self, generate_date):
        """现场工序数量与生产进度进度数量不匹配生成罚单"""
        ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
                                                          limit=1, order="entry_time").id

        number_working = self.env['fsn_daily'].sudo().number_of_working_hours_and_processes()
        if len(number_working['result']) > 0:
            for number in number_working['result']:
                print(number)
                data = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": ie_obj_id,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 50,
                    "record_matter": f"订单号:{number['order_number']},款号:{number['style_number']},"
                                     f"现场工序件数:{number['number_of_working_hours']}, "
                                     f"生产进度表数量:{number['production_progress_pieces']},现场工序件数与生产进度表数量不符,存在异常！"
                }
                self.sudo().create(data)


    def is_delete_staff_learder_ticket(self, today):
        ''' 每月组员离职自动处罚组长'''
        group_name_list = ['缝纫一组', '缝纫二组', '缝纫三组', '缝纫四组', '缝纫五组', '缝纫六组', '缝纫七组', '缝纫八组', '缝纫九组', '缝纫十组']
        first_day = datetime(today.year, today.month, 1)
        for group_name in group_name_list:
            leaders = self.env['hr.employee'].sudo().search([("department_id.name", "=", group_name), ("is_delete", "=", False), ("job_id.name", "=", "流水组长")]).id
            if not leaders:
                leaders = self.env['hr.employee'].sudo().search([("department_id.name", "=", group_name), ("is_delete_date", "<", today), ("is_delete_date", ">", first_day),("job_id.name", "=", "流水组长")]).id
            is_delete_staffs = self.env['hr.employee'].sudo().search([("department_id.name", "=", group_name), ("is_delete", "=", True), ("job_id.name", "!=", "流水组长"), ("is_delete_date", ">", first_day), ("is_delete_date", "<=", today)])
            if is_delete_staffs:
                for is_delete_staff in is_delete_staffs:
                    date = {
                    "is_automatic": True,
                    "declare_time": today,
                    "emp_id": leaders,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 100,
                    "record_matter": f"本月离职组员姓名:{is_delete_staff.name}！",
                    }
                    self.sudo().create(date)
                    #print(date)

    def generate_a_ticket_quantity_discrepancy(self, generate_date):
        """交货数与应交数不符处罚"""
        query_list = self.env['fsn_daily'].sudo().quantity_discrepancy()

        if len(query_list) > 0:
            for query in query_list:
                date = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": query['name'],
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 50,
                    "record_matter": f"订单号:{query['order_number']}，款号:{query['style_number']}，交货数:{query['delivery']}，应交数:{query['total']}，交货数与应交数不符,存在异常！",
                }
                self.sudo().create(date)

    def non_delivery_production_penalty(self, generate_date):
        """未交货处罚"""
        query_names = self.env['fsn_daily'].sudo().undelivered()
        print(len(query_names))
        if len(query_names) > 0:
            for query in query_names:
                date = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": query['name'],
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 100,
                    "record_matter": f"中查未交货，存在异常",
                }
                self.sudo().create(date)

    
    def no_material_summary_sheet(self,generate_date):
        """bom生产订单为0存在面辅料订单和采购订单"""
        employee_names = self.env['hr.employee'].sudo().search([("job_id.name", "=", '业务跟单'), ("is_delete", "=", False)], limit=1).id
        raw_materials_order_objs = self.env["raw_materials_order_home"].sudo().search([
            ("order_number_id", "!=", False), ("style_number_id", "!=", False),("order_number_id.is_finish", "=", '已完成')
            ])#面辅料订单明细里查询
        raw_materials_order_objs_style_number_ids = set(raw_materials_order_objs.mapped('style_number_id.style_number'))
        for raw_materials_order_objs_style_number_id in raw_materials_order_objs_style_number_ids:
            sale_pro_ids = self.env["sale_pro_line"].sudo().search([
            ("style_number.style_number", "=", raw_materials_order_objs_style_number_id)])
            if not sale_pro_ids:
                raw_materials_order_objs = self.env["raw_materials_order_home"].sudo().search([("style_number_id.style_number", "=", raw_materials_order_objs_style_number_id)], limit=1)
                #print('存在无生产订单的面辅料订单', raw_materials_order_objs_style_number_id,raw_materials_order_objs.order_number_id.order_number)
                date = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": employee_names,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 50,
                    "record_matter": f"存在无生产订单的面辅料订单，订单号:{raw_materials_order_objs.order_number_id.order_number}，款号:{raw_materials_order_objs_style_number_id}",
                }
                self.sudo().create(date)
                #print(date)
 
        fabric_ingredients_procurements = self.env["fabric_ingredients_procurement"].sudo().search([
            ("order_id", "!=", False), ("style_number", "!=", False),("order_id.is_finish", "=", '已完成')
            ])#采购订单明细里查询
        fabric_ingredients_procurements_number_ids = set(fabric_ingredients_procurements.mapped('style_number.style_number'))
        for fabric_ingredients_procurements_number_id in fabric_ingredients_procurements_number_ids:
            sale_pro_ids = self.env["sale_pro_line"].sudo().search([
            ("style_number.style_number", "=", fabric_ingredients_procurements_number_id)])
            plus_material_inventory_objs = self.env["plus_material_inventory"].sudo().search([("style_number.style_number", "=", raw_materials_order_objs_style_number_id)])
            warehouse_bom_inventory_objs = self.env["warehouse_bom_inventory"].sudo().search([("style_number.style_number", "=", raw_materials_order_objs_style_number_id)])
            if not sale_pro_ids and not plus_material_inventory_objs and not warehouse_bom_inventory_objs:
                fabric_ingredients_procurements_number_data = self.env["fabric_ingredients_procurement"].sudo().search([("style_number.style_number", "=", fabric_ingredients_procurements_number_id)], limit=1)
                #print('存在无生产订单的采购订单', fabric_ingredients_procurements_number_data.order_id.order_number,fabric_ingredients_procurements_number_id)
                date = {
                    "is_automatic": True,
                    "declare_time": generate_date,
                    "emp_id": employee_names,
                    "record_type": "punish",
                    "punish_type": "绩效",
                    "matter_type": "production",
                    "money_amount": 50,
                    "record_matter": f"存在无生产订单的采购订单，订单号:{fabric_ingredients_procurements_number_data.order_id.order_number}，款号:{fabric_ingredients_procurements_number_id}",
                }
                self.sudo().create(date)
                #print(date)

    def general_middle_check_month_efficiency(self,generate_date):
        """中查总检罚款"""
        year, month, _ = str(generate_date.date()).split("-")
        year_month = f"{year}-{month}"
        invest_punish = self.env['middle_check_month_efficiency'].sudo().search([('month', '=', year_month)])
        invest_names = set(invest_punish.mapped('invest'))
        for invest_name in invest_names:
            invest_name_id = self.env['hr.employee'].sudo().search([('name', '=', invest_name)])
            if invest_name_id:
                invest_name_punishs = self.env['middle_check_month_efficiency'].sudo().search([('month', '=', year_month),('invest', '=', invest_name)])
                punish_datas = sum(invest_name_punishs.mapped('punishment'))
                if not punish_datas == 0:
                    date = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": invest_name_id.id,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "qulity_control",
                            "money_amount": punish_datas,
                            "record_matter": f"漏查处罚",
                        }
                    self.sudo().create(date)
                    #print(date)
                    #print(punish_datas,invest_name_id.name)
        
        general_punish = self.env['general_inspection_month_efficiency'].sudo().search([('month', '=', year_month)])
        general_names = set(general_punish.mapped('general_ids.general1'))
        for general_name in general_names:
            general_name_id = self.env['hr.employee'].sudo().search([('name', '=', general_name)])
            if general_name_id:
                general_name_punishs = self.env['general_inspection_month_efficiency'].sudo().search([('month', '=', year_month),('general_ids.general1', '=', general_name)])
                general_punish_datas = sum(general_name_punishs.mapped('punishment'))
                if not general_punish_datas == 0:
                    dates = {
                            "is_automatic": True,
                            "declare_time": generate_date,
                            "emp_id": general_name_id.id,
                            "record_type": "punish",
                            "punish_type": "绩效",
                            "matter_type": "qulity_control",
                            "money_amount": general_punish_datas,
                            "record_matter": f"漏查处罚",
                        }
                    self.sudo().create(dates)
                    #print(dates)
                    #print(general_punish_datas,general_name_id.name)


    def no_efficiency_generation_of_tickets(self, generate_date):
        """	手动效率<0.1,处罚工时IE50元"""

        eff_eff_obgs = self.env["eff.eff"].sudo().search([('date', '=', generate_date - timedelta(days=2))])
        tatol = sum(eff_eff_obgs.mapped('totle_eff'))/len(eff_eff_obgs)
        print(tatol)
        # 查询IE
        ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
                                                          limit=1, order="entry_time").id
        if tatol < 0.1:
            date_time = generate_date - timedelta(days=1)
            date_str = date_time.strftime("%Y-%m-%d")
            data = {
                "is_automatic": True,
                "declare_time": generate_date,
                "emp_id": ie_obj_id,
                "record_type": "punish",
                "punish_type": "绩效",
                "matter_type": "production",
                "money_amount": 50,
                "record_matter": f"{date_str}，手工效率小于0.1，存在异常！",
            }
            self.sudo().create(data)
            print(data)
  

        # # 构建本月第一天的日期
        # first_day_of_month = datetime(generate_date.year, generate_date.month, 1)
        # date_times = first_day_of_month
        # while date_times < (generate_date - timedelta(days=2)):
        #     eff_eff_obgs = self.env["eff.eff"].sudo().search([('date', '=', date_times)])
        #     if eff_eff_obgs:
        #         tatol = sum(eff_eff_obgs.mapped('totle_eff'))/len(eff_eff_obgs)
        #         # 查询IE
        #         ie_obj_id = self.env["hr.employee"].sudo().search([("job_id.name", "=", "工时IE"), ("is_delete", "=", False)],
        #                                                         limit=1, order="entry_time").id
        #         if tatol < 0.1:
        #             date_str = date_times.strftime("%Y-%m-%d")
        #             data = {
        #                 "is_automatic": True,
        #                 "declare_time": generate_date,
        #                 "emp_id": ie_obj_id,
        #                 "record_type": "punish",
        #                 "punish_type": "绩效",
        #                 "matter_type": "production",
        #                 "money_amount": 50,
        #                 "record_matter": f"{date_str}，手工效率小于0.1，存在异常！",
        #             }
        #             self.sudo().create(data)
        #             #print(data)
        #     date_times += timedelta(days=1)




    # 手动生成奖罚记录单
    def performed_manually(self, today=None):

        if today:
            today = str(today)
            generate_date = datetime.strptime(today, "%Y-%m-%d").date()
        else:
            generate_date = fields.datetime.now().date()


        # self.day_qing_day_bi_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________1')
        # self.middle_check_day_leak_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________2')
        # self.always_check_omission_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________3')
        # self.fsn_daily_examine_customer_delivery_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________4')
        # self.fsn_daily_day_qing_day_bi_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________5')
        # self.fsn_daily_day_cycle_get_plan_set_messages(generate_date)
        # _logger.info(f'{generate_date}_________6')
        # self.fsn_daily_statistical_summary_set_messages(generate_date)
        # _logger.info(f'{generate_date}_________7')
        # self.based_on_group_statistical_abnormal_data(generate_date)
        # _logger.info(f'{generate_date}_________8')
        # self.sales_order_no_month_plan(generate_date)
        # _logger.info(f'{generate_date}_________9')
        # self.bom_material_summary_sheet_abnormal_info(generate_date)
        # _logger.info(f'{generate_date}_________10')
        # self.fsn_daily_get_monthly_plan_abnormal_messages_content(generate_date)
        # _logger.info(f'{generate_date}_________11')
        # self.fsn_daily_after_sales_return_goods(generate_date)
        # _logger.info(f'{generate_date}_________12')

        self.outsource_order_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________13')
        self.encapsulation_dg_production_value_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________14')
        # self.general_inspection_abnormal_info_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________15')
        self.get_client_ware_customer_return_info_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________16')
        self.get_examine_customer_delivery_time_messages_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________17')
        self.get_prenatal_preparation_progress_anomaly_info_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________18')
        # self.get_time_limit_not_recruitment_record_automatic_reward_punish_record(generate_date)
        # _logger.info(f'{generate_date}_________19')
        self.get_monthly_plan_overdue_info_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________20')
        self.get_group_efficiency_exception_record_automatic_reward_punish_record(generate_date)
        _logger.info(f'{generate_date}_________21')
        self.get_first_eight_pieces_abnormal_info(generate_date)
        _logger.info(f'{generate_date}_________22')
        self.get_performance_appraisal_data(generate_date)
        _logger.info(f"{generate_date}_________23")
        self.get_sale_order_not_paid_record_automatic_reward_punish_record(generate_date)
        _logger.info(f"{generate_date}_________24")
        self.suspend_and_generate_a_ticket(generate_date)
        _logger.info(f"{generate_date}_________25")
        self.manual_efficiency_generation_of_tickets(generate_date)
        _logger.info(f"{generate_date}_________26")
        self.bom_ticket_generation(generate_date)
        _logger.info(f"{generate_date}_________27")
        self.recruitment_generated_ticked(generate_date)
        _logger.info(f"{generate_date}_________28")
        self.bom_warehouse_generates_ticket(generate_date)
        _logger.info(f"{generate_date}_________29")
        self.nosignature_warehouse_generates_ticket(generate_date)
        _logger.info(f"{generate_date}_________30")
        self.abnormal_procurement_ticked(generate_date)
        _logger.info(f"{generate_date}_________31")
        self.generate_penalty_from_original_unit_price(generate_date)
        _logger.info(f"{generate_date}_________32")
        self.generate_penalty_note_for_process_quantity(generate_date)
        _logger.info(f"{generate_date}_________33")
        self.generate_a_ticket_quantity_discrepancy(generate_date)
        _logger.info(f"{generate_date}_________34")
        self.no_material_summary_sheet(generate_date)
        _logger.info(f"{generate_date}_________35")
        # self.no_efficiency_generation_of_tickets(generate_date)
        # _logger.info(f"{generate_date}_________36")
        return True



