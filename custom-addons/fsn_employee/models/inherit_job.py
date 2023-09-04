from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _inherit = "hr.job"

    active = fields.Boolean(default=True)
    actual_number_of_employees = fields.Integer(string='实际员工数量', compute='test_compute_employees', store=True)


    @api.depends('employee_ids.job_id', 'employee_ids.active', 'employee_ids.is_delete')
    def test_compute_employees(self):
        employee_data = self.env['hr.employee'].read_group([('job_id', 'in', self.ids),
                                                            ('is_delete', '=', False),
                                                            ], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in employee_data)
        for job in self:
            job.actual_number_of_employees = result.get(job.id, 0)


class FsnJobCreateAudit(models.Model):
    _name = 'fsn_job_create_audit'
    _description = 'FSN岗位创建审核'
    _rec_name='job_name'
    _order = "date desc"


    job_id = fields.Many2one("hr.job", string="岗位id")
    date = fields.Date(string="申请日期", required=True)
    job_name = fields.Char(string="岗位名称", required=True)
    department_id = fields.Many2one('hr.department', string='部门', required=True)
    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")


    # 确认弹窗
    def confirmation_button(self):

        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"
        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'fsn_job_create_audit',
            'view_id': self.env.ref('fsn_employee.fsn_job_create_audit_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action


    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            if self.state == "已审批":
                self.state = "待审批"
                self.job_id.unlink()
  

        elif button_type == "through":
            if self.state == "待审批":

                job_id = self.job_id.create({
                    "name": self.job_name,
                    "department_id": self.department_id.id
                })
                self.job_id = job_id.id
                self.state = "已审批"



    def write(self, vals):

        if self.state != "待审批":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"审批过程中的单据, 不可修改！。")


        return super(FsnJobCreateAudit, self).write(vals)



    def unlink(self):

        for record in self:

            if record.state != "待审批":

                raise ValidationError(f"审批过程中的单据, 不可删除！。")

        return super(FsnJobCreateAudit, self).unlink()