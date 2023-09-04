from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FlowConversionEfficiency(models.Model):
    _name = 'flow_conversion_efficiency'
    _description = '流量转换效率'
    _rec_name = 'platform_account_id'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    platform_account_id = fields.Many2one("platform_account", string="账号", required=True)

    exposure_number = fields.Float(string="直播间曝光人数")

    enter_number = fields.Float(string="直播间进入人数")

    exposure_conversion_efficiency = fields.Float(string="直播间曝光转化率", compute="set_exposure_conversion_efficiency", store=True)

    @api.depends('exposure_number', 'enter_number')
    def set_exposure_conversion_efficiency(self):
        for record in self:

            if record.exposure_number:
                record.exposure_conversion_efficiency = record.enter_number / record.exposure_number

    goods_exposure_number = fields.Float(string="商品曝光人数")
    enter_efficiency = fields.Float(string="直播间进入转化率", compute="set_enter_efficiency", store=True)
    @api.depends('enter_number', 'goods_exposure_number')
    def set_enter_efficiency(self):
        for record in self:

            if record.enter_number:
                record.enter_efficiency = record.goods_exposure_number / record.enter_number



    goods_click_number = fields.Float(string="商品点击人数")
    goods_exposure_efficiency = fields.Float(string="商品曝光转化率", compute="set_goods_exposure_efficiency", store=True)

    @api.depends('goods_exposure_number', 'goods_click_number')
    def set_goods_exposure_efficiency(self):
        for record in self:

            if record.goods_exposure_number:
                record.goods_exposure_efficiency = record.goods_click_number / record.goods_exposure_number


    clinch_deal_number = fields.Float(string="成交人数")
    goods_click_efficiency = fields.Float(string="商品点击转化率", compute="set_goods_click_efficiency", store=True)


    @api.depends('goods_click_number', 'clinch_deal_number')
    def set_goods_click_efficiency(self):
        for record in self:

            if record.goods_click_number:
                record.goods_click_efficiency = record.clinch_deal_number / record.goods_click_number