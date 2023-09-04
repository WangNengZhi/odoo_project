from odoo.exceptions import ValidationError
from odoo import models, fields, api


from datetime import datetime, timedelta
import time


class FillHouse(models.Model):
    _name = "fill_house"
    _description = '充绒房产值'
    _rec_name = "date"
    _order = "date desc"


    date = fields.Date('日期', required=True)