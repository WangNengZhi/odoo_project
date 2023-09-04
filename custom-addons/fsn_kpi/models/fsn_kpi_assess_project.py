
from odoo import models, fields, api


class FsnKpiTemplate(models.Model):
    _name = 'fsn_kpi_assess_project'
    _description = 'FSN_KPI考核项目'
    _rec_name = 'assess_project_serial_number'
    _order = "assess_project_serial_number desc"


    assess_project_serial_number = fields.Char(string="考核项目类型")
    department_id = fields.Many2one("hr.department", string="部门", required=True)
    job_id = fields.Many2one('hr.job', string='岗位', required=True, domain="[('department_id', '=', department_id)]")
    method_name = fields.Char(string="方法名称", required=True)
    assessment_content = fields.Char(string="考核内容")
    assessment_standard = fields.Text(string="考核标准")
    score = fields.Float(string="分值")
    calculation = fields.Text(string="计算方式")


    @api.model
    def create(self, vals):

        vals['assess_project_serial_number'] = self.env['ir.sequence'].next_by_code('fsn_kpi_assess_project_sequence')
        
        return super(FsnKpiTemplate, self).create(vals)

