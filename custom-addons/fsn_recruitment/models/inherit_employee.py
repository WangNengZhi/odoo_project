
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritEmployee(models.Model):
    _inherit = "hr.employee"


    @api.model
    def create(self, vals):

        instance = super(InheritEmployee, self).create(vals)

        if instance.introducer:

            appointment_recritment_obj = self.env["appointment.recritment"].sudo().search([
                "|", ("name", "=", instance.name), ("phone", "=", instance.mobile_phone), ("recruiter", "=", instance.introducer.name)
                ])
            
            if appointment_recritment_obj:
                appointment_recritment_obj.hr_employee_id = instance.id

        return instance
