from odoo.exceptions import ValidationError
from odoo import models, fields, api


class GeneralGeneral(models.Model):
    '''生产订单_自动任务'''
    _inherit = "sale_pro.sale_pro"


    def auto_online_scheduled_task(self, today):
        ''' 生产订单状态改为自动上线'''
        sale_pro_objs = self.env['sale_pro.sale_pro'].sudo().search([("is_finish", "=", "未上线")])
        for sale_pro_obj in sale_pro_objs:

            if sale_pro_obj.attribute.name == "裁片":

                if self.env['plus_material_outbound'].sudo().search([("order_id", "=", sale_pro_obj.id), ("state", "=", "已出库")]):
                    sale_pro_obj.is_finish = "未完成"

            else:

                if sale_pro_obj.processing_type == "工厂":
                    
                    if self.env['suspension_system_station_summary'].sudo().search([("order_number", "=", sale_pro_obj.id)]):
                        sale_pro_obj.is_finish = "未完成"
                    
                elif sale_pro_obj.processing_type == "外发":
                    
                    if self.env['fsn_month_plan'].sudo().search([("order_number", "=", sale_pro_obj.id), ("plan_online_date", "<=", today)]):
                        sale_pro_obj.is_finish = "未完成"

