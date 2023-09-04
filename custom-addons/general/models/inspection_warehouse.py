from odoo import models, fields, api

class InspectionWarehouse(models.Model):
    _name = 'inspection_warehouse'
    _description = '仓库检查'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    project = fields.Char(string="项目", required=True)
    inspector = fields.Many2one('hr.employee', string='检验员', required=True)
    amount = fields.Integer(string="总数量")
    sampling_amount = fields.Integer(string="抽样量")
    bad_amount = fields.Integer(string="不良数")
    major_problem_areas = fields.Text(string="主要问题点")
    quality = fields.Selection([('合格', '合格'), ('不合格', '不合格')], string="合格是否", required=True)
    description = fields.Text(string="备注")



    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}