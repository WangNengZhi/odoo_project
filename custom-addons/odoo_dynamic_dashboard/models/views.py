import datetime
import random
import time

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Views(models.Model):
    _name = 'views'
    _description = '视图'
    


    fsn_sales_order_id = fields.Many2one("fsn_sales_order", string="FSN销售订单")