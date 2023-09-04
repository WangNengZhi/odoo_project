from odoo import models, fields, api


class QualityRecords(models.Model):
    _name = 'quality_records'
    _description = '品质记录表'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)

    inspection_item_ids = fields.Many2many("quality_records_inspection_item", string="检验项目", required=True)

    product_problem = fields.Text(string="产品问题")
    handling_method = fields.Text(string="处理方法")

    examinant_id = fields.Many2one('hr.employee', string='巡查员', required=True)
    remark = fields.Text(string="备注")



class QualityRecordsInspectionItem(models.Model):
    _name = 'quality_records_inspection_item'
    _description = '品质记录表_检验项目'

    name = fields.Char(string="项目名称")