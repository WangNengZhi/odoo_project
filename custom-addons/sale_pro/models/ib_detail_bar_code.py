from odoo import models, fields, api
from odoo.exceptions import ValidationError
from reportlab.graphics.barcode import createBarcodeDrawing
import base64

import qrcode

from io import BytesIO



class IbDetail(models.Model):
    """ 继承订单"""
    _inherit = 'ib.detail'


    barcode_data = fields.Text(string="条形码数据")

    bar_code = fields.Image(string="条形码", compute="set_bar_code", store=True)

    qr_code = fields.Image(string="二维码", compute="generate_qr_code", store=True)


    # ib_detail_bar_code_ids = fields.One2many("ib_detail_bar_code", "ib_detail_id", string="款号条码明细表")



    # 生成条形码数据
    # @api.depends("order_id", "order_id.customer_id", "style_number")
    def set_barcode_data(self):
        for record in self:

            if record.order_id and record.style_number:
                record.barcode_data = f"693{record.order_id.customer_id.customer_number}{record.style_number}0"


    # 生成条形码
    @api.depends("barcode_data")
    def set_bar_code(self, width=300, height=50, humanreadable=0, quiet=1, mask=None):
        for record in self:

            barcode_type = "Code128"
            value = record.barcode_data

            barcode = createBarcodeDrawing(
                barcode_type, value=value, format='png', width=width, height=height,
                humanReadable=humanreadable, quiet=quiet, barBorder=4
            )

            record.bar_code = base64.b64encode(barcode.asString('png'))


    # 生成二维码(订单编号)
    @api.depends('barcode_data')
    def generate_qr_code(self):
        for record in self:

            img = qrcode.make(record.barcode_data, box_size="4")
            # PIL转base64
            b_img = BytesIO()
            img._img.save(b_img, format='jpeg')
            b_img = b_img.getvalue()
            b64_img = base64.b64encode(b_img)


            record.qr_code = b64_img







