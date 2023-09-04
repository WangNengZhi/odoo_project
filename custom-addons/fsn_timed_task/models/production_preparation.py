# -*- coding: utf-8 -*-
from odoo import models
from utils import weixin_utils

class ProductionPreparation(models.Model):
    _inherit = 'production_preparation'


    # 3P流程检测
    def _inspection_task(self, chatid):
        production_preparation_objs = self.sudo().search([])
        # 消息列表
        message_list = []

        for production_preparation_obj in production_preparation_objs:
            # 临时列表
            tem_list = []
            for line_id in production_preparation_obj.line_ids:
                if line_id.is_confirm:
                    pass
                else:
                    tem_list.append(line_id.is_confirm)

            state = production_preparation_obj.order_number.is_finish
            if not (state=='已完成' and not tem_list):
                message_list.append({
                    "style_number": production_preparation_obj.style_number.style_number,   # 款号
                    "up_wire_date": production_preparation_obj.up_wire_date,    # 上线日期
                    "group": production_preparation_obj.group,      # 组别
                    "count": len(tem_list),     # 数量
                    "state": state,  # 订单状态
                })

        if not message_list:
            return

        self.env["mail.channel"].sudo()._3p_send_messagrs(message_list)

        def format(d):
            return f"款号：{d['style_number']}，上线日期：{d['up_wire_date']}，组别：{d['group']}，未勾选数量：{d['count']}，订单状态：{d['state']}"

        # print(repr(message_list[0]))
        text = '\n'.join(format(msg) for msg in message_list)

        # weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.DEVELOPMENT_AND_TEST)     # 开服测试群
        # weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.ADMIN_GROUP)    # 公司管理群

        weixin_utils.send_app_group_info_text_weixin(text, chatid)

