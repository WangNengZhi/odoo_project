from datetime import datetime, timedelta

from odoo import models, fields, api


class ProcurementDailyReport(models.TransientModel):
    """获取采购30天没有入库信息"""
    _inherit = "fsn_daily"

    def mechanical_repair_procurement(self):
        """获取机修采购"""
        date_threshold = datetime.now() - timedelta(days=30)

        procurements = self.env['maintain_procurement'].search([('date', '>', date_threshold.strftime('%Y-%m-%d'))])
        # 检查每个采购记录是否存在对应的入库记录
        items_without_put = []

        for procurement in procurements:
            # 检查maintain_put表中是否存在对应的入库记录
            put_record = self.env['maintain_put'].search([('material_code', '=', procurement.material_code.id),
                                                          ('material_name', '=', procurement.material_name)])

            if not put_record or procurement.payment_state != '已付款':
                item_info = {
                    'date': procurement.date,
                    'code': procurement.material_code.material_code,
                    'name': procurement.material_name,
                }

                items_without_put.append(item_info)
        return items_without_put

    def office_item_procurement(self):
        """办公室物品采购"""
        date_threshold = datetime.now() - timedelta(days=30)
        office_items = self.env['office_procurement_enter'].search([('date', '>', date_threshold.strftime('%Y-%m-%d'))])

        office_without_put = []

        for office in office_items:
            office_put = self.env['office_procurement_put'].search([('material_code', '=', office.material_code.id),
                                                                    ('material_name', '=', office.material_name)])

            if not office_put or office.payment_state != '已付款':
                office_info = {
                    'date': office.date,
                    'code': office.material_code.material_code,
                    'name': office.material_name,
                }
                office_without_put.append(office_info)
        return office_without_put

    def procurement_of_surface_auxiliary_materials(self):
        """面辅料采购"""
        date_threshold = datetime.now() - timedelta(days=30)

        surface_list = []

        surface_items = self.env['fabric_ingredients_procurement'].search([('date', '>', date_threshold.strftime('%Y-%m-%d'))])
        for surface in surface_items:
            surface_put = self.env['plus_material_enter'].search([('material_coding.material_code', '=', surface.material_code.id),
                                                                  ('material_name', '=', surface.material_name)])
            if not surface_put or surface.payment_state != '已付款':
                surface_info = {
                    'date': surface.date,
                    'code': surface.material_code.name,
                    'name': surface.material_name,
                }
                surface_list.append(surface_info)
        return surface_list


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_fsn_procurement_daily(self):
        """发送采购日报"""
        message_content = {}

        message_content['mechanical_repair'] = self.env['fsn_daily'].mechanical_repair_procurement()

        message_content['office_item_procurement'] = self.env['fsn_daily'].office_item_procurement()

        message_content['procurement_of_surface'] = self.env['fsn_daily'].procurement_of_surface_auxiliary_materials()

        message_str = f"<b>{len(message_content['mechanical_repair'])}条设备采购异常记录物品未入库或未付款:</b><br/>"
        for message in message_content['mechanical_repair']:
            message_str += f"日期：{message['date']}，物料编码：{message['code']}，物品名称：{message['name']}<br/>"

        message_str += f"<b>{len(message_content['office_item_procurement'])}条办公室用品采购异常记录物品未入库或未付款:</b><br/>"
        for message in message_content['office_item_procurement']:
            message_str += f"日期：{message['date']}，物料编码：{message['code']}，物品名称：{message['name']}<br/>"

        message_str += f"<b>{len(message_content['procurement_of_surface'])}条面辅料采购异常记录物品未入库或未付款:</b><br/>"
        for message in message_content['procurement_of_surface']:
            message_str += f"日期：{message['date']}，物料编码：{message['code']}，物品名称：{message['name']}<br/>"


        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
