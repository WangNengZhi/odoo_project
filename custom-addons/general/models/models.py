# -*- coding: utf-8 -*-
import psycopg2
from odoo import models, fields, api
import time
from odoo.exceptions import ValidationError


class general(models.Model):
    _name = 'general.general'
    _description = '总检'
    _rec_name = 'item_no'
    _order = "date desc"


    date = fields.Date(string='日期', required=True)
    group = fields.Char(string='组别', required=True)
    order_number_id = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)
    item_no = fields.Many2one('ib.detail', string='款号', required=True)
    general1 = fields.Char(string='总检', required=True)
    jobs = fields.Char(string="岗位", compute="set_general_jobs", store=True)
    repair_number = fields.Integer(string='大货返修数量', required=True)

    # ---------
    general_number = fields.Integer(string='大货查货数量')
    delivery_number = fields.Integer(string='大货交货数量')
    efficiency = fields.Float(string="效率", compute="set_efficiency", store=True)
    order_number = fields.Integer(string='订单数量')
    number_of_cutting_beds = fields.Integer(string='裁床数')
    # ----------
    problems = fields.Text(string='问题点')
    invest = fields.Char(string='中查', required=True)
    comment = fields.Char(string='备注')

    repair_type = fields.Selection([
        ('车位返修','车位返修'),
        ('后道返修','后道返修'),
        ('裁床返修','裁床返修'),
        ('面料问题','面料问题'),
        ('整件返修','整件返修'),
        ('外发返修','外发返修'),
    ], string='返修类型', required=True)

    # 设置总检岗位
    @api.depends('general1')
    def set_general_jobs(self):
        for record in self:

            obj = self.env["hr.employee"].sudo().search([("name", "=", record.general1)])
            if obj:
                record.jobs = obj.job_id.name
            else:
                record.jobs = "员工名有误"


    # 设置后道待检产值
    def set_pp_wait_output_value(self):

        pp_wait_output_value_objs = self.env["pp_wait_output_value"].sudo().search([
            ("date", "=", self.date),
            ("style_number", "=", self.item_no.id),
            ("order_number", "=", self.order_number_id.id)
        ])
        # 如果存在
        if pp_wait_output_value_objs:
            pp_wait_output_value_objs.sudo().set_date()
        else:
            new_obj = self.env["pp_wait_output_value"].sudo().create({
                "date": self.date,
                "style_number": self.item_no.id,
                "order_number": self.order_number_id.id
            })
            new_obj.sudo().set_date()





    # 设置后道进出明细
    def set_following_process_detail(self):
        following_process_detail_obj = self.env["following_process_detail"].sudo().search([
            ("dDate", "=", self.date),
        ])
        if following_process_detail_obj:
            always_check_return_line_obj = following_process_detail_obj.always_check_return_ids.sudo().search([
                ("following_process_detail_id", "=", following_process_detail_obj.id),
                ("gGroup", "=", self.group),
            ])
            if always_check_return_line_obj:
                always_check_return_line_obj.sudo().set_always_check_return()
            else:
                new_obj = always_check_return_line_obj.sudo().create({
                    "following_process_detail_id": following_process_detail_obj.id,
                    "gGroup": self.group,
                })
                new_obj.sudo().set_always_check_return()
        else:
            new_detail_obj = following_process_detail_obj.sudo().create({
                "dDate": self.date,
            })
            new_obj = new_detail_obj.always_check_return_ids.create({
                "following_process_detail_id": new_detail_obj.id,
                "gGroup": self.group,
            })
            new_obj.sudo().set_always_check_return()



    # 设置总检效率表(日)
    def set_always_check_eff_day(self):
        middle_check_day_leak_objs = self.env["always_check_eff_day"].sudo().search([
            ("dDate", "=", self.date),
            ("always_check_principal", "=", self.general1)
        ])
        if middle_check_day_leak_objs:
            middle_check_day_leak_objs.sudo().set_date()
        else:
            new_obj = self.env["always_check_eff_day"].sudo().create({
                "dDate": self.date,
                "always_check_principal": self.general1
            })
            new_obj.sudo().set_date()


    # 设置中查每日漏查表数据信息
    def set_middle_check_day_leak(self):

        if self.repair_type == "车位返修":

            middle_check_day_leak_objs = self.env["middle_check_day_leak"].sudo().search([
                ("date", "=", self.date),
                ("middle_check_principal", "=", self.invest)
            ])
            if middle_check_day_leak_objs:
                middle_check_day_leak_objs.sudo().set_date()
            else:
                new_obj = self.env["middle_check_day_leak"].sudo().create({
                    "date": self.date,
                    "middle_check_principal": self.invest
                })
                new_obj.sudo().set_date()


    # 中查每日漏查(按款号)
    def set_middle_check_workpiece_ratio(self):

        if self.repair_type == "车位返修":

            middle_check_workpiece_ratio_objs = self.env["middle_check_workpiece_ratio"].sudo().search([
                ("date", "=", self.date),
                ("ib_detail_id", "=", self.item_no.id)
            ])
            # 如果存在
            if middle_check_workpiece_ratio_objs:
                middle_check_workpiece_ratio_objs.sudo().set_date()
            else:
                new_obj = self.env["middle_check_workpiece_ratio"].sudo().create({
                    "date": self.date,
                    "ib_detail_id": self.item_no.id
                })
                new_obj.sudo().set_date()


    # 设置中查漏查表返修数量
    def set_middle_check_omission_factor(self):
        # 获取年
        month = self.date.month
        # 获取月
        year = self.date.year
        year_month = f"{year}-{month}"

        middle_check_omission_factor_objs = self.env["middle_check_omission_factor"].sudo().search([
            ("middle_check_principal", "=", self.invest),
            ("month", "=", year_month),
        ])
        if middle_check_omission_factor_objs:

            for middle_check_omission_factor_obj in middle_check_omission_factor_objs:
                middle_check_omission_factor_obj.set_repair_quantity()


    # 设置总检效率表
    def set_always_check_efficiency(self):

        # 获取年
        month = self.date.month
        # 获取月
        year = self.date.year
        year_month = f"{year}-{month}"
        # 查询中查效率表
        always_check_efficiency_objs = self.env["always_check_efficiency"].sudo().search([
            ("month", "=", year_month),     # 月份
            ("always_check_principal", "=", self.general1)    # 总检负责人
        ])
        # 如果存在
        if always_check_efficiency_objs:
            always_check_efficiency_objs.sudo().set_date()
        else:
            new_obj = self.env["always_check_efficiency"].sudo().create({
                "month": year_month,
                "always_check_principal": self.general1,
            })
            new_obj.sudo().set_date()



    # 设置日款返修统计
    def set_day_style_repair_statistics(self):

        day_style_repair_statistics_objs = self.env["day_style_repair_statistics"].sudo().search([
            ("dDate", "=", self.date),      # 日期
            ("group", "=", self.group),     # 组别
            ("style_number", "=", self.item_no.id)      # 款号
        ])

        if day_style_repair_statistics_objs:
            day_style_repair_statistics_objs.sudo().set_data()
        else:
            new_obj = day_style_repair_statistics_objs.sudo().create({
                "dDate": self.date,     # 日期
                "group": self.group,    # 组别
                "style_number": self.item_no.id     # 款号
            })
            new_obj.sudo().set_data()


    # 设置效率
    @api.depends('item_no', 'general_number')
    def set_efficiency(self):
        for record in self:
            work_work_objs = self.env["work.work"].sudo().search([
                ("process_abbreviation", "like", "总检"),
                ("order_number", "=", record.item_no.id),    # 款号
            ])

            tem_standard_time = 0   # 临时标准时间

            for work_work_obj in work_work_objs:
                tem_standard_time = tem_standard_time + work_work_obj.standard_time
            # 效率 = （（总检数量 * 临时标准时间） / 39600） * 100
            record.efficiency = ((record.general_number * tem_standard_time) / 39600) * 100



    @api.model
    def create(self, val):

        res = super(general, self).create(val)
        # 设置日款返修统计
        res.set_day_style_repair_statistics()
        # 设置总检效率表
        res.set_always_check_efficiency()
        # 设置中查漏查表
        res.set_middle_check_omission_factor()
        # 设置中查漏查表（日：按款号）
        # res.set_middle_check_workpiece_ratio()
        # 设置中查漏查表（日：按中查）
        res.set_middle_check_day_leak()
        # 设置总检效率表（日）
        res.set_always_check_eff_day()
        # 设置后道进入明细
        res.set_following_process_detail()
        # 设置后道待检产值
        res.set_pp_wait_output_value()

        return res




    def unlink(self):
        # 明细表
        for record in self:


            dDate = record.date    # 日期
            group = record.group    # 组别
            item_no = record.item_no.id     # 款号id

            # 获取年
            month = record.date.month
            # 获取月
            year = record.date.year
            year_month = f"{year}-{month}"
            # 总检负责人
            general1 = record.general1
            # 中查负责人
            invest_principal = record.invest
            # 款号
            style_number = record.item_no.id
            # 订单号
            order_number_id = record.order_number_id.id

            super(general, record).unlink()

            # 删除时，日款返修统计，一起更新数据
            day_style_repair_statistics_obj = self.env["day_style_repair_statistics"].sudo().search([
                ("dDate", "=", dDate),
                ("group", "=", group),
                ("style_number", "=", item_no)
            ])
            if day_style_repair_statistics_obj:
                day_style_repair_statistics_obj.sudo().set_data()

            # 删除时，总检效率表一起跟新数据
            always_check_efficiency_objs = self.env["always_check_efficiency"].sudo().search([
                ("month", "=", year_month),     # 月份
                ("always_check_principal", "=", general1)    # 总检负责人
            ])
            if always_check_efficiency_objs:
                always_check_efficiency_objs.sudo().set_date()

            # 删除时，总检效率表一起跟新数据
            middle_check_omission_factor_objs = self.env["middle_check_omission_factor"].sudo().search([
                ("middle_check_principal", "=", invest_principal),
                ("month", "=", year_month),
            ])
            if middle_check_omission_factor_objs:
                middle_check_omission_factor_objs.sudo().set_repair_quantity()

            # 删除时
            # 查询中查效率表
            # middle_check_workpiece_ratio_objs = self.env["middle_check_workpiece_ratio"].sudo().search([
            #     ("date", "=", dDate),
            #     ("ib_detail_id", "=", style_number)
            # ])
            # 如果存在
            # if middle_check_workpiece_ratio_objs:
            #     middle_check_workpiece_ratio_objs.sudo().set_date()

            # 删除时
            # 查询中查漏查表（日）
            middle_check_day_leak_objs = self.env["middle_check_day_leak"].sudo().search([
                ("date", "=", dDate),
                ("middle_check_principal", "=", invest_principal)
            ])
            # 如果存在
            if middle_check_day_leak_objs:
                style_number_list = []
                for tem_obj in middle_check_day_leak_objs.style_number_line_ids:
                    style_number_list.append(tem_obj.name.id)
                if style_number in style_number_list:
                    middle_check_day_leak_objs.sudo().set_date()

            # 删除时
            # 设置总检效率表(日)
            middle_check_day_leak_objs = self.env["always_check_eff_day"].sudo().search([
                ("dDate", "=", dDate),
                ("always_check_principal", "=", general1)
            ])
            if middle_check_day_leak_objs:
                middle_check_day_leak_objs.sudo().set_date()


            # 删除时，设置后道进出明细
            always_check_return_line_obj = self.env["always_check_return_line"].sudo().search([
                ("dDate", "=", dDate),
                ("gGroup", "=", group)
            ])
            if always_check_return_line_obj:
                always_check_return_line_obj.sudo().set_always_check_return()



            # 删除时，设置后道待检产值
            pp_wait_output_value_obj = self.env["pp_wait_output_value"].sudo().search([
                ("date", "=", dDate),
                ("style_number", "=", style_number),
                ("order_number", "=", order_number_id)
            ])
            if pp_wait_output_value_obj:
                pp_wait_output_value_obj.sudo().set_date()



        res = super(general, self).unlink()

        return res






