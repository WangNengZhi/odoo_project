from odoo import models, fields, api

class OutsourcePlant(models.Model):
    _name = 'outsource_plant'
    _description = 'FSN外发工厂'
    _rec_name = 'name'
    # _order = "date desc"


    name = fields.Char(string="工厂名称", required=True)
    plant_type = fields.Many2many("outsource_plant_process_type", string="加工厂类型", required=True)
    plant_boss_name = fields.Char(string="工厂老板姓名", required=True)
    plant_boss_phone = fields.Char(string="工厂老板电话", required=True)
    plant_head_name = fields.Char(string="工厂主管姓名")
    plant_head_phone = fields.Char(string="工厂主管电话")
    plant_address = fields.Text(string="工厂地址", required=True)
    plant_area = fields.Float(string="工厂占地面积(平方米)", required=True)
    open_account_bank = fields.Char(string="开户行", required=True)
    bank_card_number = fields.Char(string="银行卡号", required=True)
    rating = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')
    ], string='评级', default="10", required=True)

    resources_line = fields.One2many("outsource_resources_plant", "plant_id", string="资源明细")

    fsn_customer_id = fields.Many2one("fsn_customer", string="客户", ondelete='restrict')







    def write(self, vals):

        res = super(OutsourcePlant, self).write(vals)

        if "name" in vals:
            self.sudo().fsn_customer_id.name = self.name

        return res


    def create_fsn_customer(self):
        for record in self:
            fsn_customer_obj = self.env['fsn_customer'].sudo().search([("name", "=", record.name)])
            if not fsn_customer_obj:
                fsn_customer_obj = self.env['fsn_customer'].sudo().create({"name": record.name, "type": "外部", "customer_type": "公司"})

            record.fsn_customer_id = fsn_customer_obj.id


    @api.model
    def create(self, vals):

        res = super(OutsourcePlant,self).create(vals)

        res.create_fsn_customer()

        return res



class OutsourceResourcesPlant(models.Model):
    _name = 'outsource_resources_plant'
    _description = 'FSN外发工厂资源明细'

    plant_id = fields.Many2one("outsource_plant", string="工厂", ondelete='cascade')
    resources = fields.Many2one("outsource_plant_resources_type", string="资源")
    number = fields.Integer(string="数量")
    unit = fields.Char(string="单位", related="resources.unit", store=True)


