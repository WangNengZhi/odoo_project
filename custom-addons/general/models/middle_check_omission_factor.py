from odoo import models, fields, api
import calendar, datetime


class MiddleCheckOmissionFactor(models.Model):
    _name = 'middle_check_omission_factor'
    _description = '中查漏查表'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group_line_ids = fields.One2many("omission_factor_group_line", "middle_check_omission_factor_id", string="组别")
    middle_check_principal = fields.Char(string="中查")
    repair_quantity = fields.Float(string="返修数量")
    check_quantity = fields.Float(string="查货数量")
    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)


    # 设置返修率
    @api.depends('repair_quantity', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_quantity:
                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100
            else:

                record.repair_ratio = 0

            tem_assess_index = (record.check_quantity - record.repair_quantity) * 2
            
            if tem_assess_index < 0:

                record.assess_index = 0
            else:
                record.assess_index = tem_assess_index





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


    # 设置中查漏查表数据
    def set_date(self):
        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end()   
            
            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("invest", "=", record.middle_check_principal)
            ])

            # 临时查货数量
            tem_check_quantity = 0
            # 临时组别明细
            tem_group_line_ids = []
            for invest_invest_obj in invest_invest_objs:

                tem_check_quantity = tem_check_quantity + invest_invest_obj.check_the_quantity
                tem_group_line_ids.append((0, 0, {"name": invest_invest_obj.group}))

            record.check_quantity = tem_check_quantity
            record.group_line_ids = tem_group_line_ids


    # 设置返修数量
    def set_repair_quantity(self):
        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = record.compute_start_and_end()
            # 临时返修件数
            tem_repair_value = 0

            repair_value_objs = self.env["general.general"].sudo().search([
                ("invest", "=", record.middle_check_principal),
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("repair_type", "=", "车位返修"),
            ])

            for repair_value_obj in repair_value_objs:
                tem_repair_value = tem_repair_value + repair_value_obj.repair_number
            
            record.repair_quantity = tem_repair_value



class OmissionFactorGroupLine(models.Model):
    _name = 'omission_factor_group_line'
    _description = '中查漏查表组别明细'
    _order = "name"


    middle_check_omission_factor_id = fields.Many2one("middle_check_omission_factor")
    name = fields.Char(string="组名")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        omission_factor_group_line_obj = self.env["omission_factor_group_line"].sudo().search([
            ("middle_check_omission_factor_id", "=", vals["middle_check_omission_factor_id"]),
            ("name", "=", vals["name"])
            ])
        if omission_factor_group_line_obj:
            omission_factor_group_line_obj.unlink()
            

        instance = super(OmissionFactorGroupLine, self).create(vals)
    
        return instance



