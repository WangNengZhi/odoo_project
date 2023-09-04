from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MaterialCode(models.Model):
    _name = 'material_code'
    _description = '物料编码'


    name = fields.Char(string="物料编码")
    date = fields.Datetime(string="时间")
    type = fields.Selection([('面料', '面料'), ('物料', '物料'), ('待采购', '待采购'), ('已采购', '已采购')], string='类型')
    material_name = fields.Char(string="物品名称", compute="_value_info", store=True)
    procurement_date = fields.Date(string="采购日期", compute="_value_info", store=True)
    procurement_id = fields.Many2one("fabric_ingredients_procurement", string="采购记录")

    @api.depends('procurement_id')
    def _value_info(self):
        for record in self:
            if record.procurement_id:
                record.material_name = record.procurement_id.material_name
                record.procurement_date = record.procurement_id.date


    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('material_code')

        return super(MaterialCode,self).create(vals)