from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MiddleCheckWorkpieceRatio(models.Model):
    _name = 'middle_check_workpiece_ratio'
    _description = '中查每日漏查(按款号)'
    _rec_name = 'ib_detail_id'
    _order = "date desc"


    date = fields.Date(string="日期")
    ib_detail_id = fields.Many2one("ib.detail", string="款号")
    # middle_check_date_line_ids = fields.One2many("middle_check_date_line", "middle_check_workpiece_ratio_id", string="日期")
    workpiece_ratio_group_line_ids = fields.One2many("workpiece_ratio_group_line", "middle_check_workpiece_ratio_id", string="组别")
    workpiece_ratio_principals_ids = fields.One2many("workpiece_ratio_principals", "middle_check_workpiece_ratio_id", string="中查")

    # middle_check_principal = fields.Char(string="中查")
    repair_quantity = fields.Float(string="当日返修数量")
    intraday_always_check_quantity = fields.Float(string="当日总检数量(总检)")
    intraday_repair_ratio = fields.Float(string="当日返修率", compute="set_intraday_repair_ratio", store=True)

    repair_value_sum = fields.Float(string="返修总数量(总检)")
    check_quantity = fields.Float(string="查货总数量")

    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    # assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)



    # 设置当日返修率
    @api.depends('repair_quantity', 'intraday_always_check_quantity')
    def set_intraday_repair_ratio(self):
        for record in self:
            if record.intraday_always_check_quantity:
                record.intraday_repair_ratio = (record.repair_quantity / record.intraday_always_check_quantity) * 100


    # 设置返修率
    @api.depends('repair_value_sum', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_value_sum:
                record.repair_ratio = (record.repair_value_sum / record.check_quantity) * 100
            else:

                record.repair_ratio = 0



    # 设置中查效率表数据
    def set_date(self):
        for record in self:

            record.workpiece_ratio_group_line_ids.sudo().unlink()
            record.workpiece_ratio_principals_ids.sudo().unlink()


            # 临时组别明细
            tem_group_line_ids = []
            # 临时中查明细
            tem_middle_check_principal = []

            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.date),
                ("item_no", "=", record.ib_detail_id.id),
                ("repair_type", "=", "车位返修"),
            ])
            for general_general_obj in general_general_objs:
                tem_group_line_ids.append((0, 0, {"name": general_general_obj.group}))

                tem_middle_check_principal.append((0, 0, {"name": general_general_obj.invest}))

            record.workpiece_ratio_group_line_ids = tem_group_line_ids
            record.workpiece_ratio_principals_ids = tem_middle_check_principal

            # 临时当日返修数量
            tem_repair_quantity = 0
            # 临时当日查货数
            tem_intraday_always_check_quantity = 0
            # 临时返修总数量
            tem_repair_value_sum = 0
            # 临时总查货数
            tem_check_quantity = 0

            for tem_obj in record.workpiece_ratio_principals_ids:

                general_general_objs = self.env["general.general"].sudo().search([
                    ("date", "<=", record.date),
                    ("item_no", "=", record.ib_detail_id.id),
                    ("repair_type", "=", "车位返修"),
                    ('invest', '=', tem_obj.name)
                ])
                for general_general_obj in general_general_objs:

                    tem_repair_value_sum = tem_repair_value_sum + general_general_obj.repair_number

                    if general_general_obj.date == record.date:

                        tem_repair_quantity = tem_repair_quantity + general_general_obj.repair_number

                        tem_intraday_always_check_quantity = tem_intraday_always_check_quantity + general_general_obj.general_number



                tem_invest_invest_objs = self.env["invest.invest"].sudo().search([
                    ("style_number", "=", record.ib_detail_id.id),
                    ('invest', '=', tem_obj.name),
                    ("date", "<=", record.date)
                ])

                for tem_invest_invest_obj in tem_invest_invest_objs:
                    tem_check_quantity = tem_check_quantity + tem_invest_invest_obj.check_the_quantity
                

            record.check_quantity = tem_check_quantity

            record.repair_quantity = tem_repair_quantity
            record.intraday_always_check_quantity = tem_intraday_always_check_quantity
            record.repair_value_sum = tem_repair_value_sum










class MiddleCheckDateLine(models.Model):
    _name = 'middle_check_date_line'
    _description = '中查日期明细'
    # _order = "name"



class WorkpieceRatioPrincipal(models.Model):
    _name = 'workpiece_ratio_principals'
    _description = '中查人员明细'

    middle_check_workpiece_ratio_id = fields.Many2one("middle_check_workpiece_ratio")
    name = fields.Char(string="人员名称")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        workpiece_ratio_principals_objs = self.env["workpiece_ratio_principals"].sudo().search([
            ("middle_check_workpiece_ratio_id", "=", vals["middle_check_workpiece_ratio_id"]),
            ("name", "=", vals["name"])
            ])
        if workpiece_ratio_principals_objs:
            workpiece_ratio_principals_objs.unlink()
            

        instance = super(WorkpieceRatioPrincipal, self).create(vals)
    
        return instance


class WorkpieceRatioGroupLine(models.Model):
    _name = 'workpiece_ratio_group_line'
    _description = '中查组别明细'
    _order = "name"


    middle_check_workpiece_ratio_id = fields.Many2one("middle_check_workpiece_ratio")
    name = fields.Char(string="组别名称")


    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        workpiece_ratio_group_line_obj = self.env["workpiece_ratio_group_line"].sudo().search([
            ("middle_check_workpiece_ratio_id", "=", vals["middle_check_workpiece_ratio_id"]),
            ("name", "=", vals["name"])
            ])
        if workpiece_ratio_group_line_obj:
            workpiece_ratio_group_line_obj.unlink()
            

        instance = super(WorkpieceRatioGroupLine, self).create(vals)
    
        return instance