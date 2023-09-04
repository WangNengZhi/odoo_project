from odoo import api, fields, models


import datetime
import calendar


class TargetOutputValuTop(models.Model):
    _name = 'target_output_value_top'
    _description = '目标产值（高层管理）'
    _rec_name = 'employee_id'

    target_output_value_ids = fields.Many2many("target_output_value", string="目标产值（中层管理）")
    year_month = fields.Char(string="月份")
    number = fields.Integer(string="人数")
    plann_output_value = fields.Float(string="计划产值", compute="set_plann_output_value", store=True)
    @api.depends('target_output_value_ids', 'target_output_value_ids.plann_output_value')
    def set_plann_output_value(self):
        for record in self:
            
            record.plann_output_value = sum(i.plann_output_value for i in record.target_output_value_ids if self.env["fsn_staff_team"].search([("department_id", "=", i.department_id.id)]).type == "车间")


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



    employee_id = fields.Many2one('hr.employee', string='负责人')
    entry_time = fields.Date(string='入职日期')
    is_delete_date = fields.Date(string='离职日期')
    job_id = fields.Many2one('hr.job', string='岗位', compute="set_employee_info", store=True)

    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            record.job_id = record.employee_id.job_id.id

    target_output_value_top_line_ids = fields.One2many("target_output_value_top_line", "target_output_value_top_id", string="目标产值（高层管理）逾期明细")
    delay_time_days = fields.Integer(string="误期天数", compute="set_delay_time_info", store=True)
    delay_time_quantity = fields.Integer(string="误期件数", compute="set_delay_time_info", store=True)
    @api.depends('target_output_value_top_line_ids', 'target_output_value_top_line_ids.order_quantity', 'target_output_value_top_line_ids.stock')
    def set_delay_time_info(self):
        for record in self:
            if record.target_output_value_top_line_ids:
                obj = max(record.target_output_value_top_line_ids, key=lambda x: x.date)
                record.delay_time_days = obj.delay_time_days
                record.delay_time_quantity = obj.order_quantity - obj.stock
            else:
                record.delay_time_days = 0
                record.delay_time_quantity = 0


    loss_quantity = fields.Integer(string="损耗件数")



    # 获取当月第一天和最后一天
    def set_begin_and_end(self, year, month):

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end


    # 计算当月在职日期范围
    def current_month_in_service_days(self, this_month_start, this_month_end):

        if self.employee_id.entry_time < this_month_start:
            if not self.employee_id.is_delete or self.employee_id.is_delete_date > this_month_end:
                return this_month_start, this_month_end
            else:
                return this_month_start, self.employee_id.is_delete_date
        else:
            if not self.employee_id.is_delete or self.employee_id.is_delete_date > this_month_end:
                return self.employee_id.entry_time, this_month_end
            else:
                return self.employee_id.entry_time, self.employee_id.is_delete_date



    def refresh_delay_time_info(self, start_date, end_date, target_output_value_top_obj, current_date) -> None:
        '''刷新逾期信息'''

        schedule_production_objs = self.env['schedule_production'].sudo().search([
            ("state", "=", "未完成"),
            ("processing_type", "=", "工厂"),
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

        quality_control_output_value_overdue_line_obj = self.env['target_output_value_top_line'].sudo().search([
            ("target_output_value_top_id", "=", target_output_value_top_obj.id),
            ("date", "=", current_date),
        ])

        if not quality_control_output_value_overdue_line_obj:
            quality_control_output_value_overdue_line_obj = self.env['target_output_value_top_line'].sudo().create({
                "target_output_value_top_id": target_output_value_top_obj.id,
                "date": current_date,
            })
        quality_control_output_value_overdue_line_obj.delay_time_days = delay_time_days     # 逾期天数
        quality_control_output_value_overdue_line_obj.order_quantity = order_quantity   # 订单数
        quality_control_output_value_overdue_line_obj.stock = stock      # 存量

    

    def refresh_loss_quantity(self, start_date, end_date, send_out_output_value_obj, current_date):
        ''' 刷新损耗'''

        loss_quantity = 0

        schedule_production_objs = self.env['schedule_production'].sudo().search([("date_contract", ">=", start_date),("date_contract", "<=", end_date),("processing_type", "=", "工厂")])
        print(schedule_production_objs)
        for schedule_production_obj in schedule_production_objs:

            if schedule_production_obj.order_number.is_finish != "退单" and schedule_production_obj.date_contract < current_date:
                
                loss_quantity += (schedule_production_obj.factory_delivery_variance + schedule_production_obj.defective_number)

        send_out_output_value_obj.loss_quantity = loss_quantity



    # 厂长刷新
    def factory_director_record_refresh(self, this_month_start, this_month_end):
        ''' 厂长各项信息刷新'''

        start_date, end_date =  self.current_month_in_service_days(this_month_start, this_month_end)

        pro_pro_objs = self.env['pro.pro'].search([("date", ">=", start_date),("date", "<=", end_date)])

        self.actual_finished_output_value = sum(pro_pro_objs.mapped("pro_value"))
        self.actual_finished_number = sum(pro_pro_objs.mapped("number"))

        invest_objs = self.env['invest.invest'].search([("date", ">=", start_date),("date", "<=", end_date)])
        self.group_repair_number = sum(invest_objs.mapped("repairs_number"))

        posterior_passage_statistical_objs = self.env['posterior_passage_statistical'].search([("dDate", ">=", start_date),("dDate", "<=", end_date)])
        self.following_repair_number = sum(posterior_passage_statistical_objs.mapped("dg_rework_number"))

        client_ware_objs = self.env['client_ware'].search([("dDate", ">=", start_date),("dDate", "<=", end_date)])
        self.client_warehouse_repair_number = sum(client_ware_objs.mapped("repair_number"))

        current_date = fields.Date.today()
        self.refresh_delay_time_info(start_date, end_date, self, current_date)

        self.refresh_loss_quantity(start_date, end_date, self, current_date)




    # 厂长生成
    def factory_director_record_generation(self, year_month, this_month_start, this_month_end):
        ''' 高层管理 厂长记录生成'''
        
        hr_employee_objs = self.env['hr.employee'].search([
            ("entry_time", "<=", this_month_end),
            "|", ("is_delete", "=", False),
            ("is_delete_date", ">=", this_month_start),
            ("job_id.name", "in", ["厂长", "生产总监"])
        ])
        
        for employee_obj in hr_employee_objs:

            target_output_value_top_obj = self.env['target_output_value_top'].search([("employee_id", "=", employee_obj.id), ("year_month", "=", year_month)])

            if not target_output_value_top_obj:

                employee_count = self.env["hr.employee"].search_count([("is_delete", "=", False), ("department_id.name", "like", "缝纫")])
                target_output_value_top_obj = self.create({"year_month": year_month, "employee_id": employee_obj.id, "number": employee_count})

            target_output_value_top_obj.factory_director_record_refresh(this_month_start, this_month_end)
    
            target_output_value_top_obj.entry_time = target_output_value_top_obj.employee_id.entry_time
            target_output_value_top_obj.is_delete_date = target_output_value_top_obj.employee_id.is_delete_date







    # 刷新目标产值（高层管理）
    def refresh_target_output_value_top(self, today):
        # print(today)2022-10-10 00:00:00
        this_month_start, this_month_end = self.set_begin_and_end(today.year, today.month)
        year, month, _ = str(today).split("-")

        self.factory_director_record_generation(f"{year}-{month}", this_month_start, this_month_end)



class TargetOutputValuTopLine(models.Model):
    _name = 'target_output_value_top_line'
    _description = '目标产值（高层管理）逾期明细'


    target_output_value_top_id = fields.Many2one("target_output_value_top", string="目标产值（高层管理）", ondelete="cascade")
    date = fields.Date(string="日期")
    delay_time_days = fields.Integer(string="逾期天数")
    order_quantity = fields.Integer(string="订单数")
    stock = fields.Integer(string="存量")
