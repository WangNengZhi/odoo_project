from datetime import datetime, timedelta

from odoo import models, fields, api


class BackLane(models.TransientModel):
    _inherit = "fsn_daily"
    """后道当天没有交货生成罚单"""

    def obtain_subsequent_delivery_information(self):
        """获取后道交货信息"""
        # 获取前一天的日期
        previous_day = datetime.now().date() - timedelta(days=1)
        # tmp_date = '2023-02-11'

        delivery_records = self.env['posterior_passage_output_value'].search([('date', '=', previous_day)])
        return delivery_records

