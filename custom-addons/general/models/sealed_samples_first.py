from odoo import models, fields, api


class SealedSamplesFirst(models.Model):
    _name = 'sealed_samples_first'
    _description = '首件封样'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    tarde_name = fields.Char(string="品名")

    fsn_staff_team_id = fields.Many2many("fsn_staff_team", string="生产小组", required=True)
    inspect_conclusion = fields.Text(string="检验结论")
    picture = fields.Image(string='图片', required=True)

    sealed_samples_first_line_ids = fields.One2many("sealed_samples_first_line", "sealed_samples_first_id", string="首件封样明细")


class SealedSamplesFirstLine(models.Model):
    _name = 'sealed_samples_first_line'
    _description = '首件封样明细'
    _rec_name = 'parts_name'
    _order = "parts_name"

    sealed_samples_first_id = fields.Many2one("sealed_samples_first", string="首件封样", ondelete='cascade')
    parts_name = fields.Char(string="部位名称", required=True)
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    technical_requirements = fields.Char(string="技术要求")
    sample_results = fields.Char(string="封样结果")
    confirm_record = fields.Char(string="确认记录")


