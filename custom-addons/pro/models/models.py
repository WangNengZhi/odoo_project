# -*- coding: utf-8 -*-
from re import L
from odoo.tools.misc import parse_date
from odoo.exceptions import ValidationError
from odoo import models, fields, api

from datetime import datetime, timedelta
import time
import json

class toproduct(models.Model):
    _name = 'totlepro.totlepro'
    _description = '车间产值'
    _rec_name = 'date'
    _order = "date desc"

    date = fields.Date('日期')
    week = fields.Char(string="周")
    number = fields.Integer('件数', compute="set_pro_pro_ids_info", store=True)
    pro_value = fields.Float('产值', compute="set_pro_pro_ids_info", store=True)
    num_people = fields.Float('人数', compute="set_pro_pro_ids_info", store=True)
    avg_pro = fields.Float('人均产值', compute="set_avg_pro", store=True)
    toproduct_week_id = fields.Many2one("toproduct.week", string="车间产值(周)")

    pro_pro_ids = fields.One2many("pro.pro", "totlepro_totlepro_id", string="组产值")


    # 设置 件数 和 产值
    @api.depends('pro_pro_ids', 'pro_pro_ids.number', 'pro_pro_ids.pro_value', 'pro_pro_ids.num_people')
    def set_pro_pro_ids_info(self):

        for record in self:


            record.number = sum(record.pro_pro_ids.mapped('number')) # 件数
            record.pro_value = sum(record.pro_pro_ids.mapped('pro_value'))  # 产值
            record.num_people = sum(record.pro_pro_ids.mapped('num_people'))    # 人数


    # 设置 人均产值
    @api.depends('num_people', 'pro_value')
    def set_avg_pro(self):
        for record in self:

            if record.num_people:

                record.avg_pro = record.pro_value / record.num_people


    # 检测当天的车间产值只能有一条记录
    @api.constrains('date')
    def _check_unique(self):
        demo = self.env[self._name].sudo().search([('date', '=', self.date)])
        if len(demo) > 1:
            raise ValidationError(f"已经存在{self.date}的车间产值记录了！")


    @api.onchange('date')
    def onchange1(self):
        demo = self.env['pro.pro'].sudo().search([])
        self.number = 0
        self.pro_value = 0
        self.num_people = 0
        self.avg_pro = 0
        for i in demo:
            if i.date == self.date:
                self.number += i.number
                self.pro_value += i.pro_value
                self.num_people += i.num_people
                self.avg_pro = self.pro_value / self.num_people



    # 设置车间产值（周）
    def toproduct_week(self, res):

        toproduct_week_obj = self.env['toproduct.week'].sudo().search([("week", "=", res.week)])

        if toproduct_week_obj:
            res.toproduct_week_id = toproduct_week_obj.id
        else:
            new_toproduct_week_obj = self.env["toproduct.week"].sudo().create({
                "week": res.week,
            })
            res.toproduct_week_id = new_toproduct_week_obj.id




    @api.model
    def create(self, vals):


        # 导入数据时，没有周的概念，在这里添加上
        if "week" in vals:
            pass
        else:
            datetime_obj = datetime.strptime(vals['date'], "%Y-%m-%d")
            year = datetime_obj.year
            week = datetime_obj.isocalendar()
            vals["week"] = f"{year}年第{week[1]}周"

        detail_instance = super(toproduct, self).create(vals)
        # 设置车间产值(周)
        self.toproduct_week(detail_instance)


        return detail_instance


