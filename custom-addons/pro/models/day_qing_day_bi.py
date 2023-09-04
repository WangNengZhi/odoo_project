
from odoo.exceptions import ValidationError
from odoo import models, fields, api
import itertools
from datetime import timedelta, datetime
import re


class DayQingDayBi(models.Model):
    _name = 'day_qing_day_bi'
    _description = '日清日毕'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)

    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    product_size = fields.Many2one("fsn_size", string="尺码")
    group = fields.Char(string='组别', required=True)

    num_people = fields.Float(string='人数', compute="set_pro_pro", store=True, group_operator='avg')
    
    
    avg_value = fields.Float(string='人均产值', compute="set_pro_pro", store=True)
    number = fields.Float(string='件数', compute="set_pro_pro", store=True)
    pro_value = fields.Float(string='产值', compute="set_pro_pro", store=True)

    dg_num_people = fields.Float(string='吊挂人数')
    dg_avg_value = fields.Float(string='吊挂人均产值', compute="set_dg_avg_value", store=True)
    @api.depends('dg_value', 'num_people')
    def set_dg_avg_value(self):
        for record in self:
            if record.num_people:
                record.dg_avg_value = record.dg_value / record.num_people
            else:
                record.dg_avg_value = 0
    dg_number = fields.Float(string="吊挂件数")
    dg_value = fields.Float(string="吊挂产值")


    plan_number = fields.Float(string="计划件数", compute="set_planning_slot_data", store=True)
    plan_value = fields.Float(string="计划产值", compute="set_planning_slot_data", store=True)
    plan_avg_value = fields.Float(string="计划人均产值", compute="set_planning_slot_data", store=True)

    plan_difference = fields.Float(string="计划差值（交货）", compute="set_planning_slot_data", store=True)
    plan_punishment = fields.Float(string="计划处罚（交货）", compute="set_planning_slot_data", store=True)
    plan_award = fields.Float(string="计划奖励")
    plan_stranded = fields.Float(string="计划滞留（吊挂）", compute="set_plan_stranded", store=True)
    dg_plan_award = fields.Float(string="计划奖励（吊挂）", compute="set_plan_stranded", store=True)
    # 设置计划和吊挂的差值信息
    @api.depends('plan_number', 'dg_number', 'group')
    def set_plan_stranded(self):
        for record in self:

            record.plan_stranded = record.plan_number - record.dg_number

            if record.plan_stranded < 0:
                if record.group == "后道":
                    record.dg_plan_award = abs(record.plan_stranded * 2)
                elif record.group == "裁床":
                    record.dg_plan_award = abs(record.plan_stranded)
                else:
                    record.dg_plan_award = abs(record.plan_stranded * 5)
            else:
                record.dg_plan_award = 0

    plan_stage = fields.Char(string="计划阶段", compute="set_planning_slot_data", store=True)
    unfinished_value = fields.Float(string="计划未完成百分比", compute="set_unfinished_value", store=True, group_operator='avg')



    stranded_number = fields.Float(string="滞留件数", compute="compute_retention_value", store=True)
    retention_value = fields.Float(string="滞留产值", compute="compute_retention_value", store=True)

    deductions = fields.Float(string="扣款", compute="set_deductions", store=True)

    pro_pro_id = fields.Many2one("pro.pro", string="组产值id")

    posterior_passage_output_value_id = fields.Many2one("posterior_passage_output_value", string="后道产值id")

    cutting_bed_id = fields.Many2one("cutting_bed", string="裁床产值id")

    planning_slot_id = fields.Many2one("planning.slot", string="计划id", compute="set_planning_slot", store=True)


    invest_invest_ids = fields.Many2many("invest.invest", string="中查明细")
    number_repair = fields.Float(string="返修件数", compute="set_number_repair", store=True)
    @api.depends('invest_invest_ids')
    def set_number_repair(self):
        for record in self:
            if "invest.invest" in self.env:
                record.number_repair = sum(record.invest_invest_ids.mapped('repairs_number'))





    # 手动刷新日清日毕
    def manual_refresh(self, today):

        objs = self.sudo().search([("date", "=", today)])
        objs.sudo().unlink()


        self.get_dg_data(today)


        return True



    # 设置计划未完成百分比
    @api.depends('pro_value', 'plan_value')
    def set_unfinished_value(self):
        for record in self:

            if record.plan_value:

                tem_unfinished_value = (record.plan_value - record.pro_value) / record.plan_value

                if tem_unfinished_value < 0:
                    record.unfinished_value = 0
                else:
                    record.unfinished_value = tem_unfinished_value



    # 绑定计划
    @api.depends('date', 'style_number', 'product_size', 'group')
    def set_planning_slot(self):
        for record in self:

            if "planning.slot" in self.env:

                planning_slot_objs = self.env["planning.slot"].sudo().search([
                    ("dDate", "=", record.date),
                    ("style_number", "=", record.style_number.id),
                    ("product_size", "=", record.product_size.id),
                    ("staff_group", "like", record.group)
                ], limit=1)


                if planning_slot_objs:
                    record.planning_slot_id = planning_slot_objs[0].id


    # 设置计划数据
    @api.depends('planning_slot_id', 'style_number', 'num_people', 'number', 'group')
    def set_planning_slot_data(self):
        for record in self:

            if record.planning_slot_id:

                record.plan_number = record.planning_slot_id.plan_number    # 计划数量

                record.plan_stage = record.planning_slot_id.plan_stage  # 计划阶段

                plan_difference = record.plan_number - record.number     # 计划差值
                if plan_difference >= 0:
                    record.plan_difference = plan_difference

                if record.plan_difference >= 0:
                    if record.group == "后道":
                        record.plan_punishment = record.plan_difference * 2    # 计划惩罚
                    elif record.group == "裁床":
                        record.plan_punishment = record.plan_difference     # 计划惩罚
                    else:
                        record.plan_punishment = record.plan_difference * 5     # 计划惩罚

                record.plan_value = record.plan_number * float(record.planning_slot_id.order_number.order_price)      # 计划产值

                if record.num_people:
                    record.plan_avg_value = record.plan_value / record.num_people   # 人均计划产值



    # 设置扣款
    @api.depends('stranded_number', 'group')
    def set_deductions(self):
        for record in self:
            if record.group == "后道":
                record.deductions = record.stranded_number * 2
            elif record.group == "裁床":
                record.deductions = record.stranded_number
            else:
                record.deductions = record.stranded_number * 5


    # 设置组产值内容
    @api.depends('pro_pro_id', 'posterior_passage_output_value_id', 'cutting_bed_id')
    def set_pro_pro(self):
        for record in self:

            CN_NUM = {
                "1": "车缝一组",
                "2": "车缝二组",
                "3": "车缝三组",
                "4": "车缝四组",
                "5": "车缝五组",
                "6": "车缝六组",
                "7": "车缝七组",
                "8": "车缝八组",
                "9": "车缝九组",
                "10": "车缝十组",
                "后道": "后整",
            }

            if record.group not in CN_NUM:
                dg_number_people = 0
            else:
                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([("dDate", "=", record.date), ("group.group", "=", CN_NUM[record.group])])
                dg_number_people = len(set([i.employee_id.id for i in suspension_system_station_summary_objs if i.employee_id.is_it_a_temporary_worker != "正式工(B级管理)"]))

            if record.pro_pro_id:
                record.num_people = dg_number_people
                record.avg_value = record.pro_pro_id.avg_value
                record.number = record.pro_pro_id.number
                record.pro_value = record.pro_pro_id.pro_value
            if record.posterior_passage_output_value_id:
                record.num_people = dg_number_people
                record.number = record.posterior_passage_output_value_id.number
                record.pro_value = record.posterior_passage_output_value_id.pro_value
                record.avg_value = record.pro_value / record.num_people if record.num_people else 0
            if record.cutting_bed_id:
                record.num_people = record.cutting_bed_id.num_people
                record.number = record.cutting_bed_id.number
                record.pro_value = record.cutting_bed_id.pro_value
                record.avg_value = record.pro_value / record.num_people if record.num_people else 0
        


    @api.depends('number', 'pro_value', 'dg_number', 'dg_value')
    def compute_retention_value(self):
        for record in self:
            # 设置滞留件数
            tem_stranded_number = record.dg_number - record.number
            if tem_stranded_number >= 0:
                record.stranded_number = tem_stranded_number
            else:
                record.stranded_number = 0

            # 设置滞留产值
            tem_retention_value = record.pro_value - record.dg_value
            if tem_retention_value <= 0:
                record.retention_value = tem_retention_value

            else:
                record.retention_value = 0




    def search_plan(self, today):

        CN_NUM = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            "后道": "后整",
        }

        planning_slot_objs = self.env["planning.slot"].sudo().search([
            ("dDate", "=", today),
        ])

        for planning_slot_obj in planning_slot_objs:

            if planning_slot_obj.department_id == "后道" or planning_slot_obj.department_id == "裁床":
                
                group = planning_slot_obj.staff_group
            else:

                group = re.sub("\D", "", planning_slot_obj.staff_group)

            if group:

                if group not in CN_NUM:
                    dg_number_people = 0
                else:
                    suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([("dDate", "=", today), ("group.group", "=", CN_NUM[group])])
                    dg_number_people = len(set([i.employee_id.id for i in suspension_system_station_summary_objs if i.employee_id.is_it_a_temporary_worker != "正式工(B级管理)"]))


                obj = self.search([
                    ("date", "=", today),
                    ("group", "=", group),
                    ("style_number", "=", planning_slot_obj.style_number.id),
                    ("product_size", "=", planning_slot_obj.product_size.id),
                ])

                if obj:
                    obj.sudo().write({
                        "planning_slot_id": planning_slot_obj.id,
                        "num_people": dg_number_people
                    })
                else:
                    self.create({
                        "date": today,     # 日期
                        "group": group,    # 组别
                        "style_number": planning_slot_obj.style_number.id,  # 款号id
                        "product_size": planning_slot_obj.product_size.id,    # 尺码id
                        "plan_number":  planning_slot_obj.plan_number,   # 计划件数
                        "num_people": dg_number_people
                    })


    def get_dg_data(self, today):


        CN_NUM = {
            "车缝一组": "1",
            "车缝二组": "2",
            "车缝三组": "3",
            "车缝四组": "4",
            "车缝五组": "5",
            "车缝六组": "6",
            "车缝七组": "7",
            "车缝八组": "8",
            "车缝九组": "9",
            "车缝十组": "10",
            "后整": "后道",
        }

        self.search_plan(today)

        suspension_system_summary_list = self.env["suspension_system_summary"].sudo().search_read(
            domain=[("dDate", "=", today)],
            fields=["dDate", "group", "style_number", "product_size", "people_number", "total_quantity", "production_value"],
        )

        # 按组别排序
        suspension_system_summary_list.sort(key=lambda x: x["group"], reverse=False)


        for group, group_objs in itertools.groupby(suspension_system_summary_list, key=lambda x:x["group"]):     # 按组别分组

            if group[1] not in CN_NUM:
                pass

            else:
                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([("dDate", "=", today), ("group", "=", group[0])])

                dg_number_people = len(set([i.employee_id.id for i in suspension_system_station_summary_objs if i.employee_id.is_it_a_temporary_worker != "正式工(B级管理)"]))

                group_objs_list = [i for i in group_objs if i["style_number"]]

                # 按款号排序
                group_objs_list.sort(key=lambda x: x["style_number"], reverse=False)

                for style_number, style_number_objs in itertools.groupby(group_objs_list, key=lambda x:x["style_number"]):     # 按款号分组

                    style_number_objs_list = list(style_number_objs)

                    # 按尺码排序
                    style_number_objs_list.sort(key=lambda x: x["product_size"], reverse=False)

                    for product_size, product_size_objs in itertools.groupby(style_number_objs_list, key=lambda x:x["product_size"]):     # 按尺码分组

                        product_size_objs_list = list(product_size_objs)


                        tem_total_quantity = 0      # 件数
                        tem_production_value = 0        # 产值
                        for product_size_obj in product_size_objs_list:
                            tem_total_quantity = tem_total_quantity + product_size_obj["total_quantity"]
                            tem_production_value = tem_production_value + product_size_obj["production_value"]


                        obj = self.search([
                            ("date", "=", today),
                            ("group", "=", CN_NUM[group[1]]),
                            ("style_number", "=", style_number[0]),
                            ("product_size", "=", product_size[0]),
                        ])

                        if obj:
                            obj.sudo().write({
                                "dg_number":  tem_total_quantity,   # 件数
                                "dg_value": tem_production_value,  # 产值
                                "num_people": dg_number_people
                            })
                        else:

                            new_obj = self.create({
                                "date": today,     # 日期
                                "group": CN_NUM[group[1]],    # 组别
                                "style_number": style_number[0],  # 款号id
                                "product_size": product_size[0],    # 尺码id
                                "dg_number":  tem_total_quantity,   # 件数
                                "dg_value": tem_production_value,  # 产值
                                "num_people": dg_number_people
                            })


        # 设置组产值数据
        self.set_pro_pro_data(today)
        # 设置后道产值数据
        self.set_posterior_passage_data(today)
        # 设置裁床产值数据
        self.set_cutting_bed_data(today)

    # 设置裁床产值数据
    def set_cutting_bed_data(self, today):


        cutting_bed_objs = self.env["cutting_bed"].sudo().search([
            ("date", "=", today),
        ])

        for cutting_bed_obj in cutting_bed_objs:

            day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
                ("date", "=", cutting_bed_obj.date),
                ("group", "=", "裁床"),
                ("style_number", "=", cutting_bed_obj.style_number.id),
                ("product_size", "=", cutting_bed_obj.product_size.id),
            ])
            if day_qing_day_bi_obj:
                day_qing_day_bi_obj.sudo().write({
                    "cutting_bed_id": cutting_bed_obj.id
                })
            else:
                day_qing_day_bi_obj.create({
                    "date": cutting_bed_obj.date,     # 日期
                    "group": "裁床",    # 组别
                    "style_number": cutting_bed_obj.style_number.id,  # 款号id
                    "product_size": cutting_bed_obj.product_size.id,    # 尺码id
                    "cutting_bed_id": cutting_bed_obj.id
                })


    # 设置后道产值数据
    def set_posterior_passage_data(self, today):


        posterior_passage_output_value_objs = self.env["posterior_passage_output_value"].sudo().search([
            ("date", "=", today),
        ])

        for posterior_passage_output_value_obj in posterior_passage_output_value_objs:

            day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
                ("date", "=", posterior_passage_output_value_obj.date),
                ("group", "=", "后道"),
                ("style_number", "=", posterior_passage_output_value_obj.style_number.id),
                ("product_size", "=", posterior_passage_output_value_obj.product_size.id),
            ])
            if day_qing_day_bi_obj:
                day_qing_day_bi_obj.sudo().write({
                    "posterior_passage_output_value_id": posterior_passage_output_value_obj.id
                })
            else:
                day_qing_day_bi_obj.create({
                    "date": posterior_passage_output_value_obj.date,     # 日期
                    "group": "后道",    # 组别
                    "style_number": posterior_passage_output_value_obj.style_number.id,  # 款号id
                    "product_size": posterior_passage_output_value_obj.product_size.id,    # 尺码id
                    "posterior_passage_output_value_id": posterior_passage_output_value_obj.id
                })





    # 设置组产值数据
    def set_pro_pro_data(self, today):



        pro_pro_objs = self.env["pro.pro"].sudo().search([
            ("date", "=", today),
        ])

        for pro_pro_obj in pro_pro_objs:

            obj = self.search([
                ("date", "=", pro_pro_obj.date),
                ("group", "=", pro_pro_obj.group),
                ("style_number", "=", pro_pro_obj.style_number.id),
                ("product_size", "=", pro_pro_obj.product_size.id),
            ])

            if obj:
                obj.sudo().write({
                    "pro_pro_id": pro_pro_obj.id
                })
            else:
                self.create({
                    "date": pro_pro_obj.date,     # 日期
                    "group": pro_pro_obj.group,    # 组别
                    "style_number": pro_pro_obj.style_number.id,  # 款号id
                    "product_size": pro_pro_obj.product_size.id,    # 尺码id
                    "pro_pro_id":  pro_pro_obj.id   # 组产值id
                })



