from odoo import models, fields, api
import calendar, datetime


class AlwaysCheckOmission(models.Model):
    _name = 'always_check_omission'
    _description = '总检漏查(日)'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")

    group_line_ids = fields.One2many("aco_group_line", "always_check_omission_id", string="组别")
    style_number_line_ids = fields.One2many("aco_style_number_line", "always_check_omission_id", string="款号")

    always_check_principal = fields.Char(string="总检")

    repair_quantity = fields.Float(string="客仓当日返修数量")
    # day_check_quantity = fields.Float(string="客仓当日查货数量")
    # day_repair_ratio = fields.Float(string="客仓当日返修率", group_operator='avg')

    repair_value_sum = fields.Float(string="客仓总返修数")
    check_quantity = fields.Float(string="总检总查货数量")

    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    assess_index = fields.Float(string="考核", compute="set_repair_ratio", store=True)



    # 设置返修率
    @api.depends('repair_quantity', 'repair_value_sum', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity and record.repair_value_sum and record.repair_quantity:
                # 返修率
                record.repair_ratio = (record.repair_value_sum / record.check_quantity) * 100

                if record.repair_value_sum > (record.check_quantity * 0.03):

                    record.assess_index = record.repair_quantity * 5
                else:
                    record.assess_index = 0

            else:

                record.repair_ratio = 0
                record.assess_index = 0


    # 设置总检漏查表数据
    def set_date(self):
        for record in self:

            record.group_line_ids.sudo().unlink()
            record.style_number_line_ids.sudo().unlink()

            client_ware_objs = self.env["client_ware"].sudo().search([
                ("dDate", "=", record.dDate),
                ("general", "=", record.always_check_principal)
            ])


            for client_ware_obj in client_ware_objs:

                # 创建组明细
                aco_group_line_obj = record.group_line_ids.sudo().search([
                    ("always_check_omission_id", "=", record.id),
                    ("name", "=", client_ware_obj.gGroup),
                ])
                if not aco_group_line_obj:
                    record.group_line_ids.sudo().create({
                        "always_check_omission_id": record.id,
                        "name": client_ware_obj.gGroup
                    })

                # 创建款号明细
                aco_style_number_line_obj = record.style_number_line_ids.sudo().search([
                    ("always_check_omission_id", "=", record.id),
                    ("name", "=", client_ware_obj.style_number.id),
                ])
                if not aco_style_number_line_obj:
                    record.style_number_line_ids.sudo().create({
                        "always_check_omission_id": record.id,
                        "name": client_ware_obj.style_number.id
                    })


            # 临时查货数量
            tem_check_quantity = 0
            # 临时当日查货数
            # tem_day_check_quantity = 0
            # 临时返修件数
            tem_repair_value = 0
            # 临时返修总数
            tem_repair_value_sum = 0

            for style_number_obj in record.style_number_line_ids:

                client_ware_objs = self.env["client_ware"].sudo().search([
                    ("style_number", "=", style_number_obj.name.id),
                    ("general", "=", record.always_check_principal),
                    ("dDate", "<=", record.dDate),
                ])

                for client_ware_obj in client_ware_objs:

                    tem_repair_value_sum = tem_repair_value_sum + client_ware_obj.repair_number
                    if client_ware_obj.dDate == record.dDate:
                        tem_repair_value = tem_repair_value + client_ware_obj.repair_number
                        # tem_day_check_quantity = tem_day_check_quantity + client_ware_obj.check_number



                tem_general_general_objs = self.env["general.general"].sudo().search([
                    ("item_no", "=", style_number_obj.name.id),
                    ("general1", "=", record.always_check_principal),
                    ("date", "<=", record.dDate)
                ])
                for tem_obj in tem_general_general_objs:
                    tem_check_quantity = tem_check_quantity + tem_obj.general_number

            record.repair_quantity = tem_repair_value

            record.repair_value_sum = tem_repair_value_sum

            record.check_quantity = tem_check_quantity










# # 组别去重
# tem_group_line_ids = [(a,b,c['name']) for a, b, c in tem_group_line_ids]
# tem_group_line_ids = set(tem_group_line_ids)
# tem_group_line_ids = [(a,b,{'name':c}) for a,b,c in tem_group_line_ids]

# # 款号去重
# tem_style_number_line_ids = [(a,b,c['name']) for a, b, c in tem_style_number_line_ids]
# tem_style_number_line_ids = set(tem_style_number_line_ids)
# tem_style_number_line_ids = [(a,b,{'name':c}) for a,b,c in tem_style_number_line_ids]

# record.group_line_ids = tem_group_line_ids
# record.style_number_line_ids = tem_style_number_line_ids




class AlwaysCheckOmissionGroupLine(models.Model):
    _name = 'aco_group_line'
    _description = '总检漏查组别明细'
    _order = "name"


    always_check_omission_id = fields.Many2one("always_check_omission", ondelete="cascade")
    name = fields.Char(string="组名")



class AlwaysCheckOmissionStyleNumberLine(models.Model):

    _name = 'aco_style_number_line'
    _description = '总检漏查款号明细'
    _order = "name"

    always_check_omission_id = fields.Many2one("always_check_omission", ondelete="cascade")
    name = fields.Many2one("ib.detail", string="款号")

