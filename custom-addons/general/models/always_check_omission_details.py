from odoo import models, fields, api
from odoo.exceptions import ValidationError



class GeneralGeneral(models.Model):
    '''总检'''
    _inherit = 'general.general'



    def set_always_check_omission_details_id(self):

        for record in self:

            always_check_omission_details_objs = self.env["always_check_omission_details"].sudo().search([
                ("dDate", ">=", record.date),
                ("group", "=", record.group),
                ("style_number_id", "=", record.item_no.id),
                ("always_check_principal", "=", record.general1)
            ])
            if always_check_omission_details_objs and always_check_omission_details_objs.filtered(lambda x: x.dDate == record.date):
                pass

            else:
                today_record = always_check_omission_details_objs.sudo().create({
                    "dDate": record.date,
                    "group": record.group,
                    "style_number_id": record.item_no.id,
                    "always_check_principal": record.general1
                })
                always_check_omission_details_objs = list(always_check_omission_details_objs)
                always_check_omission_details_objs.append(today_record)

            for obj in always_check_omission_details_objs:
                obj.sudo().set_general_general_line_ids()
                obj.sudo().set_client_ware_line_ids()

    @api.model
    def create(self, vals):

        res = super(GeneralGeneral, self).create(vals)

        res.sudo().set_always_check_omission_details_id()

        return res



    def unlink(self):

        always_check_omission_details_obj_list = []
        for record in self:
            always_check_omission_details_obj = self.env["always_check_omission_details"].sudo().search([
                ("dDate", "=", record.date),
                ("group", "=", record.group),
                ("style_number_id", "=", record.item_no.id),
                ("always_check_principal", "=", record.general1)
            ])

            always_check_omission_details_obj_list.append(always_check_omission_details_obj)

        res = super(GeneralGeneral, self).unlink()


        for obj in always_check_omission_details_obj_list:
            obj.sudo().set_general_general_info()

        return res



class ClientWare(models.Model):
    '''客仓'''
    _inherit = 'client_ware'


    def set_always_check_omission_details_id(self):
        for record in self:
        
            always_check_omission_details_objs = self.env["always_check_omission_details"].sudo().search([
                ("dDate", ">=", record.dDate),
                ("group", "=", record.gGroup),
                ("style_number_id", "=", record.style_number.id),
                ("always_check_principal", "=", record.general)
            ])
            if always_check_omission_details_objs and always_check_omission_details_objs.filtered(lambda x: x.dDate == record.dDate):
                pass

            else:
                today_record = always_check_omission_details_objs.sudo().create({
                    "dDate": record.dDate,
                    "group": record.gGroup,
                    "style_number_id": record.style_number.id,
                    "always_check_principal": record.general
                })

                always_check_omission_details_objs = list(always_check_omission_details_objs)
                always_check_omission_details_objs.append(today_record)

            for obj in always_check_omission_details_objs:
                obj.sudo().set_client_ware_line_ids()
                obj.sudo().set_general_general_line_ids()


    def del_on_rec(self):
        for record in self:
            always_check_omission_details_objs = self.env["always_check_omission_details"].sudo().search([
                ("dDate", ">=", record.dDate),
                ("group", "=", record.gGroup),
                ("style_number_id", "=", record.style_number.id),
                ("always_check_principal", "=", record.general)
            ])
            always_check_omission_details_objs.sudo().unlink()


    @api.model
    def create(self, vals):

        res = super(ClientWare, self).create(vals)

        res.sudo().set_always_check_omission_details_id()

        return res

    def write(self, vals):
        self.sudo().del_on_rec()

        res = super(ClientWare, self).write(vals)

        self.sudo().set_always_check_omission_details_id()

        return res


    def unlink(self):

        always_check_omission_details_obj_list = []

        for record in self:

            always_check_omission_details_obj = self.env["always_check_omission_details"].sudo().search([
                ("dDate", "=", record.dDate),
                ("group", "=", record.gGroup),
                ("style_number_id", "=", record.style_number.id),
                ("always_check_principal", "=", record.general)
            ])
            always_check_omission_details_obj_list.append(always_check_omission_details_obj)

        res = super(ClientWare, self).unlink()


        for obj in always_check_omission_details_obj_list:
            obj.sudo().set_client_ware_info()

        return res






class AlwaysCheckOmissionDetails(models.Model):
    _name = 'always_check_omission_details'
    _description = '总检漏查(详情)'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")

    group = fields.Char(string="组别")

    style_number_id = fields.Many2one('ib.detail', string='款号')

    always_check_principal = fields.Char(string="总检")



    general_general_line_ids = fields.Many2many("general.general", string="总检")
    def set_general_general_line_ids(self):
        for record in self:
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "<=", record.dDate),
                ("group", "=", record.group),
                ("item_no", "=", record.style_number_id.id),
                ("general1", "=", record.always_check_principal)
            ])
            record.general_general_line_ids = [(6, 0, general_general_objs.ids)]
    day_check_quantity = fields.Float(string="总检当日查货数量", compute="set_general_general_info", store=True)
    check_quantity = fields.Float(string="总检总查货数量", compute="set_general_general_info", store=True)
    @api.depends("general_general_line_ids")
    def set_general_general_info(self):
        for record in self:

            record.day_check_quantity = sum(record.general_general_line_ids.filtered(lambda x: x.date == record.dDate).mapped('general_number'))
            record.check_quantity = sum(record.general_general_line_ids.mapped('general_number'))



    client_ware_line_ids = fields.Many2many("client_ware", string="客仓")
    def set_client_ware_line_ids(self):
        for record in self:
            client_ware_objs = self.env["client_ware"].sudo().search([
                ("dDate", "<=", record.dDate),
                ("gGroup", "=", record.group),
                ("style_number", "=", record.style_number_id.id),
                ("general", "=", record.always_check_principal)
            ])
            record.client_ware_line_ids = [(6, 0, client_ware_objs.ids)]

    repair_quantity = fields.Float(string="客仓当日返修数量", compute="set_client_ware_info", store=True)
    repair_value_sum = fields.Float(string="客仓总返修数", compute="set_client_ware_info", store=True)
    @api.depends("client_ware_line_ids")
    def set_client_ware_info(self):
        for record in self:
            record.repair_quantity = sum(record.client_ware_line_ids.filtered(lambda x: x.dDate == record.dDate).mapped('repair_number'))
            record.repair_value_sum = sum(record.client_ware_line_ids.mapped('repair_number'))

            






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