class toproduct_week(models.Model):
    _name = 'toproduct.week'
    _description = '车间产值(周)'
    _order = "week desc"

    week = fields.Char('周')
    number = fields.Integer('件数', compute="set_toproduct_week_messages", store=True)
    pro_value = fields.Float('产值', compute="set_toproduct_week_messages", store=True)
    num_people = fields.Float('人数', compute="set_toproduct_week_messages", store=True)
    avg_pro = fields.Float('人均产值', compute="set_toproduct_week_messages", store=True)

    totlepro_totlepro_ids = fields.One2many("totlepro.totlepro", "toproduct_week_id", string="车间产值")

    @api.depends('totlepro_totlepro_ids', 'totlepro_totlepro_ids.number', 'totlepro_totlepro_ids.pro_value', 'totlepro_totlepro_ids.num_people')
    def set_toproduct_week_messages(self):
        for record in self:

            record.number = sum(record.totlepro_totlepro_ids.mapped('number')) # 件数
            record.pro_value = sum(record.totlepro_totlepro_ids.mapped('pro_value'))  # 产值
            if len(record.totlepro_totlepro_ids):
                record.num_people = sum(record.totlepro_totlepro_ids.mapped('num_people')) / len(record.totlepro_totlepro_ids)    # 人数
            else:
                record.num_people = 0
            if record.num_people:
                record.avg_pro = record.pro_value / record.num_people
            else:
                record.avg_pro = 0


