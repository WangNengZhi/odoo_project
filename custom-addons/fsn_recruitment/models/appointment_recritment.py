
from odoo import models, fields, api


class appointment_recritment(models.Model):
    _name = 'appointment.recritment'
    _description = '招聘数据'
    _order = 'date desc'

    date = fields.Date('日期')
    name = fields.Char('姓名')
    phone = fields.Char('联系方式')
    apply_to_position = fields.Char('应聘岗位')
    recruitment_location = fields.Char('招聘地点')
    interview_time = fields.Date('面试时间')
    interviewer = fields.Many2one('hr.employee', string="面试官")
    eligibility = fields.Char('是否合格')
    entry_time = fields.Date('入职时间', compute="set_entry_time", store=True)
    resignation_time = fields.Date('离职时间', compute="set_entry_time", store=True)
    recruiter = fields.Char('招聘员')
    # recruiter_id = fields.Many2one('hr.employee', string="招聘员")
    candidate_number = fields.Integer(string="面试人数")
    comment = fields.Char('备注')


    hr_employee_id = fields.Many2one("hr.employee", string="员工", compute="set_hr_employee_id", store=True)

    @api.depends('hr_employee_id', 'hr_employee_id.introducer', 'hr_employee_id.entry_time', 'hr_employee_id.is_delete_date')
    def set_entry_time(self):
        for record in self:
            if record.hr_employee_id:
                record.entry_time = record.hr_employee_id.entry_time
                record.resignation_time = record.hr_employee_id.is_delete_date


    @api.depends('name', 'phone', 'recruiter')
    def set_hr_employee_id(self):
        for record in self:

            if record.recruiter:
                introducer_obj = self.hr_employee_id.sudo().search([("name", "=", record.recruiter)])

                hr_employee_obj = self.hr_employee_id.sudo().search([
                    "|", ("name", "=", record.name), ("mobile_phone", "=", record.phone), ("introducer", "=", introducer_obj.id)
                    ])
                
                if hr_employee_obj:
                    record.hr_employee_id = hr_employee_obj.id

