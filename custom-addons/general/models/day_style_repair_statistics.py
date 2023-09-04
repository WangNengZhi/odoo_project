
from odoo import models, fields, api


class DayStyleRepairStatistics(models.Model):
    _name = 'day_style_repair_statistics'
    _description = '日款返修统计'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    group = fields.Char(string="组别")
    style_number = fields.Many2one('ib.detail', string='款号')
    sum_examine_quantity = fields.Float(string="总检数")
    repair_quantity = fields.Float(string="返修数")
    repair_proportion = fields.Float(string="返修率", digits=(16, 2), compute="set_repair_data", store=True)
    assess_index = fields.Float(string="考核", digits=(16, 2), compute="set_repair_data", store=True)


    @api.depends('sum_examine_quantity', 'repair_quantity')
    def set_repair_data(self):
        for record in self:

            record.assess_index = record.repair_quantity - (record.sum_examine_quantity * 0.1)

            if record.sum_examine_quantity:
                record.repair_proportion = (record.repair_quantity / record.sum_examine_quantity) * 100
            else:

                record.repair_proportion = 0





    # 设置日款返修统计数据
    def set_data(self):

        for record in self:
            # 查询总检表
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.dDate),
                ("group", "=", record.group),
                ("item_no", "=", record.style_number.id),
            ])
            # 临时总检数
            tem_sum_examine_quantity = 0
            # 临时返修数
            tem_repair_quantity = 0

            for general_general_obj in general_general_objs:
                tem_sum_examine_quantity = tem_sum_examine_quantity + general_general_obj.general_number
                tem_repair_quantity = tem_repair_quantity + general_general_obj.repair_number

            
            record.sum_examine_quantity = tem_sum_examine_quantity
            record.repair_quantity = tem_repair_quantity