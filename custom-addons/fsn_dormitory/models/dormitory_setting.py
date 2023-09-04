from odoo import api, fields, models
from odoo.exceptions import ValidationError

class DormitoryPark(models.Model):
    _name = 'dormitory_park'
    _description = '宿舍园区'


    name = fields.Char(string="园区名称", required=True)
    dormitory_building_number_ids = fields.One2many("dormitory_building_number", "dormitory_park_id", string="楼号")


class DormitoryBuildingNumber(models.Model):
    _name = 'dormitory_building_number'
    _description = '宿舍楼号'


    dormitory_park_id = fields.Many2one("dormitory_park", string="园区", ondelete='restrict', required=True)
    name = fields.Char(string="楼号", required=True)
