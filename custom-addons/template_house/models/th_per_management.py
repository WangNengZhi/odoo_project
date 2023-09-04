
from odoo import models, fields, api
from odoo.exceptions import ValidationError



class ThPerManagement(models.Model):
    _name = 'th_per_management'
    _description = '样衣'
    _rec_name = 'employee_id'
    _order = 'date desc'

    date = fields.Date(string="日期", required=True)
    start_date = fields.Date(string="开始日期")
    end_date = fields.Date(string="结束日期")
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    work_type = fields.Char(string="工种", compute="set_employee_info", store=True)
    departure_date = fields.Date(string="离职日期")
    job_id = fields.Many2one("hr.job", string="岗位", compute="set_employee_info", store=True)
    job_content = fields.Text(string="工作内容")
    plan_production = fields.Float(string="计划产量")
    actual_production = fields.Float(string="实际产量")

    IE_working_hours = fields.Float(string='IE工时(秒)', digits=(16, 5))
    product_design_id = fields.Many2one("product_design", string="设计编号", required=True)
    fsn_platemaking_record_id = fields.Many2one("fsn_platemaking_record", string="版号", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    sample_image = fields.Image(string="图片")

    state = fields.Selection([('待审批', '待审批'), ('客户已审批', '客户已审批')], string="状态", default="待审批")
    is_supervisor_approval = fields.Boolean(string="主管审批")
    is_quality_control_approval = fields.Boolean(string="品控审批")

    # 设置员工信息
    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            
            record.work_type = record.employee_id.is_it_a_temporary_worker
            record.job_id = record.employee_id.job_id.id

    
    def state_change(self):
        ''' 客户审批'''
        for record in self:
            button_type = self.env.context.get("type")
            if button_type == "fallback":
                record.sudo().state = "待审批"
            elif button_type == "through":
                record.sudo().state = "客户已审批"


    def set_is_supervisor_approval(self):
        ''' 主管审批'''
        for record in self:
            button_type = self.env.context.get("type")
            if button_type == "fallback":
                record.sudo().is_supervisor_approval = False
            elif button_type == "through":
                record.sudo().is_supervisor_approval = True


    def set_is_quality_control_approval(self):
        ''' 品控审批'''
        for record in self:
            button_type = self.env.context.get("type")
            if button_type == "fallback":
                record.sudo().is_quality_control_approval = False
            elif button_type == "through":
                record.sudo().is_quality_control_approval = True

