import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class ClothingVersionSample(models.Model):
    _name = 'clothing_version_sample'
    _description = '版样'
    _rec_name = 'style_number_id'
    _order = 'date desc'

    date = fields.Date(string="日期", required=True)
    style_number_id = fields.Many2one('ib.detail', string='款号', required=True)
    plate_number = fields.Char(string="版号", required=True)
    version_sample_url = fields.Char(string="模板URL")
    author = fields.Many2one('hr.employee', string='作者', required=True)
    image = fields.Image(string="测试图片")



    def upload_attachment(self):

        
        action = {
            'name': self.plate_number,
            'view_mode': 'form',
            'res_model': 'clothing_version_sample',
            'view_id': self.env.ref('template_house.clothing_version_sample_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action
    
