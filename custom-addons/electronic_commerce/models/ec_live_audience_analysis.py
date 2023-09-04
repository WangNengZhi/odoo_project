
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ECLiveAudienceAnalysis(models.Model):
    _name = 'ec_live_audience_analysis'
    _description = '直播观客群'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)
    start_time = fields.Datetime(string="直播开始时间")
    end_time = fields.Datetime(string="直播结束时间")

    fans_ratio = fields.Float(string="粉丝占比")
    not_fans_ratio = fields.Float(string="非粉丝占比")

    man_ratio = fields.Float(string="男性占比")
    woman_tatio = fields.Float(string="女性占比")

    under_18_age_tatio = fields.Float(string="18岁以下占比")
    age_18_23 = fields.Float(string="18岁-23岁占比")
    age_24_30 = fields.Float(string="24岁-30岁占比")
    age_31_40 = fields.Float(string="31岁-40岁占比")
    age_41_50 = fields.Float(string="18岁-23岁占比")
    age_50_above = fields.Float(string="18岁-23岁占比")

    ec_laa_area_line_ids = fields.One2many("ec_laa_area_line", "elaa_id", string="地区明细", copy=True)


    # def copy(self, default=None):
    #     self.ensure_one()
    #     default = dict(default or {})


    #     for i in self.ec_laa_area_line_ids:
    #         line_obj = i.copy()

    #     return super(ECLiveAudienceAnalysis, self).copy(default=default)


class ECLiveAudienceAnalysisAreaLine(models.Model):
    _name = 'ec_laa_area_line'
    _description = '直播观客群地区明细'


    elaa_id = fields.Many2one("ec_live_audience_analysis", ondelete="cascade")

    country_id = fields.Many2one('res.country', string='国家', required=True, default=48)
    country_code = fields.Char(related='country_id.code')
    state_id = fields.Many2one('res.country.state', string='省份', domain="[('country_id', '=?', country_id)]")
    ratio = fields.Float(string="占比")