from odoo.exceptions import ValidationError
from odoo import models, fields, api



class Yingshi_Cloud_Setting(models.Model):
    _name = 'yingshi_cloud_setting'
    _description = '萤石云设置'


    key = fields.Char(string="Key")
    value = fields.Char(string="Value")


class Yingshi_Equipment_Info(models.Model):
    _name = 'yingshi_equipment_info'
    _description = '萤石设备信息'

    device_name = fields.Char(string="设备标识（唯一）")
    device_serial_number = fields.Char(string="设备序列号")
    device_channel_number = fields.Char(string="通道编号")




