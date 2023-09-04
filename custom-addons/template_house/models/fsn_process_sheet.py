from odoo import models, fields, api

class FsnProcessSheet(models.Model):
    _name = 'fsn_process_sheet'
    _description = '工艺单记录'
    _rec_name = 'style_number'
    _order = 'date desc'

    date = fields.Date(string="日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    work_type = fields.Char(string="工种", compute="set_employee_info", store=True)
    job_id = fields.Many2one("hr.job", string="岗位", compute="set_employee_info", store=True)
    # 设置员工信息
    @api.depends('employee_id')
    def set_employee_info(self):
        for record in self:
            
            record.work_type = record.employee_id.is_it_a_temporary_worker
            record.job_id = record.employee_id.job_id.id

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    process_sheet_attachment_ids = fields.Many2many('ir.attachment', string="工艺单附件")
    remark = fields.Text(string="备注")