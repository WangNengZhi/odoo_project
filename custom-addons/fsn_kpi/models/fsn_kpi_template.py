
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FsnKpiTemplate(models.Model):
    _name = 'fsn_kpi_template'
    _description = 'FSN_KPI模板'
    # _rec_name = 'name'
    # _order = "start_date desc"


    date = fields.Date(string="日期", required=True)
    department_id = fields.Many2one("hr.department", string="部门", required=True)
    job_id = fields.Many2one('hr.job', string='岗位', required=True, domain="[('department_id', '=', department_id)]")
    is_active = fields.Boolean(string="启动")

    fsn_kpi_template_line_ids = fields.One2many("fsn_kpi_template_line", "fsn_kpi_template_id", string="FSN_KPI_模板明细", copy=True)





    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.department_id.name}-{record.job_id.name}"
            result.append((record.id, rec_name))
        return result



class FsnKpiTemplateLine(models.Model):
    _name = 'fsn_kpi_template_line'
    _description = 'FSN_KPI模板明细'


    fsn_kpi_template_id = fields.Many2one("fsn_kpi_template", ondelete="cascade")
    sequence = fields.Integer(string="序号")
    assessment_project = fields.Selection([
        ('本职工作', '本职工作'),
        ('工作能力', '工作能力'),
        ('工作态度', '工作态度'),
        ],string="考核项目")
    assess_project = fields.Many2one("fsn_kpi_assess_project", string="自动考核")


    assessment_content = fields.Char(string="考核内容")
    assessment_standard = fields.Text(string="考核标准")
    score = fields.Float(string="分值")
    calculation = fields.Char(string="计算方式")
    @api.onchange("assess_project")
    def set_assess_project_info(self):
        for record in self:
            record.assessment_content = record.assess_project.assessment_content
            record.assessment_standard = record.assess_project.assessment_standard
            record.score = record.assess_project.score
            record.calculation = record.assess_project.calculation
    inspection_people = fields.Many2one('hr.employee', string='考核人')
    evaluation_score = fields.Float(string="考核评分")


