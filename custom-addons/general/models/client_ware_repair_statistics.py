from odoo import models, fields, api


class ClientWare(models.Model):
    """ 继承客仓"""
    _inherit = 'client_ware'


    client_ware_repair_statistics_id = fields.Many2one("client_ware_repair_statistics", string="客仓返修统计", compute="set_client_ware_repair_statistics_id", store=True)

    @api.depends('client_or_QC', 'dDate', 'gGroup', 'style_number')
    def set_client_ware_repair_statistics_id(self):
        for record in self:
            if record.client_or_QC:
                client_ware_repair_statistics_obj = self.env["client_ware_repair_statistics"].sudo().search([
                    ("date", "=", record.dDate),
                    ("group", "=", record.gGroup),
                    ("quality_inspector", "=", record.client_or_QC),
                    ("style_number", "=", record.style_number.id)
                ])
                if not client_ware_repair_statistics_obj:

                    client_ware_repair_statistics_obj = self.env["client_ware_repair_statistics"].sudo().create({
                        "date": record.dDate,
                        "group": record.gGroup,
                        "quality_inspector": record.client_or_QC,
                        "style_number": record.style_number.id
                    })
                before_client_ware_repair_statistics_obj = record.client_ware_repair_statistics_id
                
                record.client_ware_repair_statistics_id = client_ware_repair_statistics_obj.id

                before_client_ware_repair_statistics_obj.set_client_ware_ids_info()


    # @api.model
    # def create(self, vals):

    #     res = super(ClientWare, self).create(vals)

    #     res.sudo().set_client_ware_repair_statistics_id()

    #     return res




class ClientWareRepairStatistics(models.Model):
    _name = 'client_ware_repair_statistics'
    _description = '客仓返修统计'
    _rec_name = 'style_number'
    _order = "date desc"

    date = fields.Date(string="日期")
    group = fields.Char(string="组别")
    style_number = fields.Many2one('ib.detail', string='款号')
    quality_inspector = fields.Char(string="尾查")


    client_ware_ids = fields.One2many("client_ware", "client_ware_repair_statistics_id", string="客仓")
    repair_quantity = fields.Integer(string="返修数量", compute="set_client_ware_ids_info", store=True)
    check_quantity = fields.Integer(string="查货数量", compute="set_client_ware_ids_info", store=True)
    @api.depends('client_ware_ids', 'client_ware_ids.repair_number', 'client_ware_ids.check_number')
    def set_client_ware_ids_info(self):
        for record in self:
            record.repair_quantity = sum(record.client_ware_ids.mapped('repair_number'))
            record.check_quantity = sum(record.client_ware_ids.mapped('check_number'))

    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')

    @api.depends('repair_quantity', 'check_quantity')
    def set_repair_ratio(self):
        for record in self:
            if record.check_quantity:
                # 返修率
                record.repair_ratio = (record.repair_quantity / record.check_quantity) * 100
            else:
                record.repair_ratio = 0



