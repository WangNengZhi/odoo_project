
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class HrEmployeeSocialSecurityWizard(models.TransientModel):
    _name = 'hr_employee_social_security_wizard'
    _description = '手动设置开始缴纳社保月份向导'


    start_paying_social_security_month = fields.Char(string="开始缴纳社保月份", required=True)

    def manual_set_start_paying_social_security(self):
        ''' 用于打卡手动设置开始缴纳社保月份'''
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')
        for active_id in active_ids:
            emp_obj = self.env[active_model].sudo().browse(active_id)
            print(emp_obj.start_paying_social_security_month)
            emp_obj.start_paying_social_security_month = self.start_paying_social_security_month
            print(emp_obj.start_paying_social_security_month)


class HrEmployee(models.Model):
    _inherit = "hr.employee"


    fsn_department_id = fields.Many2one("hr.department", compute="set_fsn_department_id", store=False)
    @api.depends("department_id")
    def set_fsn_department_id(self):
        for record in self:
            record.fsn_department_id = record.department_id.id
    fsn_job_id = fields.Many2one("hr.job", string="岗位", compute="set_fsn_job_id", store=False)
    @api.depends("job_id")
    def set_fsn_job_id(self):
        for record in self:
            record.fsn_job_id = record.job_id.id
    
    social_security_state = fields.Selection([
        ('草稿', '草稿'),
        ('已审批', '已审批'),
    ], string='社保状态', default="草稿")


    start_paying_social_security_month = fields.Char(string="开始缴纳社保月份")
    @api.onchange("entry_time")
    def set_start_paying_social_security(self):
        for record in self:
            if record.entry_time:
                entry_year = record.entry_time.year
                entry_month = record.entry_time.month

                temp_date = datetime.datetime(entry_year, entry_month, 15).date()

                year, month, _ = map(int, (str(record.entry_time).split('-')))

                if record.entry_time < temp_date:
                    
                    if month == 12:
                        year += 1
                        month = 1
                    else:
                        month += 1
                else:
                    if month == 12:
                        year += 1
                        month = 2
                    else:
                        month += 2

                month = '%02d' % month

                record.start_paying_social_security_month = f"{year}-{month}"


    def manual_set_start_paying_social_security_action(self):
        ''' 用于打卡手动设置开始缴纳社保月份的动作'''

        action = {
            'name': "手动设置开始缴纳社保月份",
            'view_mode': 'form',
            'res_model': 'hr_employee_social_security_wizard',
            'view_id': self.env.ref('fsn_employee.hr_employee_social_security_wizard_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

        return action




    # 员工社保审批
    def employee_social_security_examine_and_approve(self):

        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"

        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'hr.employee',
            'view_id': self.env.ref('fsn_employee.hr_employee_social_security_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def social_security_action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.social_security_state = "草稿"
        elif button_type == "through":
            self.social_security_state = "已审批"


    # def write(self, vals):

    #     if "is_social_security" in vals and self.social_security_state == "已审批":
    #         raise ValidationError(f"社保状态已经审批不可修改!")

    #     res = super(HrEmployee, self).write(vals)

    #     return res




