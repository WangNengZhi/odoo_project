from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

import itertools
import logging

_logger = logging.getLogger(__name__)


class StationSummaryseqnoLine(models.Model):
    """ 继承站位吊挂明细"""
    _inherit = 'station_summaryseqno_line'


    automatic_scene_process_id = fields.Many2one("automatic_scene_process", string="自动现场工序")



class AutomaticSceneProcess(models.Model):
    _name = 'automatic_scene_process'
    _description = '自动现场工序'
    _rec_name = 'employee_id'
    _order = "date desc"

    date = fields.Date(string='日期')
    employee_id = fields.Many2one("hr.employee", string="员工id", compute='_set_employee_id', store=True)
    work_number = fields.Char(string="工号")
    work_type = fields.Char(string="工种", compute="set_work_type", store=True)
    departure_date = fields.Date(string="离职日期", compute="set_work_type", store=True)
    group = fields.Many2one('check_position_settings', string='组别')
    station_number = fields.Char(string="站号")
    style_number_id = fields.Many2one('ib.detail', string='款号id')
    style_number = fields.Char(string="款号")

    process_id = fields.Many2one('work.work', string="工序id", compute="set_process_info", store=True)
    process_number = fields.Char(string="工序号")
    process_describe = fields.Char(string="工序描述", compute="set_process_info", store=True)
    process_level = fields.Char(string="工序等级", compute="set_process_info", store=True)
    process_time = fields.Float(string="标准时间", compute="set_process_info", store=True)
    process_price = fields.Float(string="工序价格", compute="set_process_info", store=True)
    number = fields.Float(string="件数", compute="set_number", store=True)
    # number = fields.Float(string="件数")

    process_wages = fields.Float(string="工序工资", compute="_set_process_wages", store=True)

    is_affirm_state = fields.Selection([
        ('有异议', '有异议'),
        ('已确认', '已确认'),
        ('系统', '系统'),
    ], string="产量状态")

    # state = fields.Selection([('自动', '自动'), ('手动', '手动')], string="记录状态", default="手动")
    process_state = fields.Selection([('已确认', '已确认'), ('系统', '系统')], string="工序状态", default="已确认")


    station_summaryseqno_line_objs = fields.One2many("station_summaryseqno_line", "automatic_scene_process_id", string="吊挂工序")

    dg_piece_rate_id = fields.Many2one("dg_piece_rate", string="吊挂计件工资")

    auto_employee_information_id = fields.Many2one("auto_employee_information", string="自动员工信息", compute="_set_auto_employee_information_id", store=True)



    # 设置工序信息
    @api.depends('process_number')
    def set_process_info(self):
        for record in self:

            ib_detail_objs = self.env["ib.detail"].sudo().search([
                ("style_number", "like", record.style_number),
                # ], limit=1, order="date desc")
                ], order="date")


            if ib_detail_objs:
                for ib_detail_obj in ib_detail_objs:
                    _logger.info(f'查询到款号！{ib_detail_obj.style_number}')


                    work_work_obj = self.env["work.work"].sudo().search([
                        ("employee_id", "=", record.process_number),
                        ("order_number", "=", ib_detail_obj.id),
                    ])
                    if work_work_obj:
                        _logger.info(f'查询到工序单！')

                        record.sudo().write({
                            "process_id": work_work_obj.id,     # 工序id
                            "process_describe": work_work_obj.process_abbreviation,     # 工序描述
                            "process_level": work_work_obj.process_level,  # 工序等级
                            "process_time": work_work_obj.standard_time,   # 工序时间
                            "process_price": work_work_obj.standard_price   # 工序价格
                        })
                        break
                    else:
                        _logger.error(f'没查询到工序单！')
            else:
                _logger.error(f'没查询到款号！')




    # 设置工种，在职状态
    @api.depends('employee_id')
    def set_work_type(self):
        for record in self:
            record.work_type = record.employee_id.is_it_a_temporary_worker

            record.departure_date = record.employee_id.is_delete_date


    # 设置员工信息
    @api.depends('work_number')
    def _set_employee_id(self):
        for record in self:
            if record.work_number:
                hr_employee_obj = self.env["hr.employee"].sudo().search([("barcode", "=", record.work_number)])
                record.employee_id = hr_employee_obj.id


    # 计算件数 设置状态
    @api.depends('station_summaryseqno_line_objs', 'station_summaryseqno_line_objs.number')
    def set_number(self):
        for record in self:

            record.number = sum(record.station_summaryseqno_line_objs.mapped('number'))

            if record.station_summaryseqno_line_objs:

                record.is_affirm_state = record.station_summaryseqno_line_objs[0].is_affirm_state
                # record.is_affirm_state = "已确认"


    # 计算工序工资
    @api.depends('process_price', 'number')
    def _set_process_wages(self):
        for record in self:

            record.process_wages = record.process_price * record.number


    # 设置自动员工信息表
    @api.depends('date', 'employee_id', 'group')
    def _set_auto_employee_information_id(self):
        for record in self:

            obj = self.auto_employee_information_id.sudo().create({
                "date": record.date,
                "employee_id": record.employee_id.id,
                "group_id": record.group.id
            })

            record.auto_employee_information_id = obj.id



    # 设置吊挂计件工资
    def set_dg_piece_rate(self, today):

        # 日期减少一天
        today = today - timedelta(days=1)

        objs = self.sudo().search([("date", "=", today), ("employee_id", "!=", False)], order="group")

        for group_id, group_objs in itertools.groupby(objs, key=lambda x:x.group.id):     # 按组别分组

            group_objs_list = list(group_objs)

            group_objs_list.sort(key=lambda x: x.employee_id.id, reverse=False)     # 按员工排序

            for employee_id, employee_objs in itertools.groupby(group_objs_list, key=lambda x:x.employee_id.id):     # 再按员工分组

                dg_piece_rate_obj = self.env["dg_piece_rate"].sudo().create({
                    "date": today,
                    "employee_id": employee_id,
                    "group_id": group_id,
                })

                employee_objs_list = list(employee_objs)

                for employee_obj in employee_objs_list:
                    employee_obj.dg_piece_rate_id = dg_piece_rate_obj.id






    # 设置件数
    def set_station_summaryseqno_line_objs(self, today):

        # 日期减少一天
        today = today - timedelta(days=1)

        # 按日期查询现场工序
        wechat_process_confirm_objs = self.env["automatic_scene_process"].sudo().search([
            ("date", "=", today)
        ])
        # 循环现场工序
        for record in wechat_process_confirm_objs:
            # 查询吊挂产量
            suspension_system_station_summary_objs = self.env["suspension_system_station_summary"].sudo().search([
                ("dDate", "=", record.date),    # 日期
                ("employee_id", "=", record.employee_id.id),   # 员工
                ("group", "=", record.group.id),     # 组别
                ("station_number", "=", int(record.station_number)),      # 站号
                ("style_number", "like", record.style_number),      # 款号
            ])
            # 循环吊挂产量
            for suspension_system_station_summary_obj in suspension_system_station_summary_objs:
                # 查询吊挂产量明细
                station_summaryseqno_line_objs = self.env["station_summaryseqno_line"].sudo().search([
                    ("seqno_id", "=", suspension_system_station_summary_obj.id),
                    ("SeqNo", "=", int(record.process_number)),
                ])
                print(station_summaryseqno_line_objs)

                for station_summaryseqno_line_obj in station_summaryseqno_line_objs:
                    station_summaryseqno_line_obj.automatic_scene_process_id = record.id

            # record.is_affirm_state = "已确认"


    # 自动生成工序
    def auto_generate_process(self, today):

        suspension_system_station_summary_objs = self.env["suspension_system_station_summary"].sudo().search([
            ("dDate", "=", today),    # 日期
        ])

        for suspension_system_station_summary_obj in suspension_system_station_summary_objs:

            if suspension_system_station_summary_obj.style_number:
                style_number = suspension_system_station_summary_obj.style_number.style_number.split("-")

                if len(style_number) <= 2:
                    style_number = style_number[0]
                else:
                    style_number = "-".join(style_number[0:-1])

                for dg_line in suspension_system_station_summary_obj.line_lds:

                    automatic_scene_process_objs = self.env["automatic_scene_process"].sudo().search([
                        ("date", "=", today),   # 日期
                        ("employee_id", "=", suspension_system_station_summary_obj.employee_id.id),     # 员工
                        ("group", "=", suspension_system_station_summary_obj.group.id),     # 组别
                        ("style_number", "=", style_number),    # 款号
                        ("station_number", "=", suspension_system_station_summary_obj.station_number),  # 站号
                        ("process_number", "=", dg_line.SeqNo),     # 工序号
                    ])
                    if automatic_scene_process_objs:
                        pass
                    else:
                        self.env["automatic_scene_process"].sudo().create({
                            "date": today,  # 日期
                            # "employee_id": suspension_system_station_summary_obj.employee_id.id,    # 员工
                            "work_number": suspension_system_station_summary_obj.employee_id.barcode,   # 工号
                            "style_number": style_number,   # 款号
                            "group": suspension_system_station_summary_obj.group.id,    # 组别
                            "station_number": str(suspension_system_station_summary_obj.station_number),    # 站号
                            "process_number": dg_line.SeqNo,    # 工序号
                            "process_state": "系统",    # 工序状态
                        })











