from odoo import models, fields, api
import datetime


import calendar

import itertools


class FsnDaily(models.TransientModel):
    _inherit = "fsn_daily"


    def set_outsource_order_delay_time_info(self, today):
        ''' 外发误期异常信息'''

        abnormal_list = []
        outsource_order_objs = self.env['outsource_order'].sudo().search([
            ("approval_state", "=", "待审批"),
            ("state", "not in", ['已完成', '退单']),
            ("responsible_person", "!=", False),
            ("customer_delivery_time", "<", today)
        ], order='customer_delivery_time desc')

        for outsource_order_obj in outsource_order_objs:

            days = (today - outsource_order_obj.customer_delivery_time).days

            difference = outsource_order_obj.order_quantity - outsource_order_obj.stock

            abnormal_list.append({
                "date_order": outsource_order_obj.order_id.date,
                "contract_date": outsource_order_obj.customer_delivery_time,
                "responsible_person": outsource_order_obj.responsible_person.name,
                "processing_plant": outsource_order_obj.outsource_plant_id.name,
                "order_number": outsource_order_obj.order_id.order_number,
                "order_quantity": outsource_order_obj.order_quantity,
                "actual_delivered_quantity": outsource_order_obj.actual_delivered_quantity,
                "stock": outsource_order_obj.stock,
                "defective_goods": outsource_order_obj.defective_number,
                "number": difference,
                "overdue": days,
            })
        
        return {"date": today, "message_content": abnormal_list}


    def get_client_ware_customer_return_info(self, today):
        ''' 获取客仓客户退货信息'''
        old_today = today - datetime.timedelta(days=7)
        abnormal_list = []

        client_ware_objs = self.env['client_ware'].sudo().search([("dDate", ">=", old_today), ("check_type", "=", "客户")])

        for client_ware_obj in client_ware_objs:

            abnormal_list.append({
                "dDate": client_ware_obj.dDate,
                "customer_delivery_time": client_ware_obj.order_number.customer_delivery_time,
                "gGroup": client_ware_obj.gGroup,
                "order_number": client_ware_obj.order_number.order_number,
                "style_number": client_ware_obj.style_number.style_number,
                "repair_number": client_ware_obj.repair_number
            })

        return {"date": today, "message_content": abnormal_list}


    def get_day_plan_abnormal_info(self, today):
        ''' 获取日计划异常信息'''

        abnormal_list = []

        planning_slot_objs = self.env['planning.slot'].sudo().search([("dDate", ">=", "2022-10-01"),("lock_state", "=", "未审批")], order='dDate')

        for date, date_planning_slot_objs in itertools.groupby(planning_slot_objs, key=lambda x:x.dDate):

            date_planning_slot_objs = list(date_planning_slot_objs)
            date_planning_slot_objs.sort(key=lambda x: x.department_id, reverse=False)

            date_plan_info_dict = {}

            for department, department_planning_slot_objs in itertools.groupby(date_planning_slot_objs, key=lambda x:x.department_id):

                def get_plan_output_value_data(objs, staff_group):
                    ''' 获取当天各部门计划总产值数据'''

                    people_list = []
                    output_value = 0
                    plan_stage = ""
                    style_number = []
                    plan_number = 0

                    for obj in objs:
                        people_list.append(obj.number_people)
                        output_value += obj.plan_output_value
                        plan_number += obj.plan_number
                        if not plan_stage:
                            plan_stage = obj.plan_stage
                        else:
                            if plan_stage == "开款第一天":
                                pass
                            elif plan_stage == "正常":
                                if obj.plan_stage in ["开款第一天", "开款第二天"]:
                                    plan_stage = obj.plan_stage
                            elif plan_stage == "开款第二天":
                                if obj.plan_stage == "开款第一天":
                                    plan_stage = obj.plan_stage

                        style_number.append(obj.style_number.style_number_base_id.name)
                    
                    number_people = max(people_list, default=0)

                    return {
                        "staff_group": staff_group,
                        "number_people": number_people,
                        "output_value": output_value,
                        "plan_stage": plan_stage,
                        "plan_number": plan_number,
                        "style_number": " ".join(set(style_number))
                    }
                
                if department == "车间":

                    department_planning_slot_objs = list(department_planning_slot_objs)
                    department_planning_slot_objs.sort(key=lambda x: x.staff_group, reverse=False)

                    staff_group_plan_info_list = []

                    for staff_group, staff_group_planning_slot_objs in itertools.groupby(department_planning_slot_objs, key=lambda x:x.staff_group):

                        staff_group_plan_info_list.append(get_plan_output_value_data(staff_group_planning_slot_objs, staff_group))

                    for staff_group_plan_info_record in staff_group_plan_info_list:

                        if staff_group_plan_info_record["number_people"]:
                            plan_value_avg = (staff_group_plan_info_record["output_value"] / staff_group_plan_info_record["number_people"])
                        else:
                            plan_value_avg = 0

                        if staff_group_plan_info_record['plan_stage'] == "开款第一天":
                            if plan_value_avg < 450:
                                abnormal_list.append({
                                    "date": date,   # 日期
                                    "group_name": staff_group_plan_info_record['staff_group'],   # 组别
                                    "num_people": staff_group_plan_info_record["number_people"],     # 人数
                                    "style_number_base": staff_group_plan_info_record['style_number'],   # 款号
                                    "plan_stage": staff_group_plan_info_record["plan_stage"],    # 计划阶段
                                    "plan_value_sum": format(plan_value_avg, '0.2f'),    # 人均产值
                                })
                        elif staff_group_plan_info_record['plan_stage'] == "开款第二天":
                            if plan_value_avg < 500:
                                abnormal_list.append({
                                    "date": date,   # 日期
                                    "group_name": staff_group_plan_info_record['staff_group'],   # 组别
                                    "num_people": staff_group_plan_info_record["number_people"],     # 人数
                                    "style_number_base": staff_group_plan_info_record['style_number'],   # 款号
                                    "plan_stage": staff_group_plan_info_record["plan_stage"],    # 计划阶段
                                    "plan_value_sum": format(plan_value_avg, '0.2f'),    # 人均产值
                                })
                        elif staff_group_plan_info_record['plan_stage'] == "正常":
                            if plan_value_avg < 560:
                                abnormal_list.append({
                                    "date": date,   # 日期
                                    "group_name": staff_group_plan_info_record['staff_group'],   # 组别
                                    "num_people": staff_group_plan_info_record["number_people"],     # 人数
                                    "style_number_base": staff_group_plan_info_record['style_number'],   # 款号
                                    "plan_stage": staff_group_plan_info_record["plan_stage"],    # 计划阶段
                                    "plan_value_sum": format(plan_value_avg, '0.2f'),    # 人均产值
                                })


                    date_plan_info_dict[department] = get_plan_output_value_data(department_planning_slot_objs, False)
                else:
                    date_plan_info_dict[department] = get_plan_output_value_data(department_planning_slot_objs, False)
                
                

            if "车间" in date_plan_info_dict:
                cutting_machine_group_plan_total_value = date_plan_info_dict["车间"]["output_value"] * 1.5

                # posterior_channel_group_plan_total_value = date_plan_info_dict["车间"]["output_value"] * 2.0

                if "裁床" in  date_plan_info_dict:
                    if date_plan_info_dict["裁床"]["output_value"] < cutting_machine_group_plan_total_value:
                        
                        abnormal_list.append({
                            "date": date,   # 日期
                            "group_name": "裁床",   # 组别
                            "num_people": date_plan_info_dict["裁床"]["number_people"],     # 人数
                            "style_number_base": date_plan_info_dict["裁床"]["style_number"],   # 款号
                            "plan_stage": date_plan_info_dict["裁床"]["plan_stage"],    # 计划阶段
                            "plan_total_value": format(date_plan_info_dict["裁床"]["output_value"], '0.2f'),      # 总产值
                            "group_plan_total_value": format(cutting_machine_group_plan_total_value, '0.2f')   # 组上总产值
                        })

                if "后道" in  date_plan_info_dict:

                    if (date_plan_info_dict["后道"]["number_people"] * 100) > date_plan_info_dict["后道"]["plan_number"]:

                        abnormal_list.append({
                            "date": date,   # 日期
                            "group_name": "后道",   # 组别
                            "num_people": date_plan_info_dict["后道"]["number_people"],     # 人数
                            "style_number_base": date_plan_info_dict["后道"]["style_number"],   # 款号
                            "plan_stage": date_plan_info_dict["后道"]["plan_stage"],    # 计划阶段
                            "plan_number": date_plan_info_dict["后道"]["plan_number"],    # 件数
                        })
                    
                    # if date >= datetime.date(2023, 4, 18):

                    #     if date_plan_info_dict["后道"]["output_value"] < posterior_channel_group_plan_total_value:

                    #         abnormal_list.append({
                    #             "date": date,   # 日期
                    #             "group_name": "后道",   # 组别
                    #             "num_people": date_plan_info_dict["后道"]["number_people"],     # 人数
                    #             "style_number_base": date_plan_info_dict["后道"]["style_number"],   # 款号
                    #             "plan_stage": date_plan_info_dict["后道"]["plan_stage"],    # 计划阶段
                    #             "plan_total_value": format(date_plan_info_dict["后道"]["output_value"], '0.2f'),      # 总产值
                    #             "group_plan_total_value": format(posterior_channel_group_plan_total_value, '0.2f')   # 组上总产值
                    #         })

                    # else:

                    #     if date_plan_info_dict["后道"]["output_value"] < cutting_machine_group_plan_total_value:

                    #         abnormal_list.append({
                    #             "date": date,   # 日期
                    #             "group_name": "后道",   # 组别
                    #             "num_people": date_plan_info_dict["后道"]["number_people"],     # 人数
                    #             "style_number_base": date_plan_info_dict["后道"]["style_number"],   # 款号
                    #             "plan_stage": date_plan_info_dict["后道"]["plan_stage"],    # 计划阶段
                    #             "plan_total_value": format(date_plan_info_dict["后道"]["output_value"], '0.2f'),      # 总产值
                    #             "group_plan_total_value": format(cutting_machine_group_plan_total_value, '0.2f')   # 组上总产值
                    #         })
        

        return {"date": today, "message_content": abnormal_list}
    


    def get_general_inspection_abnormal_info(self, today):
        ''' 获取总检产量和吊挂异常信息'''

        today -= datetime.timedelta(days=1)
        while True:
            general_objs = self.env['general.general'].sudo().read_group(
                domain=[("date", "=", today)],
                fields=["general_number", "repair_number"],# 查获数   返修数
                groupby="general1"
            )
            if general_objs:
                break
            else:
                today -= datetime.timedelta(days=1)
        
        for general_obj in general_objs:

            check_position_settings_obj = self.env['check_position_settings'].sudo().search([("group", "=", "后整")])
            general_position_list = check_position_settings_obj.position_line_ids.filtered(lambda x: x.type == "总检").mapped("position")

            suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                ("dDate", "=", today),
                ("employee_id.name", "=", general_obj['general1']),
                ("station_number", "in", general_position_list)
            ])#吊挂查获数
            
            suspension_system_rework_objs = self.env['suspension_system_rework'].sudo().search([
                ('date', "=", today),
                ("qc_employee_id.name", "=", general_obj['general1']),
                ("qc_type", "=", "总检")
            ])#吊挂返修数
            
            general_obj['dg_general_number'] = sum(suspension_system_station_summary_objs.mapped("total_quantity"))
            general_obj['dg_repair_number'] = sum(suspension_system_rework_objs.mapped("few_number"))
    
        return {"date": today, "message_content": general_objs}
       
    

    def get_prenatal_preparation_progress_anomaly_info(self, today):
        ''' 获取产前准备进度表异常信息'''

        # tomorrow = today + datetime.timedelta(days=1)

        current_date  = datetime.datetime.now()

        year_start_date = datetime.datetime(current_date.year, 1, 1)

        previous_day = current_date - datetime.timedelta(days=1)

        abnormal_list = []

        fsn_month_plan_objs = self.env['fsn_month_plan'].sudo().search([("plan_online_date", ">=", year_start_date.date()),
                                                                        ("plan_online_date", "<=", previous_day.date())])

        for i in fsn_month_plan_objs:

            if i.style_number.style_number.split("-")[1] == "3":
                continue

            prenatal_preparation_progress_obj = self.env['prenatal_preparation_progress'].sudo().search([("order_number", "=", i.order_number.id), ("style_number", "=", i.style_number.id)])

            temp_list = []
            if not prenatal_preparation_progress_obj.is_sample_dress:   # 样衣
                temp_list.append("样衣")

            if not prenatal_preparation_progress_obj.is_sample_dress:   # 样板
                temp_list.append("样板")

            if not prenatal_preparation_progress_obj.is_sample_dress:   # 工艺单
                temp_list.append("工艺单")

            if not prenatal_preparation_progress_obj.is_sample_dress:   # 单件用量
                temp_list.append("单件用量")

            if temp_list:
                abnormal_list.append({"订单号": i.order_number.order_number, "款号": i.style_number.style_number, "demo_list": temp_list})
        return {"date": today, "message_content": abnormal_list}
    



    def get_monthly_plan_overdue_info(self, today):
        ''' 获取月计划 逾期信息'''

        # 日期增加一天（下一天）
        query_date = today

        abnormal_list = []
    
        fsn_month_plan_info_list = self.env["fsn_month_plan"].sudo().search([
            ("fsn_staff_team_id.type", "=", "车间"),
            ("customer_delivery_time", "<=", query_date),
            ("order_number.processing_type", "!=", "返修"),
            ("lock_state", "=", "未审批")], order="customer_delivery_time desc")
        
        
        for fsn_month_plan_info in fsn_month_plan_info_list:

            schedule_production_objs = self.env['schedule_production'].sudo().search([
                ("order_number", "=", fsn_month_plan_info.order_number.id),
                ("style_number", "=", fsn_month_plan_info.style_number.id),
                ("lock_state", "=", "未审批")
            ])

            temp_dict = {
                    "customer_delivery_time": fsn_month_plan_info.customer_delivery_time,   # 客户货期
                    "order_number": fsn_month_plan_info.order_number.order_number,  # 订单号
                    "style_number": fsn_month_plan_info.style_number.style_number,  # 款号
                    "group": fsn_month_plan_info.fsn_staff_team_id.name,    # 组别
                }

            difference_delivery = sum(schedule_production_objs.mapped("difference_delivery"))
            if difference_delivery:
                temp_dict['difference_delivery'] = difference_delivery
            else:
                temp_dict['difference_delivery'] = 0

            factory_delivery_variance = sum(schedule_production_objs.mapped("factory_delivery_variance"))
            if factory_delivery_variance:
                temp_dict['factory_delivery_variance'] = factory_delivery_variance
            else:
                temp_dict['factory_delivery_variance'] = 0

            if temp_dict['difference_delivery'] or temp_dict['factory_delivery_variance']:
                abnormal_list.append(temp_dict)

        return {"date": today, "message_content": abnormal_list}
    


    def get_group_efficiency_exception_record(self, today):
        ''' 获取各组效率异常记录'''

        start_date = datetime.date(today.year, today.month, 1)

        abnormal_list = []

        objs_list= self.env['automatic_efficiency_table'].sudo().read_group(
            domain=[("date", ">=", start_date), ("date", "<", today), ("work_type", "not like", "B级管理"), ("group.group", 'like', "车缝")],
            fields=["group", "efficiency"],
            groupby=['group']
        )

        for i in objs_list:

            efficiency = float("{:.2f}".format(i['efficiency']))

            if efficiency < 50:
                abnormal_list.append({"group": str(i['group'][-1]), "efficiency": efficiency})
                
        return {"date": today, "message_content": abnormal_list}
    
    


    def get_first_eight_pieces_abnormal_info(self, today):
        ''' 获取首八件异常信息'''

        query_date = today - datetime.timedelta(days=2)

        abnormal_list = []
    
        fsn_month_plan_objs = self.env["fsn_month_plan"].sudo().search([
            ("plan_online_date", "=", query_date),
            ("order_number.processing_type", "!=", "返修"),
            ("lock_state", "=", "未审批")], order="customer_delivery_time desc")
        
        # for fsn_month_plan_obj in fsn_month_plan_objs:
        #     if fsn_month_plan_obj.style_number.style_number.split("-")[1] == "3":
        #         continue

        for fsn_month_plan_obj in fsn_month_plan_objs:
            style_number_parts = fsn_month_plan_obj.style_number.style_number.split('-')
            if len(style_number_parts) >= 2 and style_number_parts[1] == "3":
                continue


            if not self.env['first_eight_pieces'].sudo().search([
                ("order_number", "=", fsn_month_plan_obj.order_number.id),
                ("style_number", "=", fsn_month_plan_obj.style_number.id)
            ]):
                abnormal_list.append({
                    "customer_delivery_time": fsn_month_plan_obj.customer_delivery_time,
                    "order_number": fsn_month_plan_obj.order_number.order_number,
                    "style_number": fsn_month_plan_obj.style_number.style_number,
                    "plan_online_date": fsn_month_plan_obj.plan_online_date
                })
        print(abnormal_list)
        return {"date": today, "message_content": abnormal_list}
    

    def get_material_summary_sheet_abnormal_info2(self, today):
        ''' 获取物料用量 计划用量和实际用量异常记录'''
        material_summary_sheet_objs = self.env['material_summary_sheet'].sudo().search([("date_contract", "!=", False),
                                                                                        ("date_order", ">=", "2023-07-01"),
                                                                                        ('state', '=', '未确认')])
        
        abnormal_list = []
        for i in material_summary_sheet_objs:

            if i.style_number.style_number.split("-")[1] in ["3", "4"]:
                continue

            if (i.actual_dosage > (i.plan_dosage + i.plan_dosage * 0.003)) or (i.actual_dosage < (i.plan_dosage - i.plan_dosage * 0.003)):
                abnormal_list.append({
                    'date': i.date_order,
                    "date_contract": i.date_contract,
                    "order_id": i.order_id.order_number,
                    "style_number": i.style_number.style_number,
                    "material_name": i.material_name,
                    "material_type": i.material_type,
                    "plan_dosage": i.plan_dosage,

                    "actual_usage": i.actual_usage,
                    "actual_dosage": i.actual_dosage,
                })

        return {"date": today, "message_content": abnormal_list}
    
    
    def get_outsource_order_no_person_charge(self, today):
        ''' 获取外发订单 无负责人的记录'''

        outsource_order_objs = self.env['outsource_order'].sudo().sudo().search([("date", ">=", "2023-01-01"), ("responsible_person", "=", False)])
        abnormal_list = []

        for i in outsource_order_objs:
            abnormal_list.append({
                "customer_delivery_time": i.customer_delivery_time,
                "order_number": i.order_id.order_number,
            })
            print(abnormal_list)
        return {"date": today, "message_content": abnormal_list}