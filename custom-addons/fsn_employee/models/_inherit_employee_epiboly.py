from odoo import models, fields, api
from odoo.exceptions import ValidationError

"""用于外包计件工资计算"""



class HrEmployee(models.Model):
    _inherit = "hr.employee"




    epiboly_contract_line_ids = fields.One2many("epiboly_contract_line", "hr_employee_id", string="外包计件明细")

    @api.onchange("outsourcing_type")
    def set_epiboly_contract_line_ids(self):
        for record in self:
            if record.outsourcing_type == "长期":
                
                for i in self.env['long_term_temp_rate'].sudo().search([]):

                    self.env['epiboly_contract_line'].sudo().create({
                        "hr_employee_id": record.id,
                        "process_name": i.process_name,
                        "processing_cost": i.processing_cost
                    })
            else:
                record.epiboly_contract_line_ids.unlink()



class EpibolyContractLine(models.Model):
    _name = "epiboly_contract_line"
    _description = '外包(计件)合同明细'


    hr_employee_id = fields.Many2one("hr.employee", ondelete="cascade")
    outsourcing_type = fields.Char(string="外包类型", compute="set_outsourcing_type", store=True)
    @api.depends("hr_employee_id", "hr_employee_id.outsourcing_type")
    def set_outsourcing_type(self):
        for record in self:
            record.outsourcing_type = record.hr_employee_id.outsourcing_type

    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号')
    style_number = fields.Many2one('ib.detail', string='款号')
    process_number = fields.Char(string="工序号")
    process_name = fields.Char(string="工序名称")
    
    color = fields.Char(string="颜色")
    size = fields.Char(string="尺码")
    number = fields.Integer(string="件数")
    processing_cost = fields.Float(string="加工费")
    @api.onchange("order_id", "style_number", "process_number")
    def set_processing_cost(self):
        for record in self:
            if record.order_id and record.style_number and record.process_number:
                temporary_workers_apply_objs = self.env["temporary_workers_apply"].sudo().search([
                    ("order_id", "=", record.order_id.id),
                    ("style_number", "=", record.style_number.id),
                    ("process_no", "=", record.process_number),
                    ("state", "=", "审批通过")
                ])
                record.processing_cost = min(temporary_workers_apply_objs.mapped("apply_price"), default=0)
            else:
                record.processing_cost = 0

            
    delivery_date = fields.Date(string="交货日期")
    remark = fields.Char(string="备注")

    # 检查数据唯一性
    @api.constrains('hr_employee_id', 'style_number', 'process_number')
    def _check_unique(self):
        for record in self:
            if record.outsourcing_type == "短期":
                if self.env[record._name].search_count([
                    ('hr_employee_id', '=', record.hr_employee_id.id),
                    ('style_number', '=', record.style_number.id),
                    ('process_number', '=', record.process_number)
                ]) > 1:
                    raise ValidationError(f"{record.hr_employee_id.name}已经存在款号:{record.style_number.style_number},工序号:{record.process_number}的记录了！不可重复！")

            else:
                # pass
                if self.env[record._name].search_count([
                    ('hr_employee_id', '=', record.hr_employee_id.id),
                    ('process_name', '=', record.process_name),
                ]) > 1:
                    raise ValidationError(f"{record.hr_employee_id.name}已经存工序名称为{record.process_name}的记录了！不可重复！")




