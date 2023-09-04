from odoo import api, fields, models

import datetime
import calendar

from typing import List



class SendOutOutputValue(models.Model):
    _name = 'send_out_output_value'
    _description = '外发产值（外发主管）'
    _rec_name = 'employee_id'


    year_month = fields.Char(string="月份")
    employee_id = fields.Many2one('hr.employee', string='负责人')
    entry_time = fields.Date(string='入职日期')
    is_delete_date = fields.Date(string='离职日期')
    department_id = fields.Many2one("hr.department", string="部门", compute="set_employee_info", store=True)
    job_id = fields.Many2one('hr.job', string='岗位', compute="set_employee_info", store=True)
    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            record.job_id = record.employee_id.job_id.id
            record.department_id = record.employee_id.department_id.id
    number = fields.Integer(string="人数")

    plann_output_value = fields.Float(string="计划产值")
    actual_finished_number = fields.Integer(string="实际完成件数")
    actual_finished_output_value = fields.Float(string="实际完成产值")
    progress = fields.Float(string="进度", compute="set_progress", store=True)
    @api.depends('plann_output_value', 'actual_finished_output_value')
    def set_progress(self):
        for record in self:
            if record.plann_output_value:
                record.progress = (record.actual_finished_output_value / record.plann_output_value) * 100
            else:
                record.progress = 0

    following_repair_number = fields.Integer(string="后道退回件数")
    following_repair_number_ratio = fields.Float(string="后道退回率", compute="set_ratio", store=True)

    client_warehouse_repair_number = fields.Integer(string="客仓返修件数")
    client_warehouse_repair_number_ratio = fields.Float(string="客仓返修率", compute="set_ratio", store=True)


    @api.depends('actual_finished_number', 'following_repair_number', 'client_warehouse_repair_number')
    def set_ratio(self):
        for record in self:
            if record.actual_finished_number:
                record.following_repair_number_ratio = record.following_repair_number / record.actual_finished_number
                record.client_warehouse_repair_number_ratio = record.client_warehouse_repair_number / record.actual_finished_number
            else:
                record.following_repair_number_ratio = 0
                record.client_warehouse_repair_number_ratio = 0


    send_out_output_value_line_ids = fields.One2many("send_out_output_value_line", "send_out_output_value_id", string="外发产值（外发主管）明细")
    delay_time_days = fields.Integer(string="误期天数", compute="set_delay_time_info", store=True)
    delay_time_quantity = fields.Integer(string="误期件数", compute="set_delay_time_info", store=True)
    @api.depends('send_out_output_value_line_ids', 'send_out_output_value_line_ids.order_quantity', 'send_out_output_value_line_ids.stock')
    def set_delay_time_info(self):
        for record in self:

            if record.send_out_output_value_line_ids:
                obj = max(record.send_out_output_value_line_ids, key=lambda x: x.date)
                record.delay_time_days = obj.delay_time_days
                record.delay_time_quantity = obj.order_quantity - obj.stock
            else:
                record.delay_time_days = 0
                record.delay_time_quantity = 0

    loss_quantity = fields.Integer(string="损耗件数")


    def set_begin_and_end(self, year, month):
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end



    def current_month_in_service_days(self, send_out_output_value_obj, this_month_start, this_month_end):
        ''' 计算当月在职日期范围'''
        print(send_out_output_value_obj.employee_id.entry_time, this_month_start)
        if send_out_output_value_obj.employee_id.entry_time < this_month_start:

            if not send_out_output_value_obj.employee_id.is_delete or send_out_output_value_obj.employee_id.is_delete_date > this_month_end:
                return this_month_start, this_month_end
            else:
                return this_month_start, send_out_output_value_obj.employee_id.is_delete_date
        else:
            if not send_out_output_value_obj.employee_id.is_delete or send_out_output_value_obj.employee_id.is_delete_date > this_month_end:
                return send_out_output_value_obj.employee_id.entry_time, this_month_end
            else:
                return send_out_output_value_obj.employee_id.entry_time, send_out_output_value_obj.employee_id.is_delete_date


    def detect_and_generate_record(self, year_month: str) -> List:
        ''' 检测并生成记录'''


        send_out_output_value_list = list(self.env['send_out_output_value'].sudo().search([("year_month", "=", year_month)]))

        staff_number = self.env["hr.employee"].sudo().search_count([("is_delete", "=", False), ("department_id.name", "=", "外发部")])


        group_leader_objs = self.env['hr.employee'].sudo().search([
            ("is_delete", "=", False), ("job_id.name", "in", ["外发兼品控主管", "外发主管", "生产总监"])
        ], order='entry_time desc')

        for group_leader_obj in group_leader_objs:

            if not self.env['send_out_output_value'].sudo().search([("year_month", "=", year_month), ("employee_id", "=", group_leader_obj.id)]):
                send_out_output_value_list.append(self.env['send_out_output_value'].sudo().create({
                    "year_month": year_month,
                    "number": staff_number,
                    "employee_id": group_leader_obj.id,
                }))


        return send_out_output_value_list



    def refresh_actual_finished_output_value(self, start_date, end_date, send_out_output_value_obj) -> None:
        ''' 刷新实际完成件数'''

        outgoing_output_objs = self.env['outgoing_output'].sudo().search([("date", ">=", start_date),("date", "<=", end_date)])

        send_out_output_value_obj.actual_finished_output_value = sum(outgoing_output_objs.mapped("pro_value"))
        send_out_output_value_obj.actual_finished_number = sum(outgoing_output_objs.mapped("number"))


    def refresh_following_repair_number(self, start_date, end_date, send_out_output_value_obj) -> None:
        ''' 刷新后道返修件数'''

        posterior_passage_statistical_objs = self.env['posterior_passage_statistical'].sudo().search([("group", "=", "外发"),("dDate", ">=", start_date),("dDate", "<=", end_date)])
        
        send_out_output_value_obj.following_repair_number = sum(posterior_passage_statistical_objs.mapped("dg_rework_number"))


    def refresh_client_warehouse_repair_number(self, start_date, end_date, send_out_output_value_obj) -> None:
        ''' 刷新客仓返修件数'''

        client_ware_objs = self.env['client_ware'].sudo().search([("gGroup", "=", "外发"),("dDate", ">=", start_date),("dDate", "<=", end_date)])
            
        send_out_output_value_obj.client_warehouse_repair_number = sum(client_ware_objs.mapped("repair_number"))



    def refresh_send_out_output_value_line(self, start_date, end_date, send_out_output_value_obj, current_date) -> None:
        ''' 刷新外发产值明细'''
        outsource_order_objs = self.env["outsource_order"].sudo().search([
            ("approval_state", "=", "待审批"),
            ("state", "not in", ['已完成', '退单']),
            ("customer_delivery_time", ">=", start_date),
            ("customer_delivery_time", "<=", end_date)
        ])
        
        order_quantity = 0
        stock = 0
        delay_time_days = 0

        for outsource_order_obj in outsource_order_objs:

            if outsource_order_obj.customer_delivery_time < current_date:

                order_quantity += outsource_order_obj.order_quantity
                stock += outsource_order_obj.stock
                delay_time_days += (current_date - outsource_order_obj.customer_delivery_time).days


        send_out_output_value_line_obj = self.env['send_out_output_value_line'].sudo().search([
            ("send_out_output_value_id", "=", send_out_output_value_obj.id),
            ("date", "=", current_date),
        ])
        if not send_out_output_value_line_obj:
            send_out_output_value_line_obj = self.env['send_out_output_value_line'].sudo().create({
                "send_out_output_value_id": send_out_output_value_obj.id,
                "date": current_date,   # 日期  
            })

        send_out_output_value_line_obj.delay_time_days = delay_time_days     # 逾期天数
        send_out_output_value_line_obj.order_quantity = order_quantity   # 订单数
        send_out_output_value_line_obj.stock = stock      # 存量


    def refresh_loss_quantity(self, start_date, end_date, send_out_output_value_obj, current_date):
        ''' 刷新损耗'''

        loss_quantity = 0

        schedule_production_objs = self.env['schedule_production'].sudo().search([("date_contract", ">=", start_date),("date_contract", "<=", end_date),("processing_type", "=", "外发")])

        for schedule_production_obj in schedule_production_objs:

            if schedule_production_obj.order_number.is_finish != "退单" and schedule_production_obj.date_contract < current_date:
                
                loss_quantity += (schedule_production_obj.factory_delivery_variance + schedule_production_obj.defective_number)

        send_out_output_value_obj.loss_quantity = loss_quantity


    # 刷新目标产值
    def refresh_send_out_output_value(self) -> None:
        ''' 刷新外发产值'''

        current_date = fields.Date.today()
        
        if current_date.month < 10:
            year_month = f"{current_date.year}-0{current_date.month}"
        else:
            year_month = f"{current_date.year}-{current_date.month}"

        this_month_start, this_month_end = self.set_begin_and_end(current_date.year, current_date.month)

        send_out_output_value_list = self.detect_and_generate_record(year_month)

        for send_out_output_value_obj in send_out_output_value_list:

            if send_out_output_value_obj.employee_id:
                start_date, end_date =  self.current_month_in_service_days(send_out_output_value_obj, this_month_start, this_month_end)
                send_out_output_value_obj.entry_time = send_out_output_value_obj.employee_id.entry_time
                send_out_output_value_obj.is_delete_date = send_out_output_value_obj.employee_id.is_delete_date
            else:
                start_date, end_date =  this_month_start, this_month_end

            self.refresh_actual_finished_output_value(start_date, end_date, send_out_output_value_obj)

            self.refresh_following_repair_number(start_date, end_date, send_out_output_value_obj)

            self.refresh_client_warehouse_repair_number(start_date, end_date, send_out_output_value_obj)

            self.refresh_send_out_output_value_line(start_date, end_date, send_out_output_value_obj, current_date)

            self.refresh_loss_quantity(start_date, end_date, send_out_output_value_obj, current_date)






class SendOutOutputValueLine(models.Model):
    _name = 'send_out_output_value_line'
    _description = '外发产值（外发主管）明细'


    send_out_output_value_id = fields.Many2one("send_out_output_value", string="外发产值（外发主管）", ondelete="cascade")
    date = fields.Date(string="日期")
    delay_time_days = fields.Integer(string="逾期天数")
    outsource_order_id = fields.Many2one("outsource_order", string="外发订单")
    order_quantity = fields.Integer(string="订单数")
    stock = fields.Integer(string="存量")

