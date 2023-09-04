from odoo import models, fields, api

import datetime
import time

from utils import weixin_approval_utils


class OutsourceOrder(models.Model):
    _inherit = 'outbound_order_progress'


    sp_no = fields.Char(string="审批编号")


    def workwx_auto_sync_info(self, now_time):
        ''' 同步企业微信审批任务'''
        now_time += datetime.timedelta(hours=8)
        old_time = now_time - datetime.timedelta(days=5)

        now_time_stamp = int(time.mktime(now_time.timetuple()))
        old_time_stamp = int(time.mktime(old_time.timetuple()))


        print(now_time, old_time)
        print(now_time_stamp, old_time_stamp)
        approval_number_info = weixin_approval_utils.get_approval_number_info(old_time_stamp, now_time_stamp, weixin_approval_utils.SP_TEMPLATE_ID, weixin_approval_utils.HAVE_PASSED)

        for sp_no in approval_number_info:
            print(sp_no)

            if self.env['outbound_order_progress'].sudo().search([("sp_no", "=", sp_no)]):
                continue

            detail_info = weixin_approval_utils.get_approval_details_info(sp_no)

            # 申请人
            emp_obj = self.env['hr.employee'].sudo().search([("enterprise_wechat_account", "=", detail_info['applyer']['userid'])])
            # 外发订单

            for field_info in detail_info['apply_data']['contents']:

                if field_info['title'][0]['text'] == "交货日期":

                    s_timestamp = int(field_info['value']['date']['s_timestamp']) + 28800
                    s_timestamp = time.localtime(s_timestamp)
                    sp_date = time.strftime("%Y-%m-%d", s_timestamp)

                if field_info['title'][0]['text'] == "外发订单":

                    outsource_order_id = int(field_info['value']['selector']['options'][0]['key'])
                    outsource_order_obj = self.env['outsource_order'].sudo().browse(outsource_order_id)
 
                if field_info['title'][0]['text'] == "款号":

                    ib_detail_id = int(field_info['value']['selector']['options'][0]['key'])
                    ib_detail_obj = self.env['ib.detail'].sudo().browse(ib_detail_id)

                line_list = []
                if field_info['title'][0]['text'] == "交货尺码明细":
                    
                    for line_info in field_info['value']['children']:

                        for line_field_info in line_info['list']:

                            if line_field_info['title'][0]['text'] == "尺码":
                                size_name = line_field_info['value']['selector']['options'][0]['key']
                                fsn_size_obj = self.env['fsn_size'].sudo().search([("name", "=", size_name)])

                            if line_field_info['title'][0]['text'] == "裁剪件数":

                                cutting_number = line_field_info['value']['new_number']

                            if line_field_info['title'][0]['text'] == "完成件数":

                                complete_number = line_field_info['value']['new_number']

                            if line_field_info['title'][0]['text'] == "交货件数":

                                delivery_number = line_field_info['value']['new_number']

                        line_list.append((0, 0, {
                            "size": fsn_size_obj.id,
                            "solid_cutting_quantity": cutting_number,
                            "complete_number": complete_number,
                            "quantity_delivered": delivery_number,
                        }))
            print(sp_no)
            try:

                outbound_order_progress_obj = self.env['outbound_order_progress'].sudo().create({
                    "sp_no": sp_no,     # 审批编号
                    "date": sp_date,    # 日期
                    "responsible_person": outsource_order_obj.responsible_person.id,   # 负责人
                    "outsource_order_id": outsource_order_obj.id,   # 外发订单
                    "order_number": outsource_order_obj.order_id.id,    # 订单号
                    "style_number": ib_detail_obj.id,   # 款号
                    "outbound_order_progress_line_ids": line_list,  # 进度表明细
                })

                last_outbound_order_progress_obj = self.env['outbound_order_progress'].sudo().search([
                    ("outsource_order_id", "=", outsource_order_obj.id),
                    ("style_number", "=", ib_detail_obj.id),
                    ("id", "!=", outbound_order_progress_obj.id)
                ], order="date desc", limit=1)

                if last_outbound_order_progress_obj:
                    outbound_order_progress_obj.outbound_order_progress_id = last_outbound_order_progress_obj.id
            
            except Exception as err:
                pass