class two_general(models.Model):
    _name = 'two.general'
    _description = '总检返修汇总表'

    date = fields.Char(string='日期')
    item_no = fields.Char(string='款号')
    order_number = fields.Integer(string='订单数量')
    general1 = fields.Char(string='总检')

    invest = fields.Char(string='中查')
    repair_total = fields.Integer(string='返修汇总')
    repair_rate = fields.Float(string='返修率(%)', group_operator='avg')
    # comment = fields.Char(string='备注')






class invest(models.Model):
    _name = 'invest.invest'
    _description = '中查'
    _rec_name = 'invest'
    _order = "date desc"
    _inherit = ['mail.thread']

    date = fields.Date(string='日期', required=True, track_visibility='onchange')
    group = fields.Char(string='组别', required=True, track_visibility='onchange')
    invest = fields.Char(string='中查', required=True, track_visibility='onchange')
    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', track_visibility='onchange')
    repairs_number = fields.Integer(string='大货返修数量', track_visibility='onchange')
    quantity_of_delivery = fields.Integer(string='大货交货数量', track_visibility='onchange')
    check_the_quantity = fields.Integer(string='大货查货数量', track_visibility='onchange')
    fangong = fields.Many2one('hr.employee', string='返工', track_visibility='onchange')
    problems = fields.Text(string='问题点', track_visibility='onchange')
    comment = fields.Char(string='车位姓名', track_visibility='onchange')
    date_split = fields.Char(string='日期分割', compute='_compute_date_split', store=True, track_visibility='onchange')

    repair_rate = fields.Float(string='返修率(%)', compute='repair', store=True, track_visibility='onchange')

    repair_type = fields.Selection([
        ('车位返修','车位返修'),
        ('后道返修','后道返修'),
        ('裁床返修','裁床返修'),
        ('整件返修','整件返修'),
        ('外发返修','外发返修'),
        ('面料问题','面料问题'),
    ], string='返修类型', required=True)


    # 设置后道进出明细
    def set_following_process_detail(self):

        following_process_detail_obj = self.env["following_process_detail"].sudo().search([
            ("dDate", "=", self.date),
        ])
        if following_process_detail_obj:
            middle_check_return_ids_obj = following_process_detail_obj.middle_check_return_ids.sudo().search([
                ("following_process_detail_id", "=", following_process_detail_obj.id),
                ("gGroup", "=", self.group),
            ])
            if middle_check_return_ids_obj:
                middle_check_return_ids_obj.sudo().set_middle_check_return()
            else:
                new_obj = middle_check_return_ids_obj.sudo().create({
                    "following_process_detail_id": following_process_detail_obj.id,
                    "gGroup": self.group,
                })
                new_obj.sudo().set_middle_check_return()
        else:
            new_detail_obj = following_process_detail_obj.sudo().create({
                "dDate": self.date,
            })
            new_obj = new_detail_obj.middle_check_return_ids.create({
                "following_process_detail_id": new_detail_obj.id,
                "gGroup": self.group,
            })
            new_obj.sudo().set_middle_check_return()






    # 设置中查效率表数据信息
    def set_middle_check_efficiency(self):

        # 获取年
        month = self.date.month
        # 获取月
        year = self.date.year
        year_month = f"{year}-{month}"
        # 查询中查效率表
        middle_check_efficiency_objs = self.env["middle_check_efficiency"].sudo().search([
            ("month", "=", year_month),     # 月份
            ("middle_check_principal", "=", self.invest)    # 中查负责人
        ])
        # 如果存在
        if middle_check_efficiency_objs:
            middle_check_efficiency_objs.sudo().set_date()
        else:
            new_obj = self.env["middle_check_efficiency"].sudo().create({
                "month": year_month,
                "middle_check_principal": self.invest,
            })
            new_obj.sudo().set_date()


    # 设置中查漏查表数据
    def set_middle_check_omission_factor(self):

        # 获取年
        month = self.date.month
        # 获取月
        year = self.date.year
        year_month = f"{year}-{month}"
        # 查询中查漏查表
        middle_check_efficiency_objs = self.env["middle_check_omission_factor"].sudo().search([
            ("month", "=", year_month),     # 月份
            ("middle_check_principal", "=", self.invest)    # 中查负责人
        ])
        # 如果存在
        if middle_check_efficiency_objs:
            middle_check_efficiency_objs.sudo().set_date()
        else:
            new_obj = self.env["middle_check_omission_factor"].sudo().create({
                "month": year_month,
                "middle_check_principal": self.invest,
            })
            new_obj.sudo().set_date()



    @api.depends('date')
    def _compute_date_split(self):
        for record in self:
            # 日期
            date = record.date
            year = str(date).split('-')[0]
            month = str(date).split('-')[1]
            new_date = year + '-' + month
            record.date_split = new_date


    @api.depends('repairs_number', 'check_the_quantity')
    def repair(self):
        for i in self:
            if i.check_the_quantity:
                i.repair_rate = (i.repairs_number / i.check_the_quantity) * 100
            else:
                i.repair_rate = 0


    @api.model
    def create(self, val):
        #
        instance = super(invest, self).create(val)

        # 设置中查效率表数据信息
        instance.set_middle_check_efficiency()
        # 设置中查漏查表数据信息
        instance.set_middle_check_omission_factor()

        # 设置后道进出明细
        instance.set_following_process_detail()


        #    中查汇总表   有没有记录
        demo = self.env['detail.detail'].sudo().search([('invest', '=', val['invest']), ('item_no', '=', val['style_number'])])
        if demo:
            date = val['date']
            style_number = val['style_number']
            delivery_number = val['quantity_of_delivery'] + demo.delivery_number
            check_number = val['check_the_quantity'] + demo.check_number
            totle_repairs = val['repairs_number'] + demo.totle_repairs
            demo.sudo().unlink()
            if check_number:
                repair_rate = totle_repairs / check_number

                demo3 = self.env['invest.invest'].sudo().search([('invest', '=', val['invest']), ('style_number', '=', val['style_number'])])
                val2 = {
                    'date': date,
                    'invest': val['invest'],
                    'item_no': style_number,
                    'delivery_number': delivery_number,
                    'check_number': check_number,
                    'totle_repairs': totle_repairs,
                    'repair_rate': repair_rate * 100,
                    'invest_totle': [(6, 0, demo3.ids)]
                }
            else:
                demo3 = self.env['invest.invest'].sudo().search([('invest', '=', val['invest']), ('style_number', '=', val['style_number'])])
                val2 = {
                    'date': date,
                    'invest': val['invest'],
                    'item_no': style_number,
                    'delivery_number': delivery_number,
                    'check_number': check_number,
                    'totle_repairs': totle_repairs,
                    'repair_rate': 0,
                    'invest_totle': [(6, 0, demo3.ids)]
                }
            self.env['detail.detail'].sudo().create(val2)
        else:
            demo3 = self.env['invest.invest'].sudo().search([('invest', '=', val['invest']), ('style_number', '=', val['style_number'])])
            if val['check_the_quantity']:
                val2 = {
                    'date': val['date'],
                    'invest': val['invest'],
                    'item_no': val['style_number'],
                    'delivery_number': val['quantity_of_delivery'],
                    'check_number': val['check_the_quantity'],
                    'totle_repairs': val['repairs_number'],
                    'repair_rate': (val['repairs_number'] / val['check_the_quantity']) * 100,
                    'invest_totle': [(6, 0, demo3.ids)]
                }
            else:
                val2 = {
                       'date': val['date'],
                       'invest': val['invest'],
                       'item_no': val['style_number'],
                       'delivery_number': val['quantity_of_delivery'],
                       'check_number': val['check_the_quantity'],
                       'totle_repairs': val['repairs_number'],
                       'repair_rate': 0,
                       'invest_totle': [(6, 0, demo3.ids)]

                }
            self.env['detail.detail'].sudo().create(val2)

        # 生成品控统计表（月     中查）
        # 日期
        date = val['date']
        # 处理年月
        # date1 = date.strptime(date, )
        year = str(date).split('-')[0]
        month = str(date).split('-')[1]
        new_date = year + '-' + month
        # 组别
        group = val['group']
        # 款号
        style_number_id = val['style_number']
        style_number1 = self.env['ib.detail'].sudo().search([('id', '=', style_number_id)]).display_name
        style_number_douhao = style_number1 + ','
        demo = self.env['quality.control.statistics.table'].sudo().search([
            ('date', '=', new_date),
            ('group', '=', group),
        ])


        if demo:
            if style_number_douhao:
                if demo.style_number:
                    if style_number1 in demo.style_number.split(',')[:-1]:
                        style_number1 = demo.style_number
                    else:
                        style_number1 = demo.style_number + style_number1 + ','

            #     新的查货数量
            new_check_the_quantity = demo.check_the_quantity + val['check_the_quantity']
            #     新的中查返修数量
            new_intermediate_inspection_and_repair_number = demo.intermediate_inspection_and_repair_number + val[
                'repairs_number']
            #     中检返修率
            if new_check_the_quantity:
                new_intermediate_inspection_and_repair_rate = (new_intermediate_inspection_and_repair_number / new_check_the_quantity) * 100
                demo.sudo().write({
                    'style_number': style_number1,
                    'check_the_quantity': new_check_the_quantity,
                    'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                    'intermediate_inspection_and_repair_rate': new_intermediate_inspection_and_repair_rate
                })
            else:
                demo.sudo().write({
                    'style_number': style_number1,
                    'check_the_quantity': new_check_the_quantity,
                    'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                    'intermediate_inspection_and_repair_rate': 0
                })

        #     啥都没有的增加    todo
        else:
            style_number = ''
            if style_number1:
                if demo.style_number:
                    if style_number1 in demo.style_number.split(',')[:-1]:
                        style_number1 = demo.style_number
                    else:
                        style_number1 = demo.style_number + style_number1 + ','

            if val['check_the_quantity']:
                self.env['quality.control.statistics.table'].sudo().create({
                        'date': new_date,
                        'group': group,
                        'style_number': style_number_douhao,
                        'check_the_quantity': val['check_the_quantity'],
                        'intermediate_inspection_and_repair_number': val['repairs_number'],
                        'intermediate_inspection_and_repair_rate': (val['repairs_number'] /val['check_the_quantity']) * 100
                    })
            else:
                self.env['quality.control.statistics.table'].sudo().create({
                    'date': new_date,
                    'group': group,
                    'style_number': style_number_douhao,
                    'check_the_quantity': val['check_the_quantity'],
                    'intermediate_inspection_and_repair_number': val['repairs_number'],
                    'intermediate_inspection_and_repair_rate': 0
                })

        return instance

    def unlink(self):

        for record in self:
            # 总表
            detail_detail_objs = self.env["detail.detail"].sudo().search([
                ("item_no", '=', record.style_number.id),
                ('invest', '=', record.invest)
            ])

            demo = self.env['invest.invest'].sudo().search([('invest', '=', record.invest), ('style_number', '=', record.style_number.display_name)])
            if len(demo) == 1:
                detail_detail_objs.sudo().unlink()

            else:
                date = record.date
                old_invest =record.invest
                old_style_number = record.style_number
                demo1 = self.env['invest.invest'].sudo().search([('invest', '=', old_invest), ('style_number', '=', old_style_number.display_name)])
                delivery_number = record.quantity_of_delivery
                check_number = record.check_the_quantity
                totle_repairs = record.repairs_number
                new_delivery_number = detail_detail_objs.delivery_number - delivery_number
                new_check_number = detail_detail_objs.check_number - check_number
                new_totle_repairs = detail_detail_objs.totle_repairs - totle_repairs
                new_id = []
                for i in demo1.ids:
                    if i == record.id:
                        pass
                    else:
                        new_id.append(i)
                if new_check_number:
                    val = {
                        'date': date,
                        'invest': old_invest,
                        'item_no': old_style_number.id,
                        'delivery_number': new_delivery_number,
                        'check_number': new_check_number,
                        'totle_repairs': new_totle_repairs,
                        'repair_rate': (new_totle_repairs / new_check_number) * 100,
                        'invest_totle': [(6, 0, new_id)]
                    }
                else:
                    val = {
                        'date': date,
                        'invest': old_invest,
                        'item_no': old_style_number.id,
                        'delivery_number': new_delivery_number,
                        'check_number': new_check_number,
                        'totle_repairs': new_totle_repairs,
                        'repair_rate': 0,
                        'invest_totle': [(6, 0, new_id)]
                    }
                detail_detail_objs.write(val)

            #     删除品控统计表（月     中查）
            # 日期
            date = record.date
            #     处理年月
            # date1 = date.strptime(date, )
            year = str(date).split('-')[0]
            month = str(date).split('-')[1]
            new_date = year + '-' + month
            #     组别
            group = record.group
            #    这边通过日期, 组别    款号的删除
            style_number = record.style_number.display_name
            #    款号
            #    如果还有,     就是等着修改.   品控表的数据

            # 本表数据       组 款号   中查表的数据
            demo2 = self.env['invest.invest'].sudo().search([('style_number', '=', style_number), ('group', '=', group),('date_split', '=', new_date)])


            invest_date = date
            year = str(invest_date).split('-')[0]
            month = str(invest_date).split('-')[1]
            invest_new_date = year + '-' + month
            demo = self.env['quality.control.statistics.table'].sudo().search([
                ('date', '=', invest_new_date),
                ('group', '=', group),
            ])
            demo3 = demo.style_number.split(',')[:-1]
            if len(demo2) == 1 and len(demo3) == 1:
                demo.sudo().unlink()
            elif len(demo2) == 1:
                #    删除款号，重新计算
                #  款号
                style_number_totle = demo.style_number
                style_number_new = []
                for style_number_sigle in style_number_totle.split(',')[:-1]:
                    if style_number_sigle == style_number:
                        pass
                    else:
                        style_number_new.append(style_number_sigle)
                style_number_new_set = ','.join(style_number_new) + ','
                #     新的查货数量
                new_check_the_quantity = demo.check_the_quantity - record.check_the_quantity
                #     新的中查返修数量
                new_intermediate_inspection_and_repair_number = demo.intermediate_inspection_and_repair_number - record.repairs_number
                if new_check_the_quantity:
                    #     中检返修率
                    new_intermediate_inspection_and_repair_rate = (new_intermediate_inspection_and_repair_number / new_check_the_quantity) * 100
                    demo.sudo().write({
                        'style_number': style_number_new_set,
                        'check_the_quantity': new_check_the_quantity,
                        'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                        'intermediate_inspection_and_repair_rate': new_intermediate_inspection_and_repair_rate
                    })
                else:
                    demo.sudo().write({
                        'style_number': style_number_new_set,
                        'check_the_quantity': new_check_the_quantity,
                        'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                        'intermediate_inspection_and_repair_rate': 0
                    })
            else:
                #        重新计算
                #     新的查货数量
                new_check_the_quantity = demo.check_the_quantity - record.check_the_quantity
                #     新的中查返修数量
                new_intermediate_inspection_and_repair_number = demo.intermediate_inspection_and_repair_number - record.repairs_number
                if new_check_the_quantity:
                    #     中检返修率
                    new_intermediate_inspection_and_repair_rate = (new_intermediate_inspection_and_repair_number / new_check_the_quantity) * 100
                    demo.sudo().write({
                        'check_the_quantity': new_check_the_quantity,
                        'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                        'intermediate_inspection_and_repair_rate': new_intermediate_inspection_and_repair_rate
                    })
                else:
                    demo.sudo().write({
                        'check_the_quantity': new_check_the_quantity,
                        'intermediate_inspection_and_repair_number': new_intermediate_inspection_and_repair_number,
                        'intermediate_inspection_and_repair_rate': 0
                })


            # 获取年
            month = record.date.month
            # 获取月
            year = record.date.year
            year_month = f"{year}-{month}"
            # 中查负责人
            invest_personnel = record.invest
            # 款号
            style_number = record.style_number.id
            # 日期
            dDate = record.date
            # 组
            gGroup = record.group

            super(invest, record).unlink()

            # 删除时，总检效率表一起跟新数据
            middle_check_efficiency_objs = self.env["middle_check_efficiency"].sudo().search([
                ("month", "=", year_month),     # 月份
                ("middle_check_principal", "=", invest_personnel)    # 中查负责人
            ])
            if middle_check_efficiency_objs:
                middle_check_efficiency_objs.sudo().set_date()

            # 删除时，总检效率表一起跟新数据
            middle_check_omission_factor_objs = self.env["middle_check_omission_factor"].sudo().search([
                ("month", "=", year_month),     # 月份
                ("middle_check_principal", "=", invest_personnel)    # 中查负责人
            ])
            if middle_check_omission_factor_objs:
                middle_check_omission_factor_objs.sudo().set_date()



            # 删除时，设置后道进出明细
            middle_check_return_line_obj = self.env["middle_check_return_line"].sudo().search([
                ("dDate", "=", dDate),
                ("gGroup", "=", gGroup)
            ])
            if middle_check_return_line_obj:
                middle_check_return_line_obj.sudo().set_middle_check_return()


        return super(invest, self).unlink()


