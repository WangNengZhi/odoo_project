from odoo import api, fields, models

import datetime
import calendar

import itertools

from typing import List


class TargetOutputValue(models.Model):
    _name = 'target_output_value'
    _description = '目标产值（中层管理）'


    year_month = fields.Char(string="月份")
    number = fields.Integer(string="人数")
    group_avg_workpiece_ratio = fields.Float(string="平均效率")
    department_id = fields.Many2one("hr.department", string="部门")
    group_id = fields.Many2one("fsn_staff_team", string="员工小组")
    plann_output_value = fields.Float(string="计划产值")
    actual_finished_number = fields.Integer(string="实际完成件数")
    personnel_turnover = fields.Integer(string="人员流失", compute="_compute_personnel_turnover", store=True)

    @api.depends('department_id.member_ids.is_delete')
    def _compute_personnel_turnover(self):
        for record in self:
            if record.department_id:
                employees = record.department_id.member_ids.filtered(
                    lambda emp: emp.is_delete and emp.is_delete_date.strftime('%Y-%m').startswith(record.year_month)
                )
                record.personnel_turnover = len(employees)
            else:
                record.personnel_turnover = 0

    actual_finished_output_value = fields.Float(string="实际完成产值")
    progress = fields.Float(string="进度", compute="set_progress", store=True)
    @api.depends('plann_output_value', 'actual_finished_output_value')
    def set_progress(self):
        for record in self:
            if record.plann_output_value:
                record.progress = (record.actual_finished_output_value / record.plann_output_value) * 100
            else:
                record.progress = 0

    piecework_value = fields.Float(string="计件产值")


    dg_abnormal_count = fields.Integer(string="吊挂异常计数")
    blocking_scheme = fields.Float(string="阻塞率", compute="set_blocking_scheme", store=True)
    @api.depends("dg_abnormal_count", "number", "actual_finished_number")
    def set_blocking_scheme(slef):
        for record in slef:
            if record.number and record.actual_finished_number:
                record.blocking_scheme = (record.dg_abnormal_count / record.number / record.actual_finished_number) * 10
            else:
                record.blocking_scheme = 0


    employee_id = fields.Many2one('hr.employee', string='负责人')
    entry_time = fields.Date(string='入职日期')
    is_delete_date = fields.Date(string='离职日期')


    group_repair_number = fields.Integer(string="组返修件数")
    group_repair_number_ratio = fields.Float(string="组返修率", compute="set_ratio", store=True)

    following_repair_number = fields.Integer(string="后道退回件数")
    following_repair_number_ratio = fields.Float(string="后道退回率", compute="set_ratio", store=True)

    client_warehouse_repair_number = fields.Integer(string="客仓返修件数")
    client_warehouse_repair_number_ratio = fields.Float(string="客仓返修率", compute="set_ratio", store=True)

    @api.depends('actual_finished_number', 'group_repair_number', 'following_repair_number', 'client_warehouse_repair_number')
    def set_ratio(self):
        for record in self:
            if record.actual_finished_number:
                record.group_repair_number_ratio = record.group_repair_number / record.actual_finished_number
                record.following_repair_number_ratio = record.following_repair_number / record.actual_finished_number
                record.client_warehouse_repair_number_ratio = record.client_warehouse_repair_number / record.actual_finished_number
            else:
                record.group_repair_number_ratio = 0
                record.following_repair_number_ratio = 0
                record.client_warehouse_repair_number_ratio = 0



    fsn_month_plan_ids = fields.Many2many("fsn_month_plan", "target_output_value_id", string="月计划")
    small_order_number = fields.Integer(string="小单", compute="set_fsn_month_plan_info", store=True)
    medium_order_number = fields.Integer(string="中单", compute="set_fsn_month_plan_info", store=True)
    big_order_number = fields.Integer(string="大单", compute="set_fsn_month_plan_info", store=True)
    @api.depends('fsn_month_plan_ids', 'fsn_month_plan_ids.plan_number')
    def set_fsn_month_plan_info(self):

        for record in self:

            order_number_dict = {"small_order_number": [], "medium_order_number": [], "big_order_number": []}

            fsn_month_plan_list = list(record.fsn_month_plan_ids)

            fsn_month_plan_list.sort(key=lambda x: x.style_number.style_number_base_id, reverse=True)     # 按款号前缀排序

            for style_number_base, style_number_base_objs in itertools.groupby(fsn_month_plan_list, key=lambda x:x.style_number.style_number_base_id):     # 按款号前缀分组
                
                style_number_base_plan_number = sum(i.plan_number for i in style_number_base_objs)
                if style_number_base_plan_number < 200:
                    order_number_dict['small_order_number'].append(style_number_base_plan_number)
                elif style_number_base_plan_number > 800:
                    order_number_dict['big_order_number'].append(style_number_base_plan_number)
                else:
                    order_number_dict['medium_order_number'].append(style_number_base_plan_number)

            record.small_order_number = len(order_number_dict['small_order_number'])
            record.medium_order_number = len(order_number_dict['medium_order_number'])
            record.big_order_number = len(order_number_dict['big_order_number'])




    # 检测并生成记录
    def detect_and_generate_record(self, year_month: str) -> List:
        ''' 检测并生成记录'''

        target_output_value_list = list(self.env['target_output_value'].sudo().search([("year_month", "=", year_month)]))
        
        current_employees_list = list(self.env["hr.employee"].sudo().search([("is_delete", "=", False)], order="department_id"))
        emps = {}
        for emp in current_employees_list:
            if "缝纫" in emp.department_id.name or emp.department_id.name in ['后道部', '裁床部']:
                dept_id = emp.department_id.id
                if dept_id not in emps:
                    emps[dept_id] = []
                emps[dept_id].append(emp)


        for key in emps:

            department_name = self.env['hr.department'].browse(key).name

            if department_name == "裁床部":
                group_leader_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("department_id", "=", key), ("job_id.name", "=", "裁床主管")], order='entry_time')
            elif department_name == "后道部":
                group_leader_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("department_id", "=", key), ("job_id.name", "=", "后道主管")], order='entry_time')
            else:
                group_leader_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("department_id", "=", key), ("job_id.name", "=", "流水组长")], order='entry_time')

            if group_leader_objs:
                if not self.env['target_output_value'].sudo().search([("year_month", "=", year_month), ("department_id", "=", key), ("employee_id", "=", group_leader_objs[0].id)]):
                    target_output_value_list.append(self.env['target_output_value'].sudo().create({
                        "year_month": year_month,
                        "number": len(emps[key]),
                        "department_id": key,
                        "employee_id": group_leader_objs[0].id,
                    }))
            else:
                if not self.env['target_output_value'].sudo().search([("year_month", "=", year_month), ("department_id", "=", key)]):
                    target_output_value_list.append(self.env['target_output_value'].sudo().create({
                        "year_month": year_month,
                        "number": len(emps[key]),
                        "department_id": key,
                    }))

        return target_output_value_list
        
        
    # 获取当月第一天和最后一天
    def set_begin_and_end(self, year, month):

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()     # 当月最后一天

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


    # 刷新实际完成产值和件数
    def refresh_actual_finished_output_value(self, this_month_start, this_month_end, fsn_staff_team_obj) -> None:
        for record in self:

            if record.department_id.name == "裁床部":
                cutting_bed_objs = self.env['cutting_bed'].sudo().search([("date", ">=", this_month_start),("date", "<=", this_month_end)])
                record.actual_finished_output_value = sum(cutting_bed_objs.mapped("pro_value"))
                record.actual_finished_number = sum(cutting_bed_objs.mapped("number"))
            elif record.department_id.name == "后道部":
                posterior_passage_output_value_objs = self.env['posterior_passage_output_value'].sudo().search([("date", ">=", this_month_start),("date", "<=", this_month_end)])
                record.actual_finished_output_value = sum(posterior_passage_output_value_objs.mapped("pro_value"))
                record.actual_finished_number = sum(posterior_passage_output_value_objs.mapped("number"))
            else:
                pro_pro_objs = self.env['pro.pro'].sudo().search([("group", "=", fsn_staff_team_obj.name),("date", ">=", this_month_start),("date", "<=", this_month_end)])
                record.actual_finished_output_value = sum(pro_pro_objs.mapped("pro_value"))
                record.actual_finished_number = sum(pro_pro_objs.mapped("number"))
                

    # 刷新组返修件数
    def refresh_group_repair_number(self, this_month_start, this_month_end, fsn_staff_team_obj) -> None:
        for record in self:

            invest_objs = self.env['invest.invest'].sudo().search([("group", "=", fsn_staff_team_obj.name),("date", ">=", this_month_start),("date", "<=", this_month_end)])
            
            record.group_repair_number = sum(invest_objs.mapped("repairs_number"))


    # 刷新后道返修件数
    def refresh_following_repair_number(self, this_month_start, this_month_end, fsn_staff_team_obj) -> None:
        for record in self:

            posterior_passage_statistical_objs = self.env['posterior_passage_statistical'].sudo().search([("group", "=", fsn_staff_team_obj.name),("dDate", ">=", this_month_start),("dDate", "<=", this_month_end)])
            
            record.following_repair_number = sum(posterior_passage_statistical_objs.mapped("dg_rework_number"))


    # 刷新客仓返修件数
    def refresh_client_warehouse_repair_number(self, this_month_start, this_month_end, fsn_staff_team_obj) -> None:
        for record in self:

            client_ware_objs = self.env['client_ware'].sudo().search([("gGroup", "=", fsn_staff_team_obj.name),("dDate", ">=", this_month_start),("dDate", "<=", this_month_end)])
            
            record.client_warehouse_repair_number = sum(client_ware_objs.mapped("repair_number"))


    # 绑定月计划
    def refresh_binding_fsn_month_plan(self, this_month_start, this_month_end, year_month, fsn_staff_team_obj) -> None:
        ''' 绑定月计划'''
        for record in self:

            fsn_month_plan_objs = self.env['fsn_month_plan'].sudo().search([
                ("order_number_date", ">=", this_month_start),
                ("order_number_date", "<=", this_month_end),
                ("month", "=", year_month),
                ("fsn_staff_team_id", "=", fsn_staff_team_obj.id)
            ])

            record.fsn_month_plan_ids = [(6, 0, fsn_month_plan_objs.ids)]


    # 绑定目标产值（高层管理）
    def binding_target_output_value_top(self):
        for record in self:
            target_output_value_top_objs = self.env['target_output_value_top'].search([("year_month", "=", record.year_month)])
            for target_output_value_top_obj in target_output_value_top_objs:
                target_output_value_top_obj.target_output_value_ids =  [(4, record.id)]


    def set_group_avg_workpiece_ratio(self, this_month_start, this_month_end):
        ''' 设置平均效率'''
        for record in self:

            if record.department_id.name == "裁床部":

                eff_objs = self.env['eff.eff'].sudo().read_group(
                    domain=[("group", "=", "裁床"), ("date", ">=", this_month_start), ("date", "<=", this_month_end)],
                    fields=["totle_eff"],
                    groupby="date:month"
                )
                if eff_objs:
                    record.group_avg_workpiece_ratio = eff_objs[0]["totle_eff"] / 100
                else:
                    record.group_avg_workpiece_ratio = 0

            elif record.department_id.name == "后道部":
                
                job_ids_list = self.env['hr.job'].sudo().search([("name", "in", ["中查", "现场IE", "后道主管", "流水车位"])]).ids

                automatic_efficiency_table_objs = self.env['automatic_efficiency_table'].sudo().read_group(
                    domain=[("group.group", "=", "后整"), ("job_id", "not in", job_ids_list), ("date", ">=", this_month_start), ("date", "<=", this_month_end)],
                    fields=["efficiency"],
                    groupby="date:month"
                )
                if automatic_efficiency_table_objs:
                    record.group_avg_workpiece_ratio = automatic_efficiency_table_objs[0]["efficiency"] / 100
                else:
                    record.group_avg_workpiece_ratio = 0
            
            else:

                automatic_efficiency_table_objs = self.env['automatic_efficiency_table'].sudo().read_group(
                    domain=[("group.group", "=", f"车缝{record.department_id.name[-2:]}"), ("work_type", "!=", "正式工(B级管理)"), ("date", ">=", this_month_start), ("date", "<=", this_month_end)],
                    fields=["efficiency"],
                    groupby="date:month"
                )
                if automatic_efficiency_table_objs:
                    record.group_avg_workpiece_ratio = automatic_efficiency_table_objs[0]["efficiency"] / 100
                else:
                    record.group_avg_workpiece_ratio = 0



    def set_piecework_value(self, this_month_start, this_month_end):
        ''' 设置计件产值'''
        for record in self:

            if record.department_id.name == "后道部":
                
                dg_piece_rate_objs = self.env['dg_piece_rate'].sudo().search([("group_id.group", "=", "后整"), ("date", ">=", this_month_start), ("date", "<=", this_month_end)])

                record.piecework_value = sum(dg_piece_rate_objs.mapped("cost"))

            else:
                dg_piece_rate_objs = self.env['dg_piece_rate'].sudo().search([("group_id.group", "=", f"车缝{record.department_id.name[-2:]}"), ("date", ">=", this_month_start), ("date", "<=", this_month_end)])

                record.piecework_value = sum(dg_piece_rate_objs.mapped("cost"))


    def set_dg_abnormal_count(self, this_month_start, this_month_end):
        ''' 设置吊挂异常计数'''

        if self.department_id.name == "后道部":
            dg_abnormal_record_objs = self.env['dg_abnormal_record'].sudo().search([("group", "=", "后整"), ("create_date", ">=", this_month_start), ("create_date", "<=", this_month_end)])

            self.dg_abnormal_count = len(dg_abnormal_record_objs)
        else:

            dg_abnormal_record_objs = self.env['dg_abnormal_record'].sudo().search([("group", "=", f"车缝{self.department_id.name[-2:]}"), ("create_date", ">=", this_month_start), ("create_date", "<=", this_month_end)])

            self.dg_abnormal_count = len(dg_abnormal_record_objs)
            

    def refresh_plann_output_value(self, this_month_start_, this_month_end_, fsn_staff_team_obj):
        ''' 设置计划产值'''
        planning_slot_objs = self.env['planning.slot'].sudo().search([("dDate", ">=", this_month_start_), ("dDate", "<=", this_month_end_), ("department_id", "=", fsn_staff_team_obj.name)])
        self.plann_output_value = sum(planning_slot_objs.mapped("plan_output_value"))


    # 刷新目标产值
    def refresh_target_output_value(self, current_date=None) -> None:

        if not current_date:
            current_date = fields.Date.today()
        print(current_date)
        if current_date.month < 10:
            year_month = f"{current_date.year}-0{current_date.month}"
        else:
            year_month = f"{current_date.year}-{current_date.month}"

        this_month_start, this_month_end = self.set_begin_and_end(current_date.year, current_date.month)

        target_output_value_list = self.detect_and_generate_record(year_month)

        for target_output_value_obj in target_output_value_list:

            if target_output_value_obj.employee_id:

                target_output_value_obj.entry_time = target_output_value_obj.employee_id.entry_time
                target_output_value_obj.is_delete_date = target_output_value_obj.employee_id.is_delete_date

                this_month_start_, this_month_end_ =  target_output_value_obj.current_month_in_service_days(this_month_start, this_month_end)
            
            else:
                this_month_start_, this_month_end_ = this_month_start, this_month_end

            fsn_staff_team_obj = self.env['fsn_staff_team'].sudo().search([("department_id", "=", target_output_value_obj.department_id.id)])
            if fsn_staff_team_obj:

                target_output_value_obj.refresh_actual_finished_output_value(this_month_start_, this_month_end_, fsn_staff_team_obj)

                if target_output_value_obj.department_id.name in ["裁床部", "后道部"]:

                    target_output_value_obj.refresh_plann_output_value(this_month_start_, this_month_end_, fsn_staff_team_obj)
                
                else:
                    
                    target_output_value_obj.refresh_group_repair_number(this_month_start_, this_month_end_, fsn_staff_team_obj)

                    target_output_value_obj.refresh_following_repair_number(this_month_start_, this_month_end_, fsn_staff_team_obj)

                    target_output_value_obj.refresh_client_warehouse_repair_number(this_month_start_, this_month_end_, fsn_staff_team_obj)

                    target_output_value_obj.refresh_binding_fsn_month_plan(this_month_start_, this_month_end_, year_month, fsn_staff_team_obj)
                
                target_output_value_obj.binding_target_output_value_top()

                target_output_value_obj.set_group_avg_workpiece_ratio(this_month_start_, this_month_end_)

                if target_output_value_obj.department_id.parent_id.name == "车间" or target_output_value_obj.department_id.name == "后道部":

                    target_output_value_obj.set_piecework_value(this_month_start_, this_month_end_)

                    target_output_value_obj.set_dg_abnormal_count(this_month_start_, this_month_end_)


        return True


class DgAbnormalRecord(models.Model):
    _name = 'dg_abnormal_record'
    _description = '吊挂异常记录'



    name = fields.Char(string="员工姓名")
    group = fields.Char(string="组别")






