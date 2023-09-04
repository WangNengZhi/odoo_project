from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FsnKpiDepartment(models.Model):
    _name = 'fsn_kpi_department'
    _description = 'FSN_KPI专用部门'
    _rec_name = 'name'
    # _order = "start_date desc"



    name = fields.Char(string="部门名称", required=True)
    fsn_kpi_job_line_ids = fields.One2many("fsn_kpi_job", "fsn_kpi_department_id", string="岗位明细")


class FsnKpiJob(models.Model):
    _name = 'fsn_kpi_job'
    _description = 'FSN_KPI专用岗位'
    _rec_name = 'name'
    # _order = "start_date desc"


    fsn_kpi_department_id = fields.Many2one("fsn_kpi_department", ondelete="cascade")
    name = fields.Char(string="岗位名称")