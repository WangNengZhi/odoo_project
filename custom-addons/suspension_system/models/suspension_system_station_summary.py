from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import requests
import json
from utils import weixin_utils
import collections
import itertools



class SuspensionSystemStationSummary(models.Model):
    _name = 'suspension_system_station_summary'
    _description = '吊挂站号产量汇总'
    # _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    group = fields.Many2one('check_position_settings', string='组别')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号（对象）')
    order_number_show = fields.Char(string="订单号")
    style_number = fields.Many2one('ib.detail', string='款号（对象）')
    MONo = fields.Char(string="款号")
    employee_id = fields.Many2one('hr.employee', string='员工')
    job_id = fields.Many2one("hr.job", string="岗位")
    employee_level = fields.Char(string="员工等级", compute="set_employee_level", store=True)
    station_number = fields.Integer(string="站号")
    rack_cnt = fields.Integer(string="衣架数量")
    rack_cap = fields.Integer(string="衣架容量")
    SeqNo = fields.Integer(string="工序号")
    production_value = fields.Float(string="产值", compute="set_production_value", store=True)
    total_quantity = fields.Integer(string="总件数")
    workpiece_ratio = fields.Float(string="效率", compute="set_workpiece_ratio", store=True)

    last_record = fields.Many2one("suspension_system_station_summary", string="上一个小时的记录")

    # last_total_quantity = fields.Integer(string="上一次执行时的件数")

    line_lds = fields.One2many("station_summaryseqno_line", "seqno_id", string="工序明细")


    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.dDate}-{record.group.group}-{record.station_number}"
            result.append((record.id, rec_name))
        return result


    # 用于手动刷新工序明细中的标准时间
    def refresh_standard_time(self):
        for record in self:
            for line_obj in record.line_lds:
                line_obj.sudo().set_standard_time()


    # 设置员工等级
    @api.depends('employee_id')
    def set_employee_level(self):
        for record in self:

            if record.group.group == "后整":
                if record.employee_id.job_id:
                    record.employee_level = record.employee_id.job_id.name
            else:
                if record.employee_id.staff_level:
                    record.employee_level = record.employee_id.staff_level



    # 计算产值
    @api.depends('total_quantity', 'order_number', 'order_number.order_price')
    def set_production_value(self):
        for record in self:

            record.production_value = record.total_quantity * float(record.order_number.order_price)


    # 计算效率
    @api.depends('style_number', 'line_lds.number', 'line_lds.standard_time', 'line_lds.update_number')
    def set_workpiece_ratio(self):

        today = datetime.now().date()
        # 开始时间 当天8点
        start_time = datetime(today.year, today.month, today.day, 0, 0, 0) + timedelta(hours=8)
        # 结束时间 当天21点（11个小时）
        end_time = datetime(today.year, today.month, today.day, 0, 0, 0) + timedelta(hours=19)
        # 现在时间
        current_time = datetime.now() + timedelta(hours=8)


        for record in self:
            # 如果不是当天
            if today != record.dDate:
                work_time = 39600
            else:

                if current_time > end_time:
                    work_time = int((end_time - start_time).total_seconds())
                else:
                    work_time = int((current_time - start_time).total_seconds())


            tem_val = 0

            # 8点之后才计算效率
            if current_time > start_time:

                for line_obj in record.line_lds:

                    tem_val = tem_val + (line_obj.standard_time * line_obj.number)

                record.workpiece_ratio = (tem_val / work_time) * 100






    # 获取员工对象
    def get_employee_name(self, EmpID):

        hr_employee_obj = self.env["hr.employee"].sudo().search([
            ("barcode", "=", EmpID)
        ])
        # 返回员工对象
        return hr_employee_obj


    # 获取订单编号
    def get_order_number(self, SeqCode):

        order_number_obj = self.env["sale_pro.sale_pro"].sudo().search([("order_number", "=", SeqCode)])
        # 返回订单对象
        return order_number_obj






    # 记录上的件数和产值全部设置为0
    def empty_records(self, start_time, group):

        # 查询汇总表是否已经存在数据
        suspension_system_summary_objs = self.env["suspension_system_station_summary"].sudo().search([
            ("dDate", "=", start_time),     # 日期
            ("group", "=", group),  # 组别
        ])

        for suspension_system_summary_obj in suspension_system_summary_objs:

            suspension_system_summary_obj.sudo().write({
                "SeqNo": 0,
                "total_quantity": 0,
                # "production_value": 0,
            })




    def send_daily_summary_to_enterprise_weixin(self, message_group="测试群"):
        ''' 将吊挂各组最慢员工每日统计发到企业微信 '''
        # print('*'*80)
        # print('send_daily_summary_to_enterprise_weixin()')

        today = datetime.now().date()
        # today = datetime(2021, 12, 6)
        data = self.sudo().search([('dDate','=',today)])

        stats = {}
        involved_employees = {}
        EMPLOYEE, STATION = 0, 1
        for x in data:
            if x.group not in stats:
                stats[x.group] = collections.Counter()
            if x.employee_id:
                key = EMPLOYEE, x.employee_id.id
                involved_employees[x.employee_id.id] = x.employee_id
            else:
                key = STATION, x.station_number
            stats[x.group][key] += x.total_quantity
        if not stats:
            return

        def format(group, cnter, involved_employees):
            def _format(t, id):
                if t == EMPLOYEE:
                    return f'{involved_employees[id].name}'
                else:  # STATION
                    return f'站号{id}'

            s = ''
            mini = min(cnter.values())
            s += f'{group.group}：'
            if all(n==mini for n in cnter.values()):
                s += f'各人产量相同（{mini}件）'
            else:
                workers = [worker for worker, n in cnter.items() if n == mini]
                if len(workers) > 1:
                    (t, id), *others = workers
                    s += '、'.join(_format(t,id) for t,id in others) + '和' + _format(t,id)
                else:
                    (t, id), *_ = workers
                    s += _format(t,id)
                # s += '产量最少。'
                # s += repr(workers)
            return s

        text = f'吊挂各组最慢员工统计（{today.year}年{today.month}月{today.day}日）：\n\n'
        text += '\n'.join(format(group,cnter,involved_employees) for group, cnter in stats.items())
        # print('*'*80)
        # print(text)
        if message_group == "管理群":
            weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.ALL_PERSONNEL)  # 风丝袅全员群
        elif message_group == "测试群":
            weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.DEVELOPMENT_AND_TEST)  # 开发测试群




class StationSummarySeqnoLine(models.Model):
    _name = 'station_summaryseqno_line'
    _description = '吊挂站号产量汇总工序明细'
    _rec_name = 'SeqNo'

    seqno_id = fields.Many2one("suspension_system_station_summary", ondelete="cascade")
    SeqNo = fields.Integer(string="工序号")
    standard_time = fields.Float(string="标准用时", compute="set_standard_time", store=True)
    number = fields.Integer(string="数量")
    update_number = fields.Integer(string="更新次数")
    is_update = fields.Boolean(string="是否活跃")
    first_time = fields.Datetime(string="第一件时间")
    last_time = fields.Datetime(string="最后一件时间")


    # 获取标准时间
    @api.depends('seqno_id', 'SeqNo')
    def set_standard_time(self):

        for record in self:

            work_work_obj = self.env["work.work"].sudo().search([
                ("order_number", "=", record.seqno_id.style_number.id),    # 款号
                ("employee_id", "=", str(record.SeqNo)),       # 工序号
            ])

            record.standard_time = work_work_obj.standard_time