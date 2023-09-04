from odoo import models, fields, api
import calendar, datetime


class MiddleCheckEfficiency(models.Model):
    _name = 'middle_check_efficiency'
    _description = '中查效率表'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group_line_ids = fields.One2many("middle_check_group_line", "middle_check_efficiency_id", string="组别")
    middle_check_principal = fields.Char(string="中查")
    repair_quantity = fields.Float(string="返修数量")
    check_quantity = fields.Float(string="查货数量")
    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')

    # 设置返修率
    @api.depends('repair_quantity', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_quantity:
                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100
            else:

                record.repair_ratio = 0



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


    # 设置中查效率表数据
    def set_date(self):
        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end()   
            
            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("invest", "=", record.middle_check_principal)
            ])
            # 临时返修数量
            tem_repair_quantity = 0
            # 临时查货数量
            tem_check_quantity = 0
            # 临时组别明细
            tem_group_line_ids = []
            for invest_invest_obj in invest_invest_objs:
                # for line_group_obj in record.group_line_ids:
                #     line_group_obj.sudo().unlink()

                tem_repair_quantity = tem_repair_quantity + invest_invest_obj.repairs_number
                tem_check_quantity = tem_check_quantity + invest_invest_obj.check_the_quantity
                tem_group_line_ids.append((0, 0, {"name": invest_invest_obj.group}))

            record.repair_quantity = tem_repair_quantity
            record.check_quantity = tem_check_quantity
            record.group_line_ids = tem_group_line_ids



class MiddleCheckGroupLine(models.Model):
    _name = 'middle_check_group_line'
    _description = '中查效率表组别明细'
    _order = "name"


    middle_check_efficiency_id = fields.Many2one("middle_check_efficiency")
    name = fields.Char(string="组名")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        repair_value_group_obj = self.env["middle_check_group_line"].sudo().search([
            ("middle_check_efficiency_id", "=", vals["middle_check_efficiency_id"]),
            ("name", "=", vals["name"])
            ])
        if repair_value_group_obj:
            repair_value_group_obj.unlink()
            

        instance = super(MiddleCheckGroupLine, self).create(vals)
    
        return instance