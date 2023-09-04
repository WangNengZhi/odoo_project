from odoo import api, fields, models
# from odoo.exceptions import ValidationError

class EcResultsManage(models.Model):
    _name = 'ec_results_manage'
    _description = '电商绩效管理'
    _rec_name = 'employee_id'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    job_id = fields.Many2one('hr.job', compute="set_employee_messages", store=True, string='岗位')
    # 设置当前薪资
    @api.depends('employee_id')
    def set_employee_messages(self):
        for record in self:
            # 岗位
            record.job_id = record.employee_id.job_id.id
    task_id = fields.Many2one("ec_task", string="任务", required=True)
    unit = fields.Char(string="单位", required=True)
    number = fields.Float(string="数量")