class product(models.Model):
    _name = 'pro.pro'
    _description = '组产值'
    _inherit = ['mail.thread']
    _rec_name = 'date'
    _order = "date desc"

    date = fields.Date('日期', required=True, track_visibility='onchange')
    week = fields.Char(string="周")
    style_number = fields.Many2one('ib.detail', string='款号', required=True, track_visibility='onchange')
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    group = fields.Char('组别', required=True, track_visibility='onchange')
    number = fields.Integer('件数', track_visibility='onchange')
    num_people = fields.Float('人数', track_visibility='onchange')

    # @api.depends("date", "group")
    def set_num_people(self):

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
        }

        for record in self:
            if "check_position_settings" in self.env and "auto_employee_information" in self.env:
                # 查询组别
                check_position_settings_obj = self.env["check_position_settings"].sudo().search([
                    ("group", "=", CN_NUM.get(record.group, record.group))
                ])
                employee_id_objs_list = self.env["auto_employee_information"].sudo().search([
                    ("date", "=", record.date),    # 日期
                    ("group_id", "=", check_position_settings_obj.id),     # 组别
                ]).mapped('employee_id')

                employee_id_objs_list = list(set(employee_id_objs_list))
                record.num_people = len(employee_id_objs_list)



    avg_value = fields.Float('人均产值', compute="set_pro_value", store=True)
    pro_value = fields.Float('产值', compute="set_pro_value", store=True)
    pro_pro_week_id = fields.Many2one('pro.pro.week', string="组产值(周)")
    totlepro_totlepro_id = fields.Many2one('totlepro.totlepro', string="车间产值")


    dg_number = fields.Float(string="吊挂件数", compute="compute_retention_value", store=True)
    dg_value = fields.Float(string="吊挂产值", compute="compute_retention_value", store=True)

    stranded_number = fields.Float(string="滞留件数", compute="compute_retention_value", store=True)
    retention_value = fields.Float(string="滞留产值", compute="compute_retention_value", store=True)



    # 设置滞留产值
    @api.depends("date", "group", "style_number", "product_size", "number", "pro_value")
    def compute_retention_value(self):

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
        }

        for record in self:

            if record.group:

                suspension_system_summary_objs_list = []

                # 判断是否有依赖的模型
                if "suspension_system_summary" in self.env and "check_position_settings" in self.env:

                    # 查询组别
                    check_position_settings_obj = self.env["check_position_settings"].sudo().search([
                        # ("group", "=", CN_NUM[record.group])
                        ("group", "=", CN_NUM.get(record.group, record.group))
                    ])

                    #查询吊挂产值
                    suspension_system_summary_objs_list = self.env["suspension_system_summary"].sudo().search_read([
                        ("dDate", "=", record.date),    # 日期
                        ("group", "=", check_position_settings_obj.id),     # 组别
                        ("style_number", "=", record.style_number.id),      # 款号
                        ("product_size", "=", record.product_size.id),      # 尺码
                    ], ["total_quantity", "production_value"])

                else:
                    pass

                tem_total_quantity_list = []
                tem_production_value_list = []

                for suspension_system_summary_obj in suspension_system_summary_objs_list:
                    tem_total_quantity_list.append(suspension_system_summary_obj["total_quantity"])
                    tem_production_value_list.append(suspension_system_summary_obj["production_value"])

                # 吊挂件数
                record.dg_number = sum(tem_total_quantity_list)
                # 吊挂产值
                record.dg_value = sum(tem_production_value_list)

                # 滞留产值 = 吊挂组产值之和 - 组产值
                record.retention_value = sum(tem_production_value_list) - record.pro_value
                # 滞留件数 = 吊挂组件数之和 - 组件数
                record.stranded_number = sum(tem_total_quantity_list) - record.number

    # 设置后道进出明细
    def set_following_process_detail(self):
        following_process_detail_obj = self.env["following_process_detail"].sudo().search([
            ("dDate", "=", self.date)
        ])
        if following_process_detail_obj:
            following_process_detail_obj.set_workshop_production()
        else:
            new_obj = following_process_detail_obj.create({
                "dDate": self.date
            })
            new_obj.set_workshop_production()



    # 数据检测
    def inspect_data(self):

        abnormal_record = []

        for record in self:

            on_work_objs = self.env["on.work"].sudo().search([
                ("date1", "=", record.date),
                ("group", "=", record.group),
                ("order_number", "=", record.style_number.id)
            ])

            record_over_number_list = []
            for on_work_obj in on_work_objs:
                record_over_number_list.append(on_work_obj.over_number)



            if record_over_number_list:

                if record.number != max(record_over_number_list):
                    abnormal_record.append({
                        "类型": "件数",
                        "日期": record.date,
                        "款号": record.style_number.style_number,
                        "组别": record.group,
                        "原因": "数据错误!",
                        "目标数值": max(record_over_number_list),
                    })
                else:
                    ib_detail_objs = self.env["ib.detail"].sudo().search([("id", "=", record.style_number.id)])

                    production_value = ib_detail_objs.price * record.number

                    if record.pro_value != production_value:
                        abnormal_record.append({
                            "类型": "产值",
                            "日期": record.date,
                            "款号": record.style_number.style_number,
                            "组别": record.group,
                            "原因": "数据错误!",
                            "目标数值": production_value,
                        })

            else:

                abnormal_record.append({
                    "类型": "件数",
                    "日期": record.date,
                    "款号": record.style_number.style_number,
                    "组别": record.group,
                    "原因": "没有找到对应记录！"
                })

        text = ""
        for i in abnormal_record:
            text = text + str(i) + "\n"


        raise ValidationError(f"异常记录:\n{text}")



    # 设置计划的实际完成数量
    def set_plan_data(self):

        max_datetime = datetime.combine(self.date, datetime.max.time()) - timedelta(hours=8)     # 最大时间
        min_datetime = datetime.combine(self.date, datetime.min.time()) - timedelta(hours=8)     # 最小时间

        plan_objs = self.env["planning.slot"].sudo().search([
            ("start_datetime", ">=", min_datetime),
            ("start_datetime", "<=", max_datetime),
            ("end_datetime", ">=", min_datetime),
            ("end_datetime", "<=", max_datetime),
            ("style_number", "=", self.style_number.id),    # 款号
            ("staff_group", "=", self.group + "组"),    # 组别
            ("product_size", "=", self.product_size.id),    # 尺码
        ])


        for plan_obj in plan_objs:

            objs = self.env[self._name].sudo().search([
                ("date", "=", self.date),
                ("style_number", "=", self.style_number.id),
                ("group", "=", self.group),
            ])
            tem_actual_number = 0
            for obj in objs:
                tem_actual_number = tem_actual_number + obj.number

            plan_obj.actual_number = tem_actual_number


    # 计算人均产值
    @api.depends('style_number', 'number', 'num_people', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)

            if obj.num_people:

                obj.avg_value = obj.pro_value / obj.num_people


    # 设置显示名称
    def name_get(self):
        result = []
        for record in self:
            rec_name = "日期:%s,      款号: %s,      组别:%s" % (record.date, record.style_number.style_number, record.group)   #例：%s (%s) = 数学 (2021-02-11)
            result.append((record.id, rec_name))
        return result


    # 检查数据唯一性
    @api.constrains('date', 'group', 'style_number')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ('group', '=', self.group),
            ('style_number', '=', self.style_number.id),
            ("order_number", "=", self.order_number.id),
            ('product_size', "=", self.product_size.id),
        ])

        if len(demo) > 1:
            raise ValidationError(f"{self.group}组已经存在{self.date}且款号为{self.style_number.style_number}尺码为{self.product_size.name}的产值记录了！")


    # 设置款号件数汇总数据
    def set_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id)
        ])
        if style_number_summary_objs:
            style_number_summary_objs.sudo().set_workshop()
        else:
            new_obj = style_number_summary_objs.sudo().create({
                "style_number": self.style_number.id,
            })
            new_obj.sudo().set_workshop()


    # 减少款号件数汇总数据(删除时使用)
    def reduce_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id)
        ])

        style_number_summary_objs.write({
            "workshop": style_number_summary_objs.workshop - self.number
        })


    # 设置组产值周
    def set_pro_pro_week(self, res):

        # 查询组产值(周)表里面有没有该组该周的记录，如果有则修改，如果没有则创建。
        pro_pro_week_obj = self.env['pro.pro.week'].sudo().search([("week", "=", res.week), ("group", "=", res.group)])
        if pro_pro_week_obj:
            res.pro_pro_week_id = pro_pro_week_obj.id
        else:

            new_pro_pro_week_obj = self.env["pro.pro.week"].sudo().create({
                "week": res.week,   # 周
                "group": res.group,     # 组
            })

            res.pro_pro_week_id = new_pro_pro_week_obj.id




    # 设置车间产值
    def set_totlepro_totlepro(self, res):

        # 查询是否已经存在当天的车间的产值
        totlepro_totlepro_obj = self.totlepro_totlepro_id.sudo().search([("date", "=", res.date)])
        if totlepro_totlepro_obj:
            pass
        else:

            totlepro_totlepro_obj = self.totlepro_totlepro_id.sudo().create({
                "date": str(res.date),   # 日期
            })

        res.totlepro_totlepro_id = totlepro_totlepro_obj.id


    def write(self, vals):
        res = super(product, self).write(vals)


        return res



    @api.model
    def create(self, vals):

        # 给周字段设置值
        if "week" in vals:
            pass
        else:
            datetime_obj = datetime.strptime(vals['date'], "%Y-%m-%d")
            year = datetime_obj.year
            week = datetime_obj.isocalendar()
            vals["week"] = f"{year}年第{week[1]}周"

        instance = super(product, self).create(vals)

        # 设置组产值周
        self.set_pro_pro_week(instance)

        # 设置车间产值
        self.set_totlepro_totlepro(instance)

        # 设置计划的实际完成数量
        instance.set_plan_data()

        # 设置后道进出明细
        instance.set_following_process_detail()

        return instance



    def unlink(self):

        for record in self:


            max_datetime = datetime.combine(record.date, datetime.max.time()) - timedelta(hours=8)     # 最大时间
            min_datetime = datetime.combine(record.date, datetime.min.time()) - timedelta(hours=8)     # 最小时间
            tem_style_number_id = record.style_number.id     # 款号id
            tem_staff_group = record.group    # 组别

            dDate = record.date     # 日期

            tem_product_size_id = record.product_size.id   # 尺码id


            super(product, record).unlink()

            plan_objs = self.env["planning.slot"].sudo().search([
                ("start_datetime", ">=", min_datetime),
                ("start_datetime", "<=", max_datetime),
                ("end_datetime", ">=", min_datetime),
                ("end_datetime", "<=", max_datetime),
                ("style_number", "=", tem_style_number_id),
                ("staff_group", "=", tem_staff_group + "组"),
            ])
            if plan_objs:
                plan_objs.sudo().set_data()


            # 删除时，设置后道进出明细
            following_process_detail_obj = self.env["following_process_detail"].sudo().search([
                ("dDate", "=", dDate)
            ])
            if following_process_detail_obj:
                following_process_detail_obj.sudo().set_workshop_production()



            # 删除时，设置日清日毕
            day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().search([
                ("date", "=", dDate),
                ("group", "=", tem_staff_group),
                ("style_number", "=", tem_style_number_id),
                ("product_size", "=", tem_product_size_id),
            ])
            if day_qing_day_bi_obj:
                day_qing_day_bi_obj.write({
                    "num_people": 0,
                    "avg_value": 0,
                    "number": 0,
                    "pro_value": 0,
                })


        res = super(product, self).unlink()

        return res



