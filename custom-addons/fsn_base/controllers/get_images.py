from odoo.addons.web.controllers import main as web
from odoo import http


class GetImages(http.Controller):

    @http.route('/get_imgae/', methods=['POST', 'GET'], type='http', auth="public", cors="*", csrf=False)
    def get_imgae(self, **kw):


        model = kw.get("model")     # 模型名
        id = kw.get("id")   # 记录id
        field = kw.get("field")     # 字段名

        status, headers, image_base64 = http.request.env['ir.http'].sudo().binary_content(model=model, id=id, field=field, default_mimetype='image/png')

        return web.Binary._content_image_get_response(status, headers, image_base64)
