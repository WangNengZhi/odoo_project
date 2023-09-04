from odoo import models, fields, api
import calendar, datetime


class AlwaysCheckEfficiency(models.Model):
    _name = 'always_check_efficiency'
    _description = '总检效率表'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group_line_ids = fields.One2many("always_check_group_line", "always_check_efficiency_id", string="组别")
    style_number_line_ids = fields.One2many("style_number_line", "always_check_efficiency_id", string="款号")
    always_check_principal = fields.Char(string="总检")
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

                if record.repair_quantity:
                    # 考核
                    tem_assess_index = (record.repair_quantity - (record.check_quantity * 0.03)) * 2
                    if tem_assess_index < 0:

                        record.assess_index = 0
                    
                    else:
                        record.assess_index = tem_assess_index
                else:
                    record.assess_index = 0
            
            else:
                record.repair_ratio = 0
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


    # 设置总检效率表数据
    def set_date(self):
        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end()   
            
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("general1", "=", record.always_check_principal)
            ])
            # 临时返修数量
            # tem_repair_quantity = 0
            # 临时查货数量
            tem_check_quantity = 0
            # 临时组别明细
            tem_group_line_ids = []
            # 临时款号明细
            tem_style_number_line_ids = []
            for general_general_obj in general_general_objs:

                # for line_group_obj in record.group_line_ids:
                #     line_group_obj.sudo().unlink()

                # for line_style_number_obj in record.style_number_line_ids:
                #     line_style_number_obj.sudo().unlink()

                # tem_repair_quantity = tem_repair_quantity + invest_invest_obj.repairs_number
                tem_check_quantity = tem_check_quantity + general_general_obj.general_number
                tem_group_line_ids.append((0, 0,{"name": general_general_obj.group}))
                tem_style_number_line_ids.append((0, 0,{"name": general_general_obj.item_no.id}))

            # record.repair_quantity = tem_repair_quantity
            record.check_quantity = tem_check_quantity
            record.group_line_ids = tem_group_line_ids
            record.style_number_line_ids = tem_style_number_line_ids


    # 设置返修数量
    def set_repair_quantity(self):
        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = record.compute_start_and_end()
            # 临时返修件数
            tem_repair_value = 0

            for line in record.style_number_line_ids:

                repair_value_objs = self.env["repair_value"].sudo().search([
                    ("style_number", "=", line.name.id),
                    ("date", ">=", date_dict['start']),
                    ("date", "<=", date_dict['end']),
                ])

                for repair_value_obj in repair_value_objs:
                    tem_repair_value = tem_repair_value + repair_value_obj.number
            
            record.repair_quantity = tem_repair_value







class AlwaysCheckGroupLine(models.Model):
    _name = 'always_check_group_line'
    _description = '总检效率表组别明细'
    _order = "name"


    always_check_efficiency_id = fields.Many2one("always_check_efficiency")
    name = fields.Char(string="组名")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        repair_value_group_obj = self.env["always_check_group_line"].sudo().search([
            ("always_check_efficiency_id", "=", vals["always_check_efficiency_id"]),
            ("name", "=", vals["name"]),
            ])
        if repair_value_group_obj:
            repair_value_group_obj.unlink()
            

        instance = super(AlwaysCheckGroupLine, self).create(vals)
    
        return instance


class AlwaysCheckStyleNumberline(models.Model):

    _name = 'style_number_line'
    _description = '总检效率表款号明细'
    _order = "name"

    always_check_efficiency_id = fields.Many2one("always_check_efficiency")
    name = fields.Many2one("ib.detail", string="款号")
    # repair_quantity = fields.Float(string="返修数量")

    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        repair_value_group_obj = self.env["style_number_line"].sudo().search([
            ("always_check_efficiency_id", "=", vals["always_check_efficiency_id"]),
            ("name", "=", vals["name"])
            ])
        if repair_value_group_obj:
            repair_value_group_obj.unlink()
            

        instance = super(AlwaysCheckStyleNumberline, self).create(vals)
    
        return instance
