from odoo import api, fields, models

import datetime
import calendar

class QualityControlDepOutputValue(models.Model):
    _name = 'quality_control_dep_output_value'
    _description = '品控部产值（中查、总检、尾查）'
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

    avg_workpiece_ratio = fields.Float(string="平均效率")

    check_quantity = fields.Integer(string="查货数量")
    repair_quantity = fields.Integer(string="返修数量")
    repair_rate = fields.Float(string="返修率", compute="set_repair_rate", store=True)
    @api.depends("check_quantity", "repair_quantity")
    def set_repair_rate(self):
        for record in self:
            if record.check_quantity:
                record.repair_rate = record.repair_quantity / record.check_quantity
            else:
                record.repair_rate = 0

    missing_quantity = fields.Integer(string="漏查数量")
    missing_rate = fields.Float(string="漏查率", compute="set_missing_rate", store=True)
    @api.depends("check_quantity", "missing_quantity")
    def set_missing_rate(self):
        for record in self:
            if record.check_quantity:
                record.missing_rate = record.missing_quantity / record.check_quantity
            else:
                record.missing_rate = 0


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

        quality_control_dep_output_value_list = list(self.env['quality_control_dep_output_value'].sudo().search([("year_month", "=", year_month)]))

        emp_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("job_id.name", "in", ["总检", "巡检", "中查"])])
        for emp_obj in emp_objs:
            if not self.env['quality_control_dep_output_value'].sudo().search([("year_month", "=", year_month), ("employee_id", "=", emp_obj.id)]):
                quality_control_dep_output_value_list.append(self.env['quality_control_dep_output_value'].sudo().create({
                    "year_month": year_month,
                    "employee_id": emp_obj.id,
                    "entry_time": emp_obj.entry_time,
                }))

        return quality_control_dep_output_value_list


    def refresh_avg_workpiece_ratio(self, start_date, end_date) -> None:
        ''' 刷新平均效率'''

        automatic_efficiency_table_objs = self.env['automatic_efficiency_table'].sudo().search([
            ("employee_id", "=", self.employee_id.id),
            ("date", ">=", start_date),
            ("date", "<=", end_date)
        ])

        if automatic_efficiency_table_objs:
            self.avg_workpiece_ratio = sum(automatic_efficiency_table_objs.mapped("efficiency")) / len(automatic_efficiency_table_objs) / 100
        else:
            self.avg_workpiece_ratio = 0


    def refresh_check_quantity(self, start_date, end_date) -> None:
        ''' 刷新查货数量'''

        if self.job_id.name == "中查":

            invest_objs = self.env['invest.invest'].sudo().search([("invest", "=", self.employee_id.name), ("date", ">=", start_date), ("date", "<=", end_date)])
            self.check_quantity = sum(invest_objs.mapped("check_the_quantity"))
            self.repair_quantity = sum(invest_objs.mapped("repairs_number"))
            general_objs = self.env['general.general'].sudo().search([("invest", "=", self.employee_id.name), ("date", ">=", start_date), ("date", "<=", end_date)])

            self.missing_quantity = sum(general_objs.mapped("repair_number"))
        elif self.job_id.name == "总检":
            general_objs = self.env['general.general'].sudo().search([("general1", "=", self.employee_id.name), ("date", ">=", start_date), ("date", "<=", end_date)])
            self.repair_quantity = sum(general_objs.mapped("repair_number"))
            self.check_quantity = sum(general_objs.mapped("general_number"))
            client_ware_objs = self.env['client_ware'].sudo().search([
                ("general", "=", self.employee_id.name),
                ("check_type", "=", "尾查"),
                ("dDate", ">=", start_date), ("dDate", "<=", end_date)
            ])
            self.missing_quantity = sum(client_ware_objs.mapped("repair_number"))
        elif self.job_id.name == "巡检":
            client_ware_objs = self.env['client_ware'].sudo().search([
                ("client_or_QC", "=", self.employee_id.name),
                ("check_type", "=", "尾查"),
                ("dDate", ">=", start_date), ("dDate", "<=", end_date)
            ])
            self.repair_quantity = sum(client_ware_objs.mapped("repair_number"))
            self.check_quantity = sum(client_ware_objs.mapped("check_number"))
            # client_ware_objs = self.env['client_ware'].sudo().search([
            #     ("general", "=", self.employee_id.name),
            #     ("check_type", "=", "客户"),
            #     ("dDate", ">=", start_date), ("dDate", "<=", end_date)
            # ])

    def refresh_quality_control_dep_output_value(self) -> None:
        ''' 刷新品控部产值（中查、总检、尾查）'''

        current_date = fields.Date.today()
        
        year, month, _ = str(current_date).split("-")
        year_month = f"{year}-{month}"

        this_month_start, this_month_end = self.set_begin_and_end(current_date.year, current_date.month)

        quality_control_dep_output_value_list = self.detect_and_generate_record(year_month)

        for quality_control_output_value_obj in quality_control_dep_output_value_list:

            start_date, end_date =  self.current_month_in_service_days(quality_control_output_value_obj, this_month_start, this_month_end)
            quality_control_output_value_obj.is_delete_date = quality_control_output_value_obj.employee_id.is_delete_date

            quality_control_output_value_obj.refresh_avg_workpiece_ratio(start_date, end_date)

            quality_control_output_value_obj.refresh_check_quantity(start_date, end_date)



