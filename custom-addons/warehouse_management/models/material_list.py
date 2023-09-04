from telnetlib import PRAGMA_HEARTBEAT
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MaterialList(models.Model):
    _name = 'material_list'
    _description = '物料清单'
    _rec_name = 'material_code'
    _order = "create_date desc"

    procurement_id = fields.Many2one("fabric_ingredients_procurement", string="采购清单", domain=[('state', '=', '待采购'), ("type", "!=", "面料")])
    material_code = fields.Many2one("material_code", string="物料编码")
    use_type = fields.Selection([('用料', '用料'), ('储备用料', '储备用料')], string="物料类型")
    @api.onchange('procurement_id')
    def set_material_code(self):
        for record in self:
            if record.procurement_id:

                record.material_code = record.procurement_id.material_code.id
                record.order_id = record.procurement_id.order_id.id
                record.style_number = record.procurement_id.style_number.id
                record.material_name = record.procurement_id.material_name
                record.supplier = record.procurement_id.supplier_supplier_id.supplier_name
                record.specification = record.procurement_id.specification
                record.unit = record.procurement_id.unit
                record.unit_price = record.procurement_id.unit_price
                record.use_type = record.procurement_id.use_type
            else:
                record.material_code = False
                record.order_id = False
                record.style_number = False
                record.material_name = False
                record.supplier = False
                record.specification = False
                record.unit = False
                record.unit_price = False
                record.use_type = False

    material_coding = fields.Char(string="物料编码（旧）")
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    supplier = fields.Char(string="供应商")
    client = fields.Char(string="客户(旧)", related="order_id.name", store=True)

    client_id = fields.Many2one("fsn_customer", string="客户", related="order_id.customer_id", store=True)


    material_name = fields.Char(string="物料名称", required=True)
    specification = fields.Char(string="规格")
    color = fields.Char(string="颜色")
    unit = fields.Char(string="单位")
    unit_price = fields.Float(string="单价", digits=(16, 5))
    remark = fields.Char(string="备注")



    @api.constrains('material_code')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([('material_code', '=', self.material_code.id)])
        if len(demo) > 1:
            raise ValidationError(f"物料编码为{self.material_code.name}的记录已经存在了！不可重复创建。")



    # 生成物料编码
    def generate_material_code(self):
        for record in self:

            if record.material_code:
                raise ValidationError(f"已经存在物料编码！不可生成！")
            else:
                material_code_obj = self.material_code.sudo().create({
                    "date": fields.datetime.now(),
                })
                record.material_code = material_code_obj.id






    @api.model
    def create(self, vals):

        if vals["material_code"] == False:

            material_code_obj = self.material_code.sudo().create({
                "date": fields.datetime.now(),
                "type": "物料"
            })

            vals["material_code"] = material_code_obj.id
        
        else:
            material_code_obj = self.env["material_code"].sudo().browse(vals["material_code"])
            material_code_obj.type = "已采购"

        return super(MaterialList,self).create(vals)



    def unlink(self):

        for record in self:

            fip_obj = self.env["fabric_ingredients_procurement"].sudo().search([("material_code", "=", record.material_code.id)])
            if fip_obj:
                record.material_code.type = "待采购"
            else:
                record.material_code.sudo().unlink()

        res = super(MaterialList, self).unlink()

        return res





