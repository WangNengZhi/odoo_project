from odoo import models, fields, api




class GoodsInfo(models.Model):
    _name = 'goods_info'
    _description = '商品信息'
    _rec_name = 'name'
    _order = "create_date desc"

    name = fields.Char(string="商品名称")
    style_number = fields.Many2one('ib.detail', string='款号')
    product_barcode = fields.Char(string="产品编码", compute="set_product_barcode", store=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色", required=True)
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    unit_price = fields.Float(string="单价")
    is_active = fields.Boolean(string="启用")



    sample_image = fields.Image(string="图片")
    

    # 设置产品编码
    @api.depends('style_number')
    def set_product_barcode(self):
        for record in self:

            if record.style_number:

                record.product_barcode = record.style_number.barcode_data


    def test(self):
        for record in self:
            print(record.sample_image)
            image_base64 = record.sample_image
            image_base64 = image_process(image_base64, size=(int(200), int(200)), crop=False, quality=int(0))


            # if product:
            #     status, headers, image_base64 = request.env['ir.http'].sudo().binary_content(
            #         model=args['model'], id=product.id, field=args['field'], default_mimetype='image/png')
            #     return Binary._content_image_get_response(status, headers, image_base64)


