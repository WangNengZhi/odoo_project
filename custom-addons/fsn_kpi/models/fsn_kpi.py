from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FsnKpi(models.Model):
    _name = 'fsn_kpi'
    _description = 'FSN_KPI'
    _rec_name = 'year_month'
    _order = "year_month desc"



    year = fields.Integer(string='年')
    month = fields.Integer(string='月')
    year_month = fields.Char(string='月份', required=True)


    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    department_id = fields.Many2one("hr.department", string="部门", required=True)
    job_id = fields.Many2one('hr.job', string='岗位', required=True, domain="[('department_id', '=', department_id)]")


    inspection_people = fields.Many2one('hr.employee', string="考核人")
    full_marks = fields.Float(string="满分", compute="set_total_score", store=True)
    total_score = fields.Float(string="总计得分", compute="set_total_score", store=True)

    fsn_kpi_line_ids = fields.One2many("fsn_kpi_line", "fsn_kpi_id", string="KPI明细")



    @api.depends('fsn_kpi_line_ids', 'fsn_kpi_line_ids.evaluation_score')
    def set_total_score(self):

        for record in self:

            tem_full_marks = 0      # 临时满分

            tem_total_score = 0     # 临时总计得分

            for fsn_kpi_line_obj in record.fsn_kpi_line_ids:

                tem_full_marks = tem_full_marks + fsn_kpi_line_obj.score

                tem_total_score = tem_total_score + fsn_kpi_line_obj.evaluation_score
            
            record.full_marks = tem_full_marks

            record.total_score = tem_total_score



    # 获取明细
    @api.onchange('job_id')
    def _onchange_fsn_kpi_line_ids(self):

        self.fsn_kpi_line_ids = False

        if self.job_id:
            
            fsn_kpi_template_objs = self.env["fsn_kpi_template"].sudo().search([
                ("job_id", "=", self.job_id.id),
                ("is_active", "=", True)
            ])
            if len(fsn_kpi_template_objs) == 1:

                lines = []

                for obj in fsn_kpi_template_objs.fsn_kpi_template_line_ids:

                    line = {
                        "sequence": obj.sequence,      # 序号
                        "assessment_project": obj.assessment_project,   # 考核项目
                        "assess_project": obj.assess_project.id,    # 自动考核
                        "assessment_content": obj.assessment_content,     # 考核内容
                        "assessment_standard": obj.assessment_standard,     # 考核标准
                        "score": obj.score,     # 分值
                        "calculation": obj.calculation,     # 计算方式
                    }
                    lines.append((0, 0, line))


                self.fsn_kpi_line_ids = lines
            elif len(fsn_kpi_template_objs) > 1:
                raise ValidationError('该岗位存在多个启用的模板。')
            else:
                raise ValidationError('没有找到该岗位启用的模板！')







class FsnKpiLine(models.Model):
    _name = 'fsn_kpi_line'
    _description = 'FSN_KPI_LINE'
    _order = "sequence"


    fsn_kpi_id = fields.Many2one("fsn_kpi")
    assessment_project = fields.Selection([
        ('本职工作', '本职工作'),
        ('工作能力', '工作能力'),
        ('工作态度', '工作态度'),
        ],string="考核项目")
    assess_project = fields.Many2one("fsn_kpi_assess_project", string="自动考核")
    assessment_content = fields.Char(string="考核内容")
    assessment_standard = fields.Text(string="考核标准")
    score = fields.Float(string="分值")
    calculation = fields.Text(string="计算方式")
    inspection_people = fields.Many2one('hr.employee', string='考核人')
    evaluation_score = fields.Float(string="考核评分")
    sequence = fields.Integer(string="序号")