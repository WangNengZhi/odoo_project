
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FinishedProductWareLine(models.Model):
    """ 继承仓库明细"""
    _inherit = 'finished_product_ware_line'



    def set_client_ware_general(self):

        client_ware_objs = self.env['client_ware'].sudo().search([
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("check_type", "!=", "客户"),
        ])
        if client_ware_objs:
            return " ".join(set(client_ware_objs.mapped("client_or_QC")))
        
        else:

            general_objs = self.env['general.general'].sudo().search([("order_number_id", "=", self.order_number.id), ("item_no", "=", self.style_number.id)])
            return " ".join(set(general_objs.mapped("general1")))
        

    def set_client_ware_id(self):


        client_ware_objs = self.env["client_ware"].sudo().search([
            ("dDate", "=", self.date),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id)
        ])

        check_number_objs = self.sudo().search([
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("type", "=", "入库"),
            ("character", "=", "正常"),
            ("state", "=", "确认")
        ])
        repair_number_objs = self.sudo().search([
            ("date", "=", self.date),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("type", "=", "入库"),
            ("quality", "=", "次品"),
            ("state", "=", "确认")
        ])
        if client_ware_objs:
            client_ware_objs.check_number = sum(check_number_objs.mapped("number"))
            client_ware_objs.repair_number = sum(repair_number_objs.mapped("number"))
            client_ware_objs.general = self.set_client_ware_general()
        else:
            if self.order_number.production_group_ids:


                self.env["client_ware"].sudo().create({
                    "dDate": self.date,
                    "gGroup": self.order_number.production_group_ids[0].name,
                    "order_number": self.order_number.id,
                    "style_number": self.style_number.id,
                    "client_or_QC": self.finished_product_ware_id.customer_id.name,
                    "repair_number": sum(repair_number_objs.mapped("number")),
                    "check_number": sum(check_number_objs.mapped("number")),
                    "check_type": "客户",
                    "general": self.set_client_ware_general()
                })
            else:
                raise ValidationError(f"销售订单上未填写生产组别！")

    def rollback_client_ware_id(self):

        client_ware_objs = self.env["client_ware"].sudo().search([
            ("dDate", "=", self.date),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id)
        ])
        check_number_objs = self.sudo().search([
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("type", "=", "入库"),
            ("character", "=", "正常"),
            ("state", "=", "确认")
        ])
        repair_number_objs = self.sudo().search([
            ("date", "=", self.date),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("type", "=", "入库"),
            ("quality", "=", "次品"),
            ("state", "=", "确认")
        ])
        if client_ware_objs:
            client_ware_objs.check_number = sum(check_number_objs.mapped("number"))
            client_ware_objs.repair_number = sum(repair_number_objs.mapped("number"))
        




    def set_state(self):

        for rec in self:

            res = super(FinishedProductWareLine, rec).set_state()

            if rec.quality == "次品" and rec.type == "入库":
                
                if rec.state == "确认":
                    rec.set_client_ware_id()
                elif rec.state == "草稿":
                    rec.rollback_client_ware_id()

        return res





class ClientWare(models.Model):
    _name = 'client_ware'
    _description = '客仓'
    _rec_name = 'dDate'
    _order = "dDate desc"


    dDate = fields.Date(string="日期", required=True)
    gGroup = fields.Char('组别')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('style_number', 'order_number')
    def set_order_number_domain(self):

        sale_pro_line_objs = self.env["sale_pro_line"].sudo().search([("style_number", "=", self.style_number.id)])

        return {'domain': {'order_number': [('id', 'in', sale_pro_line_objs.sale_pro_id.ids)]}}


    client_or_QC = fields.Char(string="客户/QC")
    check_type = fields.Selection([
        ('客户', '客户'),
        ('QC', 'QC'),
        ('尾查', '尾查'),
        ('仓库', '仓库'),
        ('现场返修', '现场返修'),
        ],string="检查类型", required=True)
    repair_number = fields.Integer(string='返修数量')
    check_number = fields.Integer(string="查货数量")
    def refresh_check_number(self):
        for record in self:
            objs = self.env['finished_product_ware_line'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("type", "=", "入库"),
                ("quality", "=", "合格"),
                ("state", "=", "确认")
            ])
            record.check_number = sum(objs.mapped("number"))

    general = fields.Char(string='总检')
    repair_ratio = fields.Float(string="返修率", compute="set_repair_ratio", store=True, group_operator='avg')
    # 设置返修率
    @api.depends('repair_number', 'check_number')
    def set_repair_ratio(self):
        for record in self:
            if record.check_number:

                record.repair_ratio = (record.repair_number / record.check_number) * 100

            else:
                record.repair_ratio = 0
    remark = fields.Char(string="问题点")


    punishment = fields.Float(string="扣款", compute="set_punishment", store=True)
    @api.depends('repair_number', 'client_or_QC', "check_type")
    def set_punishment(self):
        for record in self:
            if record.check_type == "客户":
                record.punishment = record.repair_number * 5
            else:
                record.punishment = record.repair_number * 3





    # 设置总检漏查表
    def set_always_check_omission(self):
        for record in self:
            always_check_omission_obj = self.env["always_check_omission"].sudo().search([
                ("dDate", "=", record.dDate),
                ("always_check_principal", "=", record.general)
            ])
            if always_check_omission_obj:
                always_check_omission_obj.sudo().set_date()
            else:
                new_obj = always_check_omission_obj.sudo().create({
                    "dDate": record.dDate,
                    "always_check_principal": record.general
                })
                new_obj.sudo().set_date()


    def del_on_always_check_omission(self):
        for record in self:
            always_check_omission_objs = self.env["always_check_omission"].sudo().search([
                ("dDate", "=", record.dDate),
                ("always_check_principal", "=", record.general)
            ])
            always_check_omission_objs.sudo().unlink()


    def write(self, vals):

        self.sudo().del_on_always_check_omission()

        res = super(ClientWare, self).write(vals)

        self.set_always_check_omission()

        return res


    @api.model
    def create(self, vals):

        instance = super(ClientWare, self).create(vals)

        # 设置总检漏查表
        instance.set_always_check_omission()

        return instance


    # 删除时,设置总检漏查表
    def unlink_set_always_check_omission(self, tem_dDate, tem_always_check_principal):

        always_check_omission_objs = self.env["always_check_omission"].sudo().search([
            ("dDate", "=", tem_dDate),
            ("always_check_principal", "=", tem_always_check_principal)
        ])
        if always_check_omission_objs:
            always_check_omission_objs.sudo().set_date()



    def unlink(self):

        for record in self:

            tem_dDate = record.dDate  # 日期
            tem_always_check_principal = record.general   # 总检负责人

            super(ClientWare, record).unlink()

            # 删除时,设置总检漏查表
            record.unlink_set_always_check_omission(tem_dDate, tem_always_check_principal)

        res = super(ClientWare, self).unlink()

        return res

