from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductionOperation_ingredients_list(models.Model):
    _name = 'production_operation_ingredients_list'
    _description = '生产工具清单'
    _rec_name = 'material_coding'
    _order = "create_date desc"


    material_coding = fields.Char(string="物品编码", required=True)
    material_name = fields.Char(string="物品名称", required=True)
    # supplier_supplier_id = fields.Char(string="222")
    specification = fields.Char(string="规格")
    unit = fields.Char(string="单位")
    unit_price = fields.Float(string="单价", digits=(16, 5))
    remark = fields.Char(string="备注")


    @api.constrains('material_coding')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([('material_coding', '=', self.material_coding)])
        if len(demo) > 1:
            raise ValidationError(f"物料编码为{self.material_coding}的记录已经存在了！不可重复创建。")


    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.material_coding, record.material_name)   #例：%s (%s) = 数学 (2021-02-11)
            result.append((record.id, rec_name))
        return result
