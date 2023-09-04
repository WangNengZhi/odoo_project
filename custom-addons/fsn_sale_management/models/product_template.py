from odoo import fields, models, api
from odoo.exceptions import ValidationError



class IbDetail(models.Model):
    _inherit = "ib.detail"
    ''' 款号'''

    def set_new_create(self):
        for record in self:
            if not record.fsn_color:
                fsn_color_obj = self.env['fsn_color'].sudo().search([("name", "=", record.color)])
                if fsn_color_obj:
                    record.fsn_color = fsn_color_obj.id
    

    def create_product_template(self):
        for record in self:
            
            if not record.fsn_color:
                break
            
            product_template_obj = self.env['product.template'].sudo().search([
                ("style_number_base_id", "=", record.style_number_base_id.id),
                ("name", "=", record.style_number_base_id.name)
            ])

            if not product_template_obj:

                product_template_obj = self.env['product.template'].sudo().create({
                    "style_number_base_id": record.style_number_base_id.id,
                    "name": record.style_number_base_id.name,    # 产品名称
                    "purchase_ok": False,   # 可采购
                    "type": "product",  # 产品类型
                    "invoice_policy": "order",
                })

                # 创建尺码变体
                product_attribute_obj = self.env['product.attribute'].sudo().search([("name", "=", "尺码")])
                if product_attribute_obj:
                    product_template_obj.attribute_line_ids.sudo().create({
                        "product_tmpl_id": product_template_obj.id,
                        "attribute_id": product_attribute_obj.id,
                        "value_ids": [(6, 0, product_attribute_obj.value_ids.ids)]
                    })
                else:
                    raise ValidationError("销售模块没有设置尺码属性！")


            # 设置颜色变体
            attribute_line_obj = product_template_obj.attribute_line_ids.sudo().filtered(lambda x: x.attribute_id.name == "颜色")    # 查询产品变体明细
            if attribute_line_obj:

                product_attribute_obj = self.env['product.attribute'].sudo().search([("name", "=", "颜色")])    # 属性表
                if product_attribute_obj:

                    product_attribute_value_obj = self.env['product.attribute.value'].sudo().search([("name", "=", record.fsn_color.name)])
                    if not product_attribute_value_obj:
                        product_attribute_value_obj = self.env['product.attribute.value'].sudo().create({
                            "name": record.fsn_color.name,
                            "attribute_id": product_attribute_obj.id
                        })
                    attribute_line_obj.sudo().write({"value_ids": [(4, product_attribute_value_obj.id)]})

                else:
                    raise ValidationError("销售模块没有设置颜色属性！")

            else:

                product_attribute_obj = self.env['product.attribute'].sudo().search([("name", "=", "颜色")])

                if product_attribute_obj:

                    product_attribute_value_obj = self.env['product.attribute.value'].sudo().search([("name", "=", record.fsn_color.name)])
                    if not product_attribute_value_obj:
                        product_attribute_value_obj = self.env['product.attribute.value'].sudo().create({
                            "name": record.fsn_color.name,
                            "attribute_id": product_attribute_obj.id
                        })

                    product_template_obj.attribute_line_ids.sudo().create({
                        "product_tmpl_id": product_template_obj.id,
                        "attribute_id": product_attribute_obj.id,
                        "value_ids": [(4, product_attribute_value_obj.id)]
                    })

                else:
                    raise ValidationError("销售模块没有设置颜色属性！")





    @api.model
    def create(self, vals):

        res = super(IbDetail,self).create(vals)

        res.create_product_template()

        return res




    def write(self, vals):

        if "style_number" in vals:

            product_template_obj = self.env['product.template'].sudo().search([
                ("style_number_base_id", "=", self.style_number_base_id.id),
                ("name", "=", self.style_number_base_id.name)
            ])
            attribute_line_obj = product_template_obj.attribute_line_ids.sudo().filtered(lambda x: x.attribute_id.name == "颜色")
            product_attribute_value_obj = self.env['product.attribute.value'].sudo().search([("name", "=", self.fsn_color.name)])
            if product_attribute_value_obj:
                if len(attribute_line_obj.value_ids) == 1:
                    attribute_line_obj.sudo().unlink()
                else:
                    attribute_line_obj.sudo().write({"value_ids": [(3, product_attribute_value_obj.id)]})
    
        res = super(IbDetail, self).write(vals)

        if "style_number" in vals:
            self.sudo().create_product_template()

        return res
        

class ProductTemplate(models.Model):
    _inherit = "product.template"
    ''' 产品模板'''

    style_number_base_id = fields.Many2one("style_number_base", string="款号前缀（产品编码）", ondelete='cascade')




