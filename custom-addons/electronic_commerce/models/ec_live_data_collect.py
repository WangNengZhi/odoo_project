
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EcLiveDataCollect(models.Model):
    _name = 'ec_live_data_collect'
    _description = '直播数据汇总'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)
    start_time = fields.Datetime(string="直播开始时间")
    end_time = fields.Datetime(string="直播结束时间")
    live_time = fields.Float(string="直播时长（分钟）", compute="_value_live_time", store=True)
    @api.depends('start_time', 'end_time')
    def _value_live_time(self):
        for record in self:
            if record.end_time and record.start_time:
                record.live_time = ((record.end_time - record.start_time).seconds) / 60



    GMV = fields.Float(string="GMV")
    volume_transaction_order = fields.Integer(string="成交订单量")
    GPM = fields.Float(string="千次成交金额GPM")
    KDJ = fields.Float(string="客单价")
    ZHL = fields.Float(string="转化率")
    UVJZ = fields.Float(string="uv价值")

    pay_roi = fields.Float(string="付费roi")
    all_those_roi = fields.Float(string="全场roi", compute="set_all_those_roi", store=True)
    @api.depends("GMV", "shop_will_push", "shake_plus", "qian_chuan_cost")
    def set_all_those_roi(self):
        for record in self:
            # GMV / (小店随心推费用 + 抖+费用 + 千川费用)
            cost = record.shop_will_push + record.shake_plus + record.qian_chuan_cost
            if cost:
                record.all_those_roi = record.GMV / cost
            else:
                record.all_those_roi = 0

    watch_number = fields.Float(string="观看人次")
    number_peaks = fields.Float(string="人数峰值")
    avg_number = fields.Float(string="平均在线人数")
    exposure_number = fields.Float(string="直播间曝光次数")
    exposure_people = fields.Float(string="直播间曝光人数")


    BGJRL = fields.Float(string="曝光进入率")
    JRSPBGL = fields.Float(string="进入商品曝光率")
    SPBGDJL = fields.Float(string="商品曝光点击率")
    BGCJZHL = fields.Float(string="曝光成交转化率")


    recommend_feed = fields.Float(string="推荐feed")
    live_plaza = fields.Float(string="直播广场")
    personal_homepage = fields.Float(string="个人主页")
    short_video_flow = fields.Float(string="短视频流量")
    search_data = fields.Float(string="搜索")
    other_scenarios = fields.Float(string="其他场景")



    shop_will_push_ratio = fields.Float(string="小店随心推")
    shop_will_push = fields.Float(string="小店随心推费用")

    shake_plus_ratio = fields.Float(string="抖+")
    shake_plus = fields.Float(string="抖+费用")

    qian_chuan = fields.Float(string="千川")
    qian_chuan_cost = fields.Float(string="千川费用")

    percentage_paid_traffic = fields.Float(string="付费流量占比", compute="set_percentage_paid_traffic", store=True)
    @api.depends("recommend_feed", "live_plaza", "personal_homepage", "short_video_flow", "search_data", "other_scenarios", "shop_will_push", "shake_plus", "qian_chuan")
    def set_percentage_paid_traffic(self):
        for record in self:

            natural = record.recommend_feed + record.live_plaza + record.personal_homepage + record.short_video_flow + record.search_data + record.other_scenarios

            pay = record.shop_will_push + record.shake_plus + record.qian_chuan

            if (natural + pay):
                record.percentage_paid_traffic = (pay / (natural + pay)) * 100
            else:
                record.percentage_paid_traffic = 0




    XZFSS = fields.Float(string="新增粉丝数")
    ZFL = fields.Float(string="转粉率")
    XRFSTS = fields.Float(string="新人粉丝团人数")
    ZTL = fields.Float(string="转团率")
    PJTLSC = fields.Float(string="平均停留时长（秒）")
    PLCS = fields.Float(string="评论次数")
    DZL = fields.Float(string="点赞量（万）")
    FXCS = fields.Float(string="分享次数")













