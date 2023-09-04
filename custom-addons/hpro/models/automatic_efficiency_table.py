from odoo import models, fields, api
from odoo.exceptions import ValidationError

import datetime
import calendar


def get_last_month_date_range(year, month):
    ''' 获取上个月份的开始和结束日期'''

    month -= 1
    if month == 0:
        year, month = year - 1, 12
    
    start_date = datetime.datetime(year, month, 1).date()
    end_date = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

    return start_date, end_date


class AutomaticEfficiencyTable(models.Model):
    _name = 'automatic_efficiency_table'
    _description = '自动效率表'
    _rec_name = 'employee_id'
    _order = "date desc"

    date = fields.Date(string='日期')
    employee_id = fields.Many2one("hr.employee", string="员工id")
    work_type = fields.Char(string="工种", compute="set_employee_info", store=True)
    departure_date = fields.Date(string="离职日期", related='employee_id.is_delete_date', store=True)
    job_id = fields.Many2one("hr.job", string="岗位", compute="set_employee_info", store=True)
    # group = fields.Char(string="组别")
    group = fields.Many2one('check_position_settings', string='组别')
    efficiency = fields.Float(string="效率", compute="set_efficiency", store=True, group_operator='avg')
    last_month_avg_efficiency = fields.Float(string="上月平均效率", group_operator='avg', compute="set_last_month_avg_efficiency", store=True)
    @api.depends("date", "employee_id")
    def set_last_month_avg_efficiency(self):
        for record in self:
            last_month_start_date, last_month_end_date = get_last_month_date_range(record.date.year, record.date.month)

            automatic_efficiency_table_objs = self.env['automatic_efficiency_table'].sudo().search([
                ("date", ">=", last_month_start_date),
                ("date", "<=", last_month_end_date),
                ("employee_id", "=", record.employee_id.id)
            ])

            if automatic_efficiency_table_objs:
                record.last_month_avg_efficiency = sum(i.efficiency for i in automatic_efficiency_table_objs) / len(automatic_efficiency_table_objs)
            else:
                record.last_month_avg_efficiency = 0


    scene_process_ids = fields.One2many("automatic_scene_process", "efficiency_table_id", string="现场工序明细")



    # 计算效率
    @api.depends('scene_process_ids', 'scene_process_ids.process_time', 'scene_process_ids.number')
    def set_efficiency(self):
        for record in self:

            record.efficiency = sum(((line.process_time * line.number) / 396) for line in record.scene_process_ids)



    # 设置员工信息
    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            record.work_type = record.employee_id.is_it_a_temporary_worker
            record.job_id = record.employee_id.job_id.id
            # record.departure_date = record.employee_id.is_delete_date



class AutomaticSceneProcess(models.Model):
    _inherit = "automatic_scene_process"


    efficiency_table_id = fields.Many2one("automatic_efficiency_table", string="效率表")



    # 设置效率表
    def set_automatic_efficiency_table(self):

        automatic_efficiency_table_obj = self.env["automatic_efficiency_table"].sudo().search([
            ("date", "=", self.date),
            ("employee_id", "=", self.employee_id.id)
        ])

        if automatic_efficiency_table_obj:
            self.efficiency_table_id = automatic_efficiency_table_obj.id
        else:
            new_obj = automatic_efficiency_table_obj.sudo().create({
                "date": self.date,
                "employee_id": self.employee_id.id,
                "group": self.group.id,
            })
            self.efficiency_table_id = new_obj.id


    @api.model
    def create(self, vals):


        instance = super(AutomaticSceneProcess, self).create(vals)

        # 设置效率表
        instance.sudo().set_automatic_efficiency_table()

        return instance