class product_week(models.Model):
    _name = 'pro.pro.week'
    _description = '组产值(周)'
    _order = "week desc"


    week = fields.Char(string="周")
    style_number = fields.Char('款号', compute="set_pro_pro_week_messages", store=True)
    group = fields.Char('组别', compute="set_pro_pro_week_messages", store=True)
    number = fields.Integer('件数', compute="set_pro_pro_week_messages", store=True)
    num_people = fields.Float('人数', compute="set_pro_pro_week_messages", store=True)
    avg_value = fields.Float('人均产值', compute="set_pro_pro_week_messages", store=True)
    pro_value = fields.Float('产值', compute="set_pro_pro_week_messages", store=True)

    pro_pro_ids = fields.One2many("pro.pro", "pro_pro_week_id", string="组产值")

    @api.depends('pro_pro_ids', 'pro_pro_ids.pro_value', 'pro_pro_ids.num_people', 'pro_pro_ids.number', 'pro_pro_ids.style_number')
    def set_pro_pro_week_messages(self):
        for record in self:

            # 产值
            record.pro_value = sum(record.pro_pro_ids.mapped("pro_value"))
            # 人数
            if len(record.pro_pro_ids):
                record.num_people = sum(record.pro_pro_ids.mapped("num_people")) / len(record.pro_pro_ids)
            else:
                record.num_people = 0
            # 人均产值
            if record.num_people:
                record.avg_value = record.pro_value / record.num_people
            else:
                record.avg_value = 0
            # 件数
            record.number = sum(record.pro_pro_ids.mapped("number"))
            # 款号
            record.style_number = ",".join(list(set([pro_pro_obj.style_number.style_number for pro_pro_obj in record.pro_pro_ids])))






