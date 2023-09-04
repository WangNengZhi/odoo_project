
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar, datetime

class GeneralGeneral(models.Model):
    '''总检'''
    _inherit = 'general.general'

    always_check_omission_details_month_id = fields.Many2one("always_check_omission_details_month", string="总检漏查表(月)")


class ClientWare(models.Model):
    '''客仓'''
    _inherit = 'client_ware'


    def set_always_check_omission_details_month(self):
        for record in self:
            if record.general:
                # 获取年
                month = record.dDate.month
                # 获取月
                year = record.dDate.year
                year_month = f"{year}-{month}"
                obj = self.env['always_check_omission_details_month'].sudo().search([
                    ("month", "=", year_month),
                    ("style_number_id", "=", record.style_number.id),
                    ("always_check_principal", "=", record.general)
                ])
                if not obj:
                    obj = self.env['always_check_omission_details_month'].sudo().create({
                        "month": year_month,
                        "style_number_id": record.style_number.id,
                        "always_check_principal": record.general
                    })
                
                obj.sudo().set_client_ware_ids()
                obj.sudo().set_general_ids()

    @api.model
    def create(self, vals):

        res = super(ClientWare, self).create(vals)

        res.sudo().set_always_check_omission_details_month()

        return res

    def write(self, vals):

        res = super(ClientWare, self).write(vals)

        self.sudo().set_always_check_omission_details_month()

        return res


class AlwaysCheckOmissionDetailsMonth(models.Model):
    _name = 'always_check_omission_details_month'
    _description = '总检漏查表(月)'
    _rec_name = 'month'
    _order = "month desc"



    month = fields.Char(string="月份")
    style_number_id = fields.Many2one('ib.detail', string='款号')
    always_check_principal = fields.Char(string="总检")
    client_ware_ids = fields.Many2many("client_ware", string="客仓")
    def set_client_ware_ids(self):
        for record in self:
            start, end = record.compute_start_and_end()
            client_ware_objs = self.env["client_ware"].sudo().search([
                ("dDate", "<=", end),
                ("dDate", ">=", start),
                ("style_number", "=", record.style_number_id.id),
                ("general", "=", record.always_check_principal)
            ])
            record.client_ware_ids = [(6, 0, client_ware_objs.ids)]
    repair_quantity = fields.Float(string="返修数量", compute="set_repair_quantity", store=True)
    @api.depends('client_ware_ids', 'client_ware_ids.repair_number')
    def set_repair_quantity(self):
        for record in self:
            record.repair_quantity = sum(record.client_ware_ids.mapped("repair_number"))
    general_ids = fields.One2many("general.general", "always_check_omission_details_month_id", string="总检")
    def set_general_ids(self):
        for record in self:
            start, end = record.compute_start_and_end()
            general_objs = self.env['general.general'].sudo().search([
                ("date", "<=", end),
                ("date", ">=", start),
                ("item_no", "=", record.style_number_id.id),
                ("general1", "=", record.always_check_principal)
            ])
            record.general_ids = [(6, 0, general_objs.ids)]
    check_quantity = fields.Float(string="查货数量", compute="set_check_quantity", store=True)
    @api.depends('general_ids', 'general_ids.general_number')
    def set_check_quantity(self):
        for record in self:
            record.check_quantity = sum(record.general_ids.mapped("general_number"))
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

            return start, end