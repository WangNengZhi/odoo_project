from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar, datetime


class QualityControlPerformance(models.Model):
    _name = 'quality_control_performance'
    _description = '品控绩效记录'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group = fields.Char(string="组别")
    # quality_control_group_line_ids = fields.One2many("quality_control_group_line", "quality_control_performance_id", string="组别")
    repair_amount = fields.Float(string="返修件数")
    workshop_amount = fields.Float(string="车间件数")
    repair_proportion = fields.Float(string="返修率", compute="set_repair_proportion", store=True)
    assess_index = fields.Float(string="考核", compute="set_repair_proportion", store=True)
    principal = fields.Many2one('hr.employee', string="负责人")




    # 设置返修率
    @api.depends('repair_amount', 'workshop_amount')
    def set_repair_proportion(self):
        for record in self:
            if record.workshop_amount:
                # 返修率
                record.repair_proportion = (record.repair_amount / record.workshop_amount) * 100
            else:
                record.repair_proportion = 0

            if record.repair_amount:
                # 考核
                record.assess_index = 2 * record.repair_amount - (record.workshop_amount * 0.03)
            else:
                record.assess_index = 0


    # 计算月的第一天和最后一天
    def compute_start_and_end(self):

        if self.month:
            # 获取当前月份的第一天和最后一天
            date_list = self.month.split("-")
            date_year = int(date_list[0])
            date_month = int(date_list[1])
            last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
            start = datetime.date(date_year, date_month, 1)
            end = datetime.date(date_year, date_month, last_day)

            return {"start": start, "end": end}


    # 设置本月考核数据
    def set_assess_index(self):
        for record in self:
            # 获取一个月的开始时间和结束时间
            date_dict = self.compute_start_and_end()

            # 查询返修产值表
            repair_value_objs = self.env["repair_value"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
            ])

            # 临时返修数
            tem_repair_amount = 0

            for repair_value_obj in repair_value_objs:

                tem_group_line_list = []

                for group_line in repair_value_obj.repair_value_group_line_ids:
                    tem_group_line_list.append(group_line.name)

                if record.group in tem_group_line_list:

                    # 临时返修产值
                    tem_repair_amount = tem_repair_amount + repair_value_obj.number


            # 查询组产值表
            pro_pro_objs = self.env["pro.pro"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("group", "=", record.group)
            ])
            # 临时车间数量
            tem_repair_quantity = 0
            for pro_pro_obj in pro_pro_objs:
                tem_repair_quantity = tem_repair_quantity + pro_pro_obj.number



            record.repair_amount = tem_repair_amount
            record.workshop_amount = tem_repair_quantity

