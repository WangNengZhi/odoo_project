from odoo import models, fields, api


class FsnTemplateRecord(models.Model):
    _name = 'fsn_template_record'
    _description = '模板记录'
    _rec_name = 'style_number_id'
    _order = 'date desc'

    date = fields.Date(string="日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    work_type = fields.Char(string="工种", compute="set_employee_info", store=True)
    departure_date = fields.Date(string="离职日期")
    job_id = fields.Many2one("hr.job", string="岗位", compute="set_employee_info", store=True)

    style_number_id = fields.Many2one('ib.detail', string='款号', required=True)
    version_sample_image = fields.Image(string="模板图片")
    attachment_ids = fields.Many2many('ir.attachment', string="附件")

    job_content = fields.Text(string="工作内容")
    plan_production = fields.Float(string="计划产量")
    actual_production = fields.Float(string="实际产量")

    IE_working_hours = fields.Float(string='IE工时(秒)', digits=(16, 5))


    # 设置员工信息
    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            
            record.work_type = record.employee_id.is_it_a_temporary_worker
            record.job_id = record.employee_id.job_id.id

