from datetime import datetime, date, time, timedelta
from odoo import api, fields, models
import itertools


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'