class CuttingBed(models.Model):
    _inherit = "cutting_bed"

    def set_day_qing_day_bi(self):

        day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
            ("date", "=", self.date),
            ("group", "=", "裁床"),
            ("style_number", "=", self.style_number.id),
            ("product_size", "=", self.product_size.id),
        ])
        if day_qing_day_bi_obj:
            day_qing_day_bi_obj.sudo().write({
                "cutting_bed_id": self.id
            })
        else:
            day_qing_day_bi_obj.sudo().create({
                "date": self.date,     # 日期
                "group": "裁床",    # 组别
                "style_number": self.style_number.id,  # 款号id
                "product_size": self.product_size.id,    # 尺码id
                "cutting_bed_id": self.id
            })

    @api.model
    def create(self, vals):

        rec = super(CuttingBed, self).create(vals)

        rec.set_day_qing_day_bi()

        return rec



class PosteriorPassageOutputValue(models.Model):
    _inherit = "posterior_passage_output_value"

    def set_day_qing_day_bi(self):

        day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
            ("date", "=", self.date),
            ("group", "=", "后道"),
            ("style_number", "=", self.style_number.id),
            ("product_size", "=", self.product_size.id),
        ])
        if day_qing_day_bi_obj:
            day_qing_day_bi_obj.sudo().write({
                "posterior_passage_output_value_id": self.id
            })
        else:
            day_qing_day_bi_obj.create({
                "date": self.date,     # 日期
                "group": "后道",    # 组别
                "style_number": self.style_number.id,  # 款号id
                "product_size": self.product_size.id,    # 尺码id
                "posterior_passage_output_value_id": self.id
            })

    @api.model
    def create(self, vals):

        rec = super(PosteriorPassageOutputValue, self).create(vals)

        rec.set_day_qing_day_bi()

        return rec



class ProPro(models.Model):
    _inherit = "pro.pro"


    def set_day_qing_day_bi(self):

        day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
            ("date", "=", self.date),
            ("group", "=", self.group),
            ("style_number", "=", self.style_number.id),
            ("product_size", "=", self.product_size.id),
        ])
        if day_qing_day_bi_obj:
            day_qing_day_bi_obj.sudo().write({
                "pro_pro_id": self.id
            })
        else:
            day_qing_day_bi_obj.create({
                "date": self.date,     # 日期
                "group": self.group,    # 组别
                "style_number": self.style_number.id,  # 款号id
                "product_size": self.product_size.id,    # 尺码id
                "pro_pro_id": self.id
            })


    @api.model
    def create(self, vals):

        rec = super(ProPro, self).create(vals)

        rec.set_day_qing_day_bi()

        return rec