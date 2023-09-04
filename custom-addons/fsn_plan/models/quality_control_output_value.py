from odoo import api, fields, models


import datetime
import calendar


class QualityControlOutputValue(models.Model):
    _name = 'quality_control_output_value'
    _description = '品控产值（品控主管）'
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


    group_repair_number = fields.Float(string="组返修件数")
    group_repair_number_ratio = fields.Float(string="组返修率", compute="set_group_repair_number_ratio", store=True)
    @api.depends('group_repair_number', 'actual_finished_number')
    def set_group_repair_number_ratio(self):
        for record in self:
            if record.actual_finished_number:
                record.group_repair_number_ratio = record.group_repair_number / record.actual_finished_number
            else:
                record.group_repair_number_ratio = 0

    following_repair_number = fields.Integer(string="后道退回件数")
    following_repair_number_ratio = fields.Float(string="后道退回率", compute="set_following_repair_number_ratio", store=True)
    @api.depends('following_repair_number', 'actual_finished_number')
    def set_following_repair_number_ratio(self):
        for record in self:
            if record.actual_finished_number:
                record.following_repair_number_ratio = record.following_repair_number / record.actual_finished_number
            else:
                record.following_repair_number_ratio = 0

    client_warehouse_repair_number = fields.Integer(string="客仓返修件数")
    client_warehouse_repair_number_ratio = fields.Float(string="客仓返修率", compute="set_client_warehouse_repair_number_ratio", store=True)
    @api.depends('client_warehouse_repair_number', 'actual_finished_number')
    def set_client_warehouse_repair_number_ratio(self):
        for record in self:
            if record.actual_finished_number:
                record.client_warehouse_repair_number_ratio = record.client_warehouse_repair_number / record.actual_finished_number
            else:
                record.client_warehouse_repair_number_ratio = 0

    quality_control_output_value_overdue_line_ids = fields.One2many("quality_control_output_value_overdue_line", "quality_control_output_value_id", string="逾期明细")
    delay_time_days = fields.Integer(string="误期天数", compute="set_delay_time_info", store=True)
    delay_time_quantity = fields.Integer(string="误期件数", compute="set_delay_time_info", store=True)
    @api.depends('quality_control_output_value_overdue_line_ids', 'quality_control_output_value_overdue_line_ids.order_quantity', 'quality_control_output_value_overdue_line_ids.stock')
    def set_delay_time_info(self):
        for record in self:
            if record.quality_control_output_value_overdue_line_ids:
                obj = max(record.quality_control_output_value_overdue_line_ids, key=lambda x: x.date)
                record.delay_time_days = obj.delay_time_days
                record.delay_time_quantity = obj.order_quantity - obj.stock
            else:
                record.delay_time_days = 0
                record.delay_time_quantity = 0





    def set_begin_and_end(self, year, month):
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end



    def current_month_in_service_days(self, send_out_output_value_obj, this_month_start, this_month_end):
        ''' 计算当月在职日期范围'''

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



    def detect_and_generate_record(self, year_month: str) -> list:
        ''' 检测并生成记录'''

        quality_control_output_value_list = list(self.env['quality_control_output_value'].sudo().search([("year_month", "=", year_month)]))

        staff_number = self.env["hr.employee"].sudo().search_count([("is_delete", "=", False), '|', ("department_id.name", "=", "品控部"), ('department_id.parent_id.name', "=", "品控部")])

        group_leader_objs = self.env['hr.employee'].sudo().search([
            ("is_delete", "=", False),
            "|", ("job_id.name", "=", "外发兼品控主管"), ("job_id.name", "=", "品控主管")
        ], order='entry_time desc')

        if group_leader_objs:
            if not self.env['quality_control_output_value'].sudo().search([("year_month", "=", year_month), ("employee_id", "=", group_leader_objs[0].id)]):
                quality_control_output_value_list.append(self.env['quality_control_output_value'].sudo().create({
                    "year_month": year_month,
                    "number": staff_number,
                    "employee_id": group_leader_objs[0].id,
                }))
        else:
            if not self.env['quality_control_output_value'].sudo().search([("year_month", "=", year_month)]):
                quality_control_output_value_list.append(self.env['quality_control_output_value'].sudo().create({
                    "year_month": year_month,
                    "number": staff_number,
                }))

        return quality_control_output_value_list



    def refresh_actual_finished_output_value(self, start_date, end_date, quality_control_output_value_obj) -> None:
        ''' 刷新实际完成件数'''

        finished_product_ware_line_objs = self.env['finished_product_ware_line'].sudo().search([
            ("date", ">=", start_date),
            ("date", "<=", end_date),
            ("type", "=", "入库"),
            ("quality", "=", "合格"),
            ("character", "=", "正常")
        ])

        quality_control_output_value_obj.actual_finished_number = sum(finished_product_ware_line_objs.mapped("number"))
        quality_control_output_value_obj.actual_finished_output_value = sum(float(i.order_number.order_price) * i.number for i in finished_product_ware_line_objs)


    def refresh_delay_time_info(self, start_date, end_date, quality_control_output_value_obj, current_date) -> None:
        '''刷新逾期信息'''

        schedule_production_objs = self.env['schedule_production'].sudo().search([
            ("state", "=", "未完成"),
            ("processing_type", "in", ["外发", "工厂"]),
            ("date_contract", ">=", start_date),
            ("date_contract", "<=", end_date)
        ])

        order_quantity = 0
        stock = 0
        delay_time_days = 0

        for schedule_production_obj in schedule_production_objs:
            
            if schedule_production_obj.order_number.is_finish not in ['已完成', '退单'] and schedule_production_obj.date_contract < current_date:

                order_quantity += schedule_production_obj.quantity_order
                stock += schedule_production_obj.qualified_stock
                delay_time_days += (current_date - schedule_production_obj.date_contract).days

        quality_control_output_value_overdue_line_obj = self.env['quality_control_output_value_overdue_line'].sudo().search([
            ("quality_control_output_value_id", "=", quality_control_output_value_obj.id),
            ("date", "=", current_date),
        ])

        if not quality_control_output_value_overdue_line_obj:
            quality_control_output_value_overdue_line_obj = self.env['quality_control_output_value_overdue_line'].sudo().create({
                "quality_control_output_value_id": quality_control_output_value_obj.id,
                "date": current_date,
            })
        quality_control_output_value_overdue_line_obj.delay_time_days = delay_time_days     # 逾期天数
        quality_control_output_value_overdue_line_obj.order_quantity = order_quantity   # 订单数
        quality_control_output_value_overdue_line_obj.stock = stock      # 存量





    # 刷新目标产值
    def refresh_quality_control_output_value(self) -> None:
        ''' 刷新品控产值'''

        current_date = fields.Date.today()
        
        if current_date.month < 10:
            year_month = f"{current_date.year}-0{current_date.month}"
        else:
            year_month = f"{current_date.year}-{current_date.month}"

        this_month_start, this_month_end = self.set_begin_and_end(current_date.year, current_date.month)

        quality_control_output_value_list = self.detect_and_generate_record(year_month)

        for quality_control_output_value_obj in quality_control_output_value_list:

            if quality_control_output_value_obj.employee_id:
                start_date, end_date =  self.current_month_in_service_days(quality_control_output_value_obj, this_month_start, this_month_end)
                quality_control_output_value_obj.entry_time = quality_control_output_value_obj.employee_id.entry_time
                quality_control_output_value_obj.is_delete_date = quality_control_output_value_obj.employee_id.is_delete_date
            else:
                start_date, end_date =  this_month_start, this_month_end

            self.refresh_actual_finished_output_value(start_date, end_date, quality_control_output_value_obj)

            invest_objs = self.env['invest.invest'].search([("date", ">=", start_date),("date", "<=", end_date)])
            quality_control_output_value_obj.group_repair_number = sum(invest_objs.mapped("repairs_number"))

            posterior_passage_statistical_objs = self.env['posterior_passage_statistical'].search([("dDate", ">=", start_date),("dDate", "<=", end_date)])
            quality_control_output_value_obj.following_repair_number = sum(posterior_passage_statistical_objs.mapped("dg_rework_number"))

            client_ware_objs = self.env['client_ware'].search([("dDate", ">=", start_date),("dDate", "<=", end_date)])
            quality_control_output_value_obj.client_warehouse_repair_number = sum(client_ware_objs.mapped("repair_number"))

            self.refresh_delay_time_info(start_date, end_date, quality_control_output_value_obj, current_date)






class QualityControlOutputValueOverdueLine(models.Model):
    _name = 'quality_control_output_value_overdue_line'
    _description = '品控产值（品控主管）逾期明细'


    quality_control_output_value_id = fields.Many2one("quality_control_output_value", string="品控产值（品控主管）", ondelete="cascade")
    date = fields.Date(string="日期")
    delay_time_days = fields.Integer(string="逾期天数")
    order_quantity = fields.Integer(string="订单数")
    stock = fields.Integer(string="存量")