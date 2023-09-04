from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AfterWholeSpecialKpi(models.Model):
    _name = 'after_whole_special_kpi'
    _description = 'FSN_KPI'
    _rec_name = 'employee_id'
    _order = "start_date desc"



    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    department_id = fields.Many2one('hr.department', compute="set_employee_messages", store=True, string='部门')
    inspection_people = fields.Many2one('hr.employee', string="考核人", required=True)

    fsn_department_job = fields.Selection([
        ('后整', '后整'),
        ('技术部', '技术部'),
        ('办公室', '办公室'),
        ('生产部', '生产部'),
    ], string="部门")
    fsn_kpi_job = fields.Selection([
        ('专机', '专机'),
        ('样衣员', '样衣员'),
        ('办公室主任', '办公室主任'),
        ('理单员', '理单员'),
        ('技术主管', '技术主管'),
        ('车间主任', '车间主任'),
        ('包装', '包装'),
        ('大烫', '大烫'),
        ('小烫', '小烫'),
        ('人事专员', '人事专员'),
        ('人事主管', '人事主管'),
        ('车工', '车工'),
        ('组长', '组长'),
        ('模板师', '模板师'),
        ('IE', 'IE'),
        ('机修', '机修'),
        ],string="岗位")
    start_date = fields.Date(string="考核开始日期", required=True,)
    end_date = fields.Date(string="考核结束日期", required=True,)
    special_kpi_line_ids = fields.One2many("special_kpi_line", "after_whole_special_kpi_id", string="后整_专机_KPI_考核明细")

    full_marks = fields.Float(string="满分", compute="set_total_score", store=True)
    total_score = fields.Float(string="总计得分", compute="set_total_score", store=True)



    @api.depends('special_kpi_line_ids')
    def set_total_score(self):


        for record in self:

            tem_full_marks = 0      # 临时满分

            tem_total_score = 0     # 临时总计得分

            for special_kpi_line_id in record.special_kpi_line_ids:

                tem_full_marks = tem_full_marks + special_kpi_line_id.score

                tem_total_score = tem_total_score + special_kpi_line_id.evaluation_score
            
            record.full_marks = tem_full_marks

            record.total_score = tem_total_score




    @api.onchange('fsn_kpi_job')
    def set_special_kpi_line_ids(self):
        for record in self:
            template_ids = self.env["special_kpi_line_template"].search([("fsn_kpi_job", "=", record.fsn_kpi_job)])

            lines = []

            for template_id in template_ids:
                line = {
                    "after_whole_special_kpi_id": record.id,
                    "assessment_project": template_id.assessment_project,   # 考核项目
                    "assessment_content": template_id.assessment_content,   # 考核内容
                    "assessment_standard": template_id.assessment_standard,     # 考核标准
                    "score": template_id.score,     # 分值
                    "calculation": template_id.calculation,     # 计算方式
                    "inspection_people": template_id.inspection_people,     # 考核人
                    "evaluation_score": template_id.evaluation_score,   # 考核评分
                    "sequence": template_id.sequence   # 序号
                }

                if template_id.score != 0:
                    lines.append((0, 0, line))
            
            record.special_kpi_line_ids = lines


    # 设置当前薪资
    @api.depends('employee_id')
    def set_employee_messages(self):
        for record in self:

            # 部门
            record.department_id = record.employee_id.department_id.id




class SpecialKpiLine(models.Model):
    _name = 'special_kpi_line'
    _description = 'FSN_KPI_考核明细'
    _order = "sequence"


    after_whole_special_kpi_id = fields.Many2one("after_whole_special_kpi")
    fsn_kpi_job = fields.Selection([
        ('专机', '专机'),
        ('样衣员', '样衣员'),
        ('办公室主任', '办公室主任'),
        ('理单员', '理单员'),
        ('技术主管', '技术主管'),
        ('车间主任', '车间主任'),
        ('包装', '包装'),
        ('大烫', '大烫'),
        ('小烫', '小烫'),
        ('人事专员', '人事专员'),
        ('人事主管', '人事主管'),
        ('车工', '车工'),
        ('组长', '组长'),
        ('模板师', '模板师'),
        ('IE', 'IE'),
        ('机修', '机修'),
        ],string="岗位")
    assessment_project = fields.Selection([
        ('本职工作', '本职工作'),
        ('工作能力', '工作能力'),
        ('工作态度', '工作态度'),
        ],string="考核项目")
    assessment_content = fields.Char(string="考核内容")
    assessment_standard = fields.Text(string="考核标准")
    score = fields.Float(string="分值")
    calculation = fields.Char(string="计算方式")
    inspection_people = fields.Many2one('hr.employee', string='考核人')
    evaluation_score = fields.Float(string="考核评分")
    sequence = fields.Integer(string="序号")







    