from odoo import api, fields, models


import datetime
import calendar


class TechnologyOutputValue(models.Model):
    _name = 'technology_output_value'
    _description = '技术科产值（技术科主管）'
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

    sample_clothes_plan_number = fields.Integer(string="样衣计划件数")
    sample_clothes_complete_number = fields.Integer(string="样衣完成件数")
    sample_clothes_per_capita_complete_number = fields.Float(string="样衣人均完成件数")

    template_plan_number = fields.Integer(string="模板计划件数")
    template_complete_number = fields.Integer(string="模板完成件数")
    template_per_capita_complete_number = fields.Float(string="模板人均完成件数")


    def set_begin_and_end(self, year:int, month:int) -> tuple:
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end


    def current_month_in_service_days(self, employee_id: object, this_month_start: datetime, this_month_end: datetime) -> tuple:
        ''' 计算当月在职日期范围'''

        if employee_id.entry_time < this_month_start:

            if not employee_id.is_delete or employee_id.is_delete_date > this_month_end:
                return this_month_start, this_month_end
            else:
                return this_month_start, employee_id.is_delete_date
        else:
            if not employee_id.is_delete or employee_id.is_delete_date > this_month_end:
                return employee_id.entry_time, this_month_end
            else:
                return employee_id.entry_time, employee_id.is_delete_date


    def generate_technology_output_value_record(self, year_month: str) -> list:
        ''' 生成刷新技术科产值记录'''
        technology_output_value_list = list(self.env['technology_output_value'].sudo().search([("year_month", "=", year_month)]))

        staff_number = self.env["hr.employee"].sudo().search_count([("is_delete", "=", False), '|', ("department_id.name", "=", "技术部"), ('department_id.parent_id.name', "=", "技术部")])

        group_leader_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("department_id.name", "=", "技术部"), ("job_id.name", "=", "技术部主管")], order='entry_time')

    
        if group_leader_objs:
            if not self.env['technology_output_value'].sudo().search([("year_month", "=", year_month), ("employee_id", "=", group_leader_objs[0].id)]):
                technology_output_value_list.append(self.env['technology_output_value'].sudo().create({
                    "year_month": year_month,
                    "number": staff_number,
                    "employee_id": group_leader_objs[0].id,
                }))
        else:
            if not self.env['technology_output_value'].sudo().search([("year_month", "=", year_month)]):
                technology_output_value_list.append(self.env['technology_output_value'].sudo().create({
                    "year_month": year_month,
                    "number": staff_number,
                }))

        return technology_output_value_list


    def calculation_sample_clothes_info(self, technology_output_value_obj: object, this_month_start: datetime, this_month_end: datetime) -> None:
        ''' 计算样衣信息'''

        th_per_management_objs = self.env['th_per_management'].sudo().search([("date", ">=", this_month_start), ("date", "<=", this_month_end)])

        technology_output_value_obj.sample_clothes_complete_number = len(th_per_management_objs)

        technology_output_value_obj.sample_clothes_per_capita_complete_number = len(th_per_management_objs) / technology_output_value_obj.number


    def calculation_template_info(self, technology_output_value_obj: object, this_month_start: datetime, this_month_end: datetime) -> None:
        ''' 计算模板信息'''

        fsn_platemaking_record_objs = self.env['fsn_platemaking_record'].sudo().search([("date", ">=", this_month_start), ("date", "<=", this_month_end)])

        technology_output_value_obj.template_complete_number = len(fsn_platemaking_record_objs)

        technology_output_value_obj.template_per_capita_complete_number = len(fsn_platemaking_record_objs) / technology_output_value_obj.number


    def refresh_technology_output_value(self) -> None:
        ''' 刷新技术科产值'''

        current_date = fields.Date.today()
        
        this_month_start, this_month_end = self.set_begin_and_end(current_date.year, current_date.month)
        year, month, _ = str(current_date).split("-")
        year_month = f"{year}-{month}"


        technology_output_value_list = self.generate_technology_output_value_record(year_month)

        for technology_output_value_obj in technology_output_value_list:

            if technology_output_value_obj.employee_id:
                this_month_start_, this_month_end_ =  self.current_month_in_service_days(technology_output_value_obj.employee_id, this_month_start, this_month_end)
                technology_output_value_obj.entry_time = technology_output_value_obj.employee_id.entry_time
                technology_output_value_obj.is_delete_date = technology_output_value_obj.employee_id.is_delete_date
            
            else:
                this_month_start_, this_month_end_ = this_month_start, this_month_end

            self.calculation_sample_clothes_info(technology_output_value_obj, this_month_start_, this_month_end_)

            self.calculation_template_info(technology_output_value_obj, this_month_start_, this_month_end_)


