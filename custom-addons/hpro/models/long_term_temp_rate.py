from odoo import models, fields, api
from odoo.exceptions import ValidationError



class LongTermTempRate(models.Model):
    _name = "long_term_temp_rate"
    _description = '长期外包工价'
    _rec_name = "process_name"

    process_name = fields.Char(string="工序名称", required=True)
    standard_working_hours = fields.Float(string="标准工时")
    standard_wages = fields.Float(string="标准工价")
    processing_cost = fields.Float(string="价格")


    # 检查数据唯一性
    @api.constrains('process_name')
    def _check_unique(self):
        if self.env[self._name].search_count([('process_name', '=', self.process_name),]) > 1:
            raise ValidationError(f"已经存在工序名称为{self.process_name}的记录了！工序名称不可重复！")