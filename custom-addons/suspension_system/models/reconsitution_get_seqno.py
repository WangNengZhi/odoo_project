from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import requests
import json
import itertools


class SuspensionSystemGetSeqno(models.Model):
    _inherit = "suspension_system_get_seqno"


