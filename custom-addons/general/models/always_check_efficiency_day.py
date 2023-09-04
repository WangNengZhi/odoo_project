import re
from odoo import models, fields, api
import calendar, datetime


class AlwaysCheckEffyDay(models.Model):
    _name = 'always_check_eff_day'
    _description = '总检效率表(日)'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    ace_day_group_line_ids = fields.One2many("ace_day_group_line", "always_check_eff_day_id", string="组别")
    ace_day_style_number_line_ids = fields.One2many("ace_day_style_number_line", "always_check_eff_day_id", string="款号")
    always_check_principal = fields.Char(string="总检")
    repair_quantity = fields.Float(string="返修数量")
    check_quantity = fields.Float(string="查货数量")
    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True)
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)


    # 设置返修率
    @api.depends('repair_quantity', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_quantity:

                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100

                # if record.repair_quantity:
                #     # 考核
                #     record.assess_index = (record.repair_quantity - (record.check_quantity * 0.03)) * 2
                # else:
                #     record.assess_index = 0
            
            else:
                record.repair_ratio = 0


    # 设置总检效率表数据
    def set_date(self):
        for record in self: 
            
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.dDate),
                ("general1", "=", record.always_check_principal)
            ])

            # 临时查货数量
            tem_check_quantity = 0
            # 临时组别明细
            tem_group_line_ids = []
            # 临时款号明细
            tem_style_number_line_ids = []
            for general_general_obj in general_general_objs:

                tem_check_quantity = tem_check_quantity + general_general_obj.general_number
                tem_group_line_ids.append((0, 0,{"name": general_general_obj.group}))
                tem_style_number_line_ids.append((0, 0,{"name": general_general_obj.item_no.id}))

            record.check_quantity = tem_check_quantity
            record.ace_day_group_line_ids = tem_group_line_ids
            record.ace_day_style_number_line_ids = tem_style_number_line_ids



    def set_repair_quantity(self):
        for record in self:

            tem_repair_value = 0

            for line in record.ace_day_style_number_line_ids:

                repair_value_objs = self.env["repair_value"].sudo().search([
                    ("style_number", "=", line.name.id),
                    ("date", "=", record.dDate),
                ])

                for repair_value_obj in repair_value_objs:
                    tem_repair_value = tem_repair_value + repair_value_obj.number
            
            record.repair_quantity = tem_repair_value






class AceDayGroupLine(models.Model):
    _name = 'ace_day_group_line'
    _description = '总检效率表组别明细(日)'
    _order = "name"


    always_check_eff_day_id = fields.Many2one("always_check_eff_day")
    name = fields.Char(string="组名")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        ace_day_group_line_obj = self.env["ace_day_group_line"].sudo().search([
            ("always_check_eff_day_id", "=", vals["always_check_eff_day_id"]),
            ("name", "=", vals["name"]),
            ])
        if ace_day_group_line_obj:
            ace_day_group_line_obj.unlink()
            

        instance = super(AceDayGroupLine, self).create(vals)
    
        return instance


class AceDayStyleNumberLine(models.Model):

    _name = 'ace_day_style_number_line'
    _description = '总检效率表款号明细(日)'
    _order = "name"

    always_check_eff_day_id = fields.Many2one("always_check_eff_day")
    name = fields.Many2one("ib.detail", string="款号")
    # repair_quantity = fields.Float(string="返修数量")

    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        ace_day_style_number_line_obj = self.env["ace_day_style_number_line"].sudo().search([
            ("always_check_eff_day_id", "=", vals["always_check_eff_day_id"]),
            ("name", "=", vals["name"])
            ])

        if ace_day_style_number_line_obj:
            ace_day_style_number_line_obj.unlink()


        instance = super(AceDayStyleNumberLine, self).create(vals)
    
        return instance