class made_employee(models.Model):
    _name = 'memp.memp'
    _description = '员工信息'
    _rec_name = 'date'
    _order = 'date desc'

    date = fields.Date('日期')
    employee = fields.Many2one('hr.employee', string="员工")
    group = fields.Char('组别')
    def name_get(self):
        result = []
        for record in self:
            rec_name = "日期:%s,      员工: %s,      组别:%s" % (record.date, record.employee.name, record.group)   #例：%s (%s) = 数学 (2021-02-11)
            result.append((record.id, rec_name))
        return result




class piecerate(models.Model):
    _name = 'cost.cost1'
    _description = '工序工资'
    _order = 'date1 desc'

    date1 = fields.Date('日期')
    employee_id = fields.Char('员工id')
    employee = fields.Many2one('hr.employee', string="员工")
    group = fields.Char('组别')
    cost = fields.Float('计件工资')



class totle_piecerate(models.Model):
    _name='ji.jian'
    _description = '计件工资'
    _order = 'date1'


    date1 = fields.Date('日期')
    employee_id = fields.Char('员工id')
    employee = fields.Many2one('hr.employee', string="员工")
    contract_type = fields.Char(string="合同")
    group = fields.Char('组别')
    cost = fields.Float('计件工资')


    def set_cost(self):
        for record in self:
            on_work_objs = self.env["on.work"].sudo().search([("date1", "=", record.date1), ("employee", "=", record.employee.id)])
            tem_cost = 0
            for on_work_obj in on_work_objs:
                tem_cost = tem_cost + (on_work_obj.standard_price * on_work_obj.over_number)

            record.cost = tem_cost



class totle_piecerate_week(models.Model):
    _name='ji.jian.week'
    _description = '计件工资(周)'
    _order = 'week desc'


    week = fields.Char('周')
    employee_id = fields.Char('员工id')
    employee = fields.Many2one('hr.employee', string="员工")
    group = fields.Char('组别')
    cost = fields.Float('计件工资')
