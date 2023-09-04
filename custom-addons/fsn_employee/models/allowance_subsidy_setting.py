from odoo.exceptions import ValidationError
from odoo import models, fields, api


class AllowanceSubsidySetting(models.Model):
    _name = 'allowance_subsidy_setting'
    _description = '津贴补助设置'
    _rec_name='job_id'



    department_id = fields.Many2one('hr.department', string='部门')
    job_id = fields.Many2one('hr.job', string='岗位', required=True)
    perfect_attendance_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="全勤奖类型", required=True)
    housing_allowances_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="房补类型", required=True)
    meal_allowances_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="饭补类型", required=True)


    # 检查数据唯一性
    @api.constrains('department_id', 'job_id')
    def _check_unique(self):

        obj_count = self.sudo().search_count([("job_id", "=", self.job_id.id)])
        if obj_count > 1:
            raise ValidationError(f"相同岗位的记录了，不可重复创建！")





class AllowanceSubsidyDetection(models.Model):
    _name = 'allowance_subsidy_detection'
    _description = '津贴补助检测'
    _rec_name='hr_employee_id'
    _order = 'detection_time'

    detection_time = fields.Datetime(string="检测时间")
    hr_employee_id = fields.Many2one("hr.employee", string="员工")
    department_id = fields.Many2one('hr.department', string='部门')
    job_id = fields.Many2one('hr.job', string='岗位', compute="set_hr_employee_messages", store=True)
    departure_date = fields.Date(string="离职日期", compute="set_hr_employee_messages", store=True)
    perfect_attendance_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="全勤奖类型", compute="set_hr_employee_messages", store=True)
    housing_allowances_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="房补类型", compute="set_hr_employee_messages", store=True)
    meal_allowances_type = fields.Selection([('薪酬之内', '薪酬之内'), ('薪酬之外', '薪酬之外')], string="饭补类型", compute="set_hr_employee_messages", store=True)

    @api.depends('hr_employee_id')
    def set_hr_employee_messages(self):
        for record in self:
            if record.hr_employee_id:
                record.job_id = record.hr_employee_id.job_id.id
                record.departure_date = record.hr_employee_id.is_delete_date
                record.perfect_attendance_type = record.hr_employee_id.attendance_bonus_type
                record.housing_allowances_type = record.hr_employee_id.housing_subsidy_type
                record.meal_allowances_type = record.hr_employee_id.meal_allowance_type
            else:
                record.job_id = False
                record.departure_date = False
                record.perfect_attendance_type = False
                record.housing_allowances_type = False
                record.meal_allowances_type = False


    def allowance_subsidy_detection(self):

        allowance_subsidy_setting_objs = self.env["allowance_subsidy_setting"].sudo().search_read([],
            ["department_id", "job_id", "perfect_attendance_type", "housing_allowances_type", "meal_allowances_type"]
        )

        for allowance_subsidy_setting_obj in allowance_subsidy_setting_objs:
            job_id, *_ = allowance_subsidy_setting_obj.get("job_id")

            hr_employee_objs = self.env["hr.employee"].sudo().search_read([("job_id", "=", job_id), ("is_delete", "=", False)],
                ["attendance_bonus_type", "housing_subsidy_type", "meal_allowance_type"]
            )

            for hr_employee_obj in hr_employee_objs:
                if not (allowance_subsidy_setting_obj.get("perfect_attendance_type") == hr_employee_obj.get("attendance_bonus_type") and allowance_subsidy_setting_obj.get("housing_allowances_type") == hr_employee_obj.get("housing_subsidy_type") and allowance_subsidy_setting_obj.get("meal_allowances_type") == hr_employee_obj.get("meal_allowance_type")):
                    self.env["allowance_subsidy_detection"].sudo().create({
                        "detection_time": fields.Datetime.now(),
                        "hr_employee_id": hr_employee_obj.get("id"),
                    })
        
        return True