from odoo import api, fields, models
from odoo.exceptions import ValidationError


import datetime


class SaleProLine(models.Model):
    _inherit = "sale_pro_line"



    def create_fsn_month_plan(self):
        ''' 创建月计划'''

        fsn_month_plan_obj = self.env['fsn_month_plan'].sudo().search([
            ("month", "=", str(self.sale_pro_id.date)[0:7]),
            ("order_number", "=", self.sale_pro_id.id),
            ("style_number", "=", self.style_number.id),
        ])
        if not fsn_month_plan_obj:

            plan_online_date = self.sale_pro_id.date + datetime.timedelta(days=5)

            if self.sale_pro_id.production_group_ids:

                for production_group_obj in self.sale_pro_id.production_group_ids:

                    days_num = 0

                    if len(self.sale_pro_id.production_group_ids) == 1:
                        plan_number = self.voucher_count

                        if production_group_obj.department_id:
                            people_number = self.env['hr.employee'].sudo()\
                                .search_count([("department_id", "=", production_group_obj.department_id.id), ("is_delete", "=", False), ("is_it_a_temporary_worker", "not in", ['正式工(B级管理)', '正式工(A级管理)'])])

                            # 测试
                            if people_number != 0:
                                days_num = (float(self.sale_pro_id.order_price) * self.sale_pro_id.sum_voucher_count) / (560 * people_number * 1.3)
                        else:
                            people_number = 0 

                    else:
                        plan_number = 0
                        people_number = 0


                    days_num = int(days_num + 1)

                    planned_completion_date = plan_online_date + datetime.timedelta(days=days_num)

                    self.env['fsn_month_plan'].sudo().create({
                        "month": str(self.sale_pro_id.date)[0:7],   # 月份
                        "fsn_staff_team_id": production_group_obj.id,     # 组别
                        "people_number": people_number,     # 人数
                        "order_number": self.sale_pro_id.id,    # 订单id
                        "style_number": self.style_number.id,      # 款号
                        "style": self.sale_pro_id.product_name,     # 款式
                        "plan_online_date": plan_online_date,   # 计划上线日期
                        "plan_number": plan_number,   # 计划数量
                        "production_delivery_time": planned_completion_date     # 计划完成日期
                    })

            else:

                planned_completion_date = plan_online_date + datetime.timedelta(days=1)

                self.env['fsn_month_plan'].sudo().create({
                    "month": str(self.sale_pro_id.date)[0:7],   # 月份
                    "fsn_staff_team_id": False,     # 组别
                    "people_number": 0,     # 人数
                    "order_number": self.sale_pro_id.id,    # 订单id
                    "style_number": self.style_number.id,      # 款号
                    "style": self.sale_pro_id.product_name,     # 款式
                    "plan_online_date": plan_online_date,   # 计划上线日期
                    "plan_number": 0,   # 计划数量
                    "production_delivery_time": planned_completion_date     # 计划完成日期
                })







    @api.model
    def create(self, vals):
        res = super(SaleProLine,self).create(vals)

        res.create_fsn_month_plan()

        return res






class FsnMonthPlan(models.Model):
    _inherit = 'fsn_month_plan'


    def automatic_generation_month_plan(self):
        ''' 自动生成月计划'''

        current_date = fields.Datetime.now()

        current_date = current_date - datetime.timedelta(days=30)

        sale_pro_objs = self.env['sale_pro.sale_pro'].sudo().search([("is_finish", "not in", ['已完成', '退单']), ("create_date", ">=", current_date)])

        for sale_pro_obj in sale_pro_objs:

            if not self.env['fsn_month_plan'].sudo().search([("order_number", "=", sale_pro_obj.id)]):

                for sale_pro_obj_line in sale_pro_obj.sale_pro_line_ids:

                    people_number = 0

                    plan_online_date = sale_pro_obj.date + datetime.timedelta(days=5)

                    if len(sale_pro_obj.production_group_ids) >= 1:

                        for fsn_staff_team_obj in sale_pro_obj.production_group_ids:
                            
                            if fsn_staff_team_obj.department_id:
                                people_number = self.env['hr.employee'].sudo()\
                                    .search_count([("department_id", "=", fsn_staff_team_obj.department_id.id), ("is_delete", "=", False), ("is_it_a_temporary_worker", "not in", ['正式工(B级管理)', '正式工(A级管理)'])])

                            days_num = 0
                            if len(sale_pro_obj.production_group_ids) == 1:
                                days_num = (float(sale_pro_obj.order_price) * sale_pro_obj.sum_voucher_count) / (560 * people_number * 1.3)
                            days_num = int(days_num + 1)

                            planned_completion_date = plan_online_date + datetime.timedelta(days=days_num)

                            self.env['fsn_month_plan'].sudo().create({
                                "month": str(sale_pro_obj.date)[0:7],   # 月份
                                "fsn_staff_team_id": fsn_staff_team_obj.id,     # 组别
                                "people_number": people_number,     # 人数
                                "order_number": sale_pro_obj.id,    # 订单id
                                "style_number": sale_pro_obj_line.style_number.id,      # 款号
                                "style": sale_pro_obj.product_name,     # 款式
                                "plan_online_date": plan_online_date,   # 计划上线日期
                                "plan_number": sale_pro_obj_line.voucher_count if len(sale_pro_obj.production_group_ids) <= 1 else 0,   # 计划数量
                                "production_delivery_time": planned_completion_date     # 计划完成日期
                            })
                    
                    else:

                        days_num = 1

                        planned_completion_date = plan_online_date + datetime.timedelta(days=days_num)

                        self.env['fsn_month_plan'].sudo().create({
                            "month": str(sale_pro_obj.date)[0:7],   # 月份
                            "people_number": people_number,     # 人数
                            "order_number": sale_pro_obj.id,    # 订单id
                            "style_number": sale_pro_obj_line.style_number.id,      # 款号
                            "style": sale_pro_obj.product_name,     # 款式
                            "plan_online_date": plan_online_date,   # 计划上线日期
                            "plan_number": sale_pro_obj_line.voucher_count if len(sale_pro_obj.production_group_ids) <= 1 else 0,   # 计划数量
                            "production_delivery_time": planned_completion_date     # 计划完成日期
                        })









    
        