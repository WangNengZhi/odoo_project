from odoo import api, fields, models
# from odoo.exceptions import ValidationError

class EcResultsManage(models.Model):
    _name = 'ec_task'
    _description = '电商任务'
    _rec_name = 'task_name'
    # _order = "date desc"


    task_name = fields.Char(string="任务名称", required=True)