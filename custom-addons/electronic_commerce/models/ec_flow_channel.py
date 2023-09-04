from odoo import api, fields, models
from odoo.exceptions import ValidationError

class EcFlowChannel(models.Model):
    _name = 'ec_flow_channel'
    _description = '电商流量渠道'
    _rec_name = 'platform_account_id'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)
    
    qianchuan_pc_traffic = fields.Float(string="千川流量占比")
    qianchuan_pc_amount = fields.Float(string="千川成交金额占比")

    small_shop_traffic = fields.Float(string="小店随心推流量占比")
    small_shop_amount = fields.Float(string="小店随心推成交金额占比")

    other_advertising_traffic = fields.Float(string="其他广告流量占比")
    other_advertising_amount = fields.Float(string="其他广告成交金额占比")

    qianchuan_brand_advertising_traffic = fields.Float(string="千川品牌广告流量占比")
    qianchuan_brand_advertising_amount = fields.Float(string="千川品牌广告成交金额占比")

    brand_advertising_traffic = fields.Float(string="品牌广告流量占比")
    brand_advertising_amount = fields.Float(string="品牌广告成交金额占比")

    recommended_feed_traffic = fields.Float(string="推荐feed流量占比")
    recommended_feed_amount = fields.Float(string="推荐feed成交金额占比")

    other_recommended_scenarios_traffic = fields.Float(string="其他推荐场景流量占比")
    other_recommended_scenarios_amount = fields.Float(string="其他推荐场景成交金额占比")

    live_square_traffic = fields.Float(string="直播广场流量占比")
    live_square_amount = fields.Float(string="直播广场成交金额占比")

    same_city_traffic = fields.Float(string="同城流量占比")
    same_city_amount = fields.Float(string="同城成交金额占比")

    big_watermelon_traffic = fields.Float(string="头条西瓜流量占比")
    big_watermelon_amount = fields.Float(string="头条西瓜成交金额占比")

    home_page_store_window_traffic = fields.Float(string="个人主页&店铺&橱窗流量占比")
    home_page_store_window_amount = fields.Float(string="个人主页&店铺&橱窗成交金额占比")

    focus_traffic = fields.Float(string="关注流量占比")
    focus_amount = fields.Float(string="关注成交金额占比")

    short_video_diversion_traffic = fields.Float(string="短视频引流流量占比")
    short_video_diversion_amount = fields.Float(string="短视频引流成交金额占比")

    search_traffic = fields.Float(string="搜索流量占比")
    search_amount = fields.Float(string="搜索成交金额占比")

    active_page_traffic = fields.Float(string="活动页流量占比")
    sactive_page_amount = fields.Float(string="活动页成交金额占比")

    other_traffic = fields.Float(string="其他流量占比")
    other_amount = fields.Float(string="其他成交金额占比")

    mall_recommend_traffic = fields.Float(string="抖音商城推荐流量占比")
    mall_recommend_amount = fields.Float(string="抖音商城推荐成交金额占比")
 

