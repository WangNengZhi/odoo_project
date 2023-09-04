from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar, datetime

class RepairClockIn(models.Model):
    _name = 'repair_clock_in'
    _description = '补卡申请单'
    _order = "repair_clock_date desc"
    # _rec_name = 'employee_id'



    repair_clock_date = fields.Date(string="补卡申请时间", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    department_id = fields.Many2one("hr.department", string="部门", compute="set_department_id", store=True)
    approver_signature = fields.Many2one('hr.employee', string='审批人')
    repair_clock_in_line_ids = fields.One2many("repair_clock_in_line", "repair_clock_in_id", string="补卡申请单明细")
    reason = fields.Char(string="补卡原因")



    # 设置部门
    @api.depends('employee_id', 'employee_id.department_id')
    def set_department_id(self):
        for record in self:
            record.department_id = record.employee_id.department_id.id




    # 计算月的第一天和最后一天
    def compute_start_and_end(self, today):

        if today:
            # 获取当前月份的第一天和最后一天
            date_list = str(today).split("-")
            date_year = int(date_list[0])
            date_month = int(date_list[1])
            last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
            start = datetime.date(date_year, date_month, 1)
            end = datetime.date(date_year, date_month, last_day)

            return {"start": start, "end": end}


    # 入职自动补卡
    def induction_fill_card(self, today):

        date_dict = self.compute_start_and_end(today)

        hr_employee_objs = self.env["hr.employee"].sudo().search([
            ("entry_time", ">=", date_dict["start"]),
            ("entry_time", "<=", date_dict["end"])
        ])
        

        for hr_employee_obj in hr_employee_objs:

            # 查询是否有入职日期的补卡记录
            repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().search([
                ("employee_id", "=", hr_employee_obj.id),
                ("line_date", "=", hr_employee_obj.entry_time)
            ])

            if repair_clock_in_line_obj:
                pass
            else:
                repair_clock_in_obj = self.env["repair_clock_in"].sudo().create({
                    "repair_clock_date": hr_employee_obj.entry_time,
                    "employee_id": hr_employee_obj.id,
                    "reason": "入职第一天补卡！（自动生成）",
                })
                repair_clock_in_line_obj = self.env["repair_clock_in_line"].sudo().create({
                    "line_date": hr_employee_obj.entry_time,
                    # "employee_id": hr_employee_obj.id,
                    "repair_clock_type": "上班卡",
                    "type": "正常补卡",
                    "reason": "入职第一天补卡！（自动生成）",
                    "repair_clock_in_id": repair_clock_in_obj.id,
                })




class RepairClockInLine(models.Model):
    _name = 'repair_clock_in_line'
    _description = '补卡申请单明细'

    repair_clock_in_id = fields.Many2one("repair_clock_in", string="补卡申请单id", ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', string='员工', store=True, compute="set_employee_id")
    line_date  = fields.Date(string="补卡日期", required=True)
    repair_clock_type = fields.Selection([
        ('上班卡', '上班卡'),
        ('下班卡', '下班卡')
    ], string='上班卡/下班卡', required=True)
    type = fields.Selection([
        ('正常补卡', '正常补卡'),
        ('异常补卡', '异常补卡 ')
    ], string="补卡类型", required=True)
    reason = fields.Char(string="补卡原因")


    # 设置员工
    @api.depends('repair_clock_in_id')
    def set_employee_id(self):
        for record in self:
            record.employee_id = record.repair_clock_in_id.employee_id.id
