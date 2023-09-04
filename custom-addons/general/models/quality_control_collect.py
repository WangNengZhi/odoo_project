from odoo import models, fields, api
from odoo.exceptions import ValidationError

class QualityControlCollect(models.Model):
    _name = 'quality_control_collect'
    _description = '品控汇总'
    _rec_name = 'style_number'
    _order = "date desc"



    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    style_number = fields.Many2one('ib.detail', string='款号')

    date = fields.Date(string="日期", compute="set_date", store=True)
    @api.depends("order_number", "order_number.date")
    def set_date(self):
        for record in self:
            if record.order_number:
                record.date = record.order_number.date

    invest_invest_ids = fields.One2many("invest.invest", "quality_control_collect_id", string="中查")
    middle_repair_number = fields.Integer(string="中查返修数", compute="set_middle_info", store=True)
    middle_check_number = fields.Integer(string="中查查货数", compute="set_middle_info", store=True)
    @api.depends("invest_invest_ids", "invest_invest_ids.repairs_number", "invest_invest_ids.check_the_quantity")
    def set_middle_info(self):
        for record in self:
            record.middle_repair_number = sum(record.invest_invest_ids.mapped("repairs_number"))
            record.middle_check_number = sum(record.invest_invest_ids.mapped("check_the_quantity"))
            

    general_general_ids = fields.One2many("general.general", "quality_control_collect_id", string="总检")
    general_repair_number = fields.Integer(string="总检返修数", compute="set_general_info", store=True)
    general_check_number = fields.Integer(string="总检查货数", compute="set_general_info", store=True)
    @api.depends("general_general_ids", "general_general_ids.repair_number", "general_general_ids.general_number")
    def set_general_info(self):
        for record in self:
            record.general_repair_number = sum(record.general_general_ids.mapped("repair_number"))
            record.general_check_number = sum(record.general_general_ids.mapped("general_number"))

    client_ware_ids = fields.One2many("client_ware", "quality_control_collect_id", string="客仓")
    client_ware_repair_number = fields.Integer(string="客仓返修数", compute="set_client_ware_info", store=True)
    client_ware_check_number = fields.Integer(string="客仓查货数", compute="set_client_ware_info", store=True)
    @api.depends("client_ware_ids", "client_ware_ids.repair_number", "client_ware_ids.check_number")
    def set_client_ware_info(self):
        for record in self:
            record.client_ware_repair_number = sum(record.client_ware_ids.mapped("repair_number"))
            record.client_ware_check_number = sum(record.client_ware_ids.mapped("check_number"))


    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "quality_control_collect_id", string="仓库明细")
    warehouse_defective_number = fields.Integer(string="仓库次品入库数", compute="set_warehouse_defective_info", store=True)

    @api.depends("finished_product_ware_line_ids", "finished_product_ware_line_ids.state", "finished_product_ware_line_ids.number", "finished_product_ware_line_ids.type", "finished_product_ware_line_ids.quality")
    def set_warehouse_defective_info(self):
        for record in self:
            record.warehouse_defective_number = sum(record.finished_product_ware_line_ids.filtered(lambda x: x.state == "确认" and x.type == "入库" and x.quality == "次品").mapped('number'))





    # 检查数据唯一性
    @api.constrains('order_number', 'style_number')
    def _check_unique(self):

        objs_count = self.env[self._name].sudo().search_count([
            ('order_number', '=', self.order_number.id),
            ('style_number', '=', self.style_number.id),
        ])
        if objs_count > 1:
            raise ValidationError("已经存在相同订单号和款号的“品控汇总”记录了！")


class Invest(models.Model):
    """ 继承中查"""
    _inherit = 'invest.invest'
    

    quality_control_collect_id = fields.Many2one("quality_control_collect", string="品控汇总")


    def set_quality_control_collect(self):

        for record in self:

            quality_control_collect_obj = self.env["quality_control_collect"].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id)
            ])
            if not quality_control_collect_obj:
                quality_control_collect_obj = self.env["quality_control_collect"].sudo().create({
                    "order_number": record.order_number.id,
                    "style_number": record.style_number.id
                })

            record.quality_control_collect_id = quality_control_collect_obj.id


    @api.model
    def create(self, vals):

        res = super(Invest,self).create(vals)

        res.set_quality_control_collect()

        return res

class General(models.Model):
    """ 继承总检"""
    _inherit = 'general.general'


    quality_control_collect_id = fields.Many2one("quality_control_collect", string="品控汇总")


    def set_quality_control_collect(self):

        for record in self:

            quality_control_collect_obj = self.env["quality_control_collect"].sudo().search([
                ("order_number", "=", record.order_number_id.id),
                ("style_number", "=", record.item_no.id)
            ])
            if not quality_control_collect_obj:
                quality_control_collect_obj = self.env["quality_control_collect"].sudo().create({
                    "order_number": record.order_number_id.id,
                    "style_number": record.item_no.id
                })
            

            record.quality_control_collect_id = quality_control_collect_obj.id


    @api.model
    def create(self, vals):

        res = super(General,self).create(vals)

        res.set_quality_control_collect()

        return res


class ClientWare(models.Model):
    """ 继承客仓"""
    _inherit = 'client_ware'


    quality_control_collect_id = fields.Many2one("quality_control_collect", string="品控汇总")


    def set_quality_control_collect(self):
        if self.order_number and self.style_number:

            quality_control_collect_obj = self.env["quality_control_collect"].sudo().search([
                ("order_number", "=", self.order_number.id),
                ("style_number", "=", self.style_number.id)
            ])
            if not quality_control_collect_obj:
                quality_control_collect_obj = self.env["quality_control_collect"].sudo().create({
                    "order_number": self.order_number.id,
                    "style_number": self.style_number.id
                })

            self.quality_control_collect_id = quality_control_collect_obj.id

    def write(self, vals):

        res = super(ClientWare, self).write(vals)

        if not ("quality_control_collect_id" in vals and len(vals) == 1):

            self.set_quality_control_collect()

        return res



    @api.model
    def create(self, vals):

        res = super(ClientWare,self).create(vals)

        res.set_quality_control_collect()

        return res


class FinishedProductWareLine(models.Model):
    """ 继承仓库明细"""
    _inherit = 'finished_product_ware_line'


    quality_control_collect_id = fields.Many2one("quality_control_collect", string="品控汇总")

    def set_quality_control_collect(self):

        for record in self:

            quality_control_collect_obj = self.env["quality_control_collect"].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id)
            ])
            if not quality_control_collect_obj:
                quality_control_collect_obj = self.env["quality_control_collect"].sudo().create({
                    "order_number": record.order_number.id,
                    "style_number": record.style_number.id
                })

            record.quality_control_collect_id = quality_control_collect_obj.id



    @api.model
    def create(self, vals):

        res = super(FinishedProductWareLine,self).create(vals)

        res.set_quality_control_collect()

        return res



    