class detail(models.Model):
    _name = 'detail.detail'
    _description = '中查返修汇总表'
    _order = "date desc"


    date = fields.Date(string='日期')
    invest = fields.Char(string='中查')
    item_no = fields.Many2one('ib.detail',  string='款号')

    delivery_number = fields.Integer(string='交货数量')

    check_number = fields.Integer(string='查货数量')
    totle_repairs = fields.Integer(string='返修汇总')
    repair_rate = fields.Float(string='返工率(%)', group_operator='avg')
    invest_totle = fields.Many2many('invest.invest', string="中查明细", ondelete='cascade')


class totle(models.Model):
    _name = 'summary'
    _description = '汇总表'

    date = fields.Date(string='日期')
    group = fields.Char(string='组别')
    item_no = fields.Many2one('ib.detail', string='款号')
    order_number = fields.Integer(string='订单数')
    number_of_cutting_beds = fields.Integer(string='裁床数')
    number_of_pieces_on_the_collar = fields.Integer(string='组上领裁片数')
    number_of_lead_offs_in_the_group = fields.Integer(string='组上领交后道数')
    inspection_name = fields.Char(string='中检姓名')
    number_of_back_end_warehousing = fields.Integer(string='后道入仓数')
    number_of_customer_returns = fields.Integer(string='客户退仓数')
    number_of_warehouses = fields.Integer(string='出仓数')


class summary_statistics(models.Model):
    _name = 'summary.statistics'
    _description = '汇总统计表'
    group = fields.Char(string='组别')
    item_no = fields.Many2one('ib.detail', string='款号')
    style_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    order_number = fields.Integer(string='订单数')
    number_of_cutting_beds = fields.Integer(string='领裁床数')
    number_of_deliveries_in_group = fields.Integer(string='组上交货数')
    unpaid_number_on_group = fields.Integer(string='组上未交数')
    number_of_post_delivery_positions = fields.Integer(string='后道交仓数')
    number_of_custonmer_returns = fields.Integer(string='客户退仓数')
    number_of_custonmer_delivered = fields.Integer(string='交付客户数')
    order_delivery = fields.Integer(string='订单未交数')


class quality_control_statistics_table(models.Model):
    _name = 'quality.control.statistics.table'
    _description = '品控统计表（月）'

    date = fields.Char(string='日期')
    group = fields.Char(string='组别')
    style_number = fields.Char(string='款号')
    intermediate_inspection_and_repair_rate = fields.Float(string='中检返修率(%)')

    check_the_quantity = fields.Float(string='查货数量')
    intermediate_inspection_and_repair_number = fields.Float(string='中检返修数量')


