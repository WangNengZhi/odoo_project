from odoo import api, fields, models
from odoo.exceptions import ValidationError

class RoomConfig(models.Model):
    _name = 'room_config'
    _description = '房间配置'
    _rec_name = 'room_serial_number'
    # _order = "date desc"


    dormitory_park_id = fields.Many2one("dormitory_park", string="园区", required=True)
    dormitory_building_number_id = fields.Many2one("dormitory_building_number", string="楼号", required=True, ondelete='restrict')

    @api.onchange('dormitory_park_id')
    def _onchange_dormitory_building_number_id(self):

        self.dormitory_building_number_id = False

        if self.dormitory_park_id:
            return {'domain': {'dormitory_building_number_id': [('dormitory_park_id', '=', self.dormitory_park_id.id)]}}
        else:
            return {'domain': {'dormitory_building_number_id': []}}
            

    room_serial_number = fields.Char(string="房间号", required=True)
    # 检查数据唯一性
    @api.constrains('dormitory_park_id', 'dormitory_building_number_id', 'room_serial_number')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('dormitory_park_id', '=', self.dormitory_park_id.id),
            ('dormitory_building_number_id', '=', self.dormitory_building_number_id.id),
            ('room_serial_number', '=', self.room_serial_number),
        ])

        if len(demo) > 1:
            raise ValidationError(f"不可创建相同园区相同楼号相同房间号")
    bed_number = fields.Integer(string="床位数量")
    is_air_conditioner = fields.Boolean(string="空调")
    is_water_heater = fields.Boolean(string="热水器")
    is_wardrobe = fields.Boolean(string="衣柜")
    note = fields.Char(string="备注")