# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

# 666666666666666666

class Channel(models.Model):
    _inherit = 'mail.channel'

    # 产前准备消息发送
    def _3p_send_messagrs(self, message_list):
        # [{'style_number': '51009-RD', 'up_wire_date': datetime.date(2021, 8, 26), 'group': '1', 'count': 25}, {'style_number': '24395-BK', 'date': datetime.date(2021, 8, 26), 'group': '1', 'count': 29}]
        
        # 消息
        message_str = ""
        for message in message_list:
            message_str += f"款号：{message['style_number']}，上线日期：{message['up_wire_date']}，组别：{message['group']}，未勾选数量：{message['count']}，订单状态：{message['state']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.production_preparation_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel

    # 产前频道
    def send_advance_preparation_messages(self, message_list):


        message_str = f"{message_list['sheet_materials_messages_content']['date']}_{len(message_list['sheet_materials_messages_content']['message_content'])}个缺少单件用料表的销售订单信息:<br/>"
        for message in message_list["sheet_materials_messages_content"]["message_content"]:
            message_str += f"客户货期：{message['customer_delivery_time']}，订单日期：{message['order_date']}，订单:{message['order_number']}，款号:{message['style_number']}<br/>"


        # message_str += f"共有{sum(len(i['message_content']) for i in message_list['plan_set_messages_messages_content'] if i['message_content'])}条存在组的计划产值有异常:<br/>"
        # for day_messages in message_list["plan_set_messages_messages_content"]:
        #     for message in day_messages["message_content"]:
        #         message_str += f"日期:{day_messages['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
        #             计划人均产值:{message['plan_value_sum']}，计划阶段:{message['plan_stage']}<br/>"


        message_str += f"{message_list['sales_order_abnormal_plan_date_messages_content']['date']}销售订单计划完成日期存在问题！<br/>"
        for message in message_list["sales_order_abnormal_plan_date_messages_content"]["message_content"]:
            if message['processing_type'] == "外发":
                if not message['customer_goods_time']:
                    message_str += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，加工类型:{message['processing_type']}，无客户货期！<br/>"
            else:
                message_str += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，计划日期:{message['planned_completion_date']}，计算日期:{message['real_date']}，加工类型:{message['processing_type']}<br/>"



        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.production_preparation_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel


    # 产后频道
    def send_postpartum_messages(self, message_list):

        message_str = f"{message_list['fabric_exception_messages_content']['date']}共有{len(message_list['fabric_exception_messages_content']['message_content'])}条无采购记录的面料入库:<br/>"
        for message in message_list["fabric_exception_messages_content"]["message_content"]:
            message_str += f"物料编码:{message}<br/>"


        message_str += f"{message_list['supplementary_material_messages_content']['date']}共有{len(message_list['supplementary_material_messages_content']['message_content'])}条无采购记录的物料入库:<br/>"
        for message in message_list["supplementary_material_messages_content"]["message_content"]:
            message_str += f"物料编码:{message}<br/>"
        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_postpartum_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel




    # 后道专用频道
    def fsn_after_the_road_inspect_channel_messages(self, message_list):
        ''' 后道专用频道'''


        _logger.info('开始发送后道专用频道信息01')
        message_str = f"<b>{message_list['day_qing_day_bi_messages_content']['date']}_{len(message_list['day_qing_day_bi_messages_content']['message_content'])}个组的日清日毕信息:</b><br/>"
        for message in message_list["day_qing_day_bi_messages_content"]["message_content"]:
            if message['group'] == "后道":
                message_str += f"组别:{message['group']}，\
                日期:{message['date']}，\
                    人均件数:{format(message['number'] / message['num_people'], '0.2f') if message['num_people'] else '人数为0!' }，\
                        吊挂人均件数:{format(message['dg_number'] / message['num_people'], '0.2f') if message['num_people'] else '人数为0!' }，\
                            滞留数:{int(message['stranded_number'])}，\
                                计划差值:{int(message['plan_difference'])}，\
                                    计划阶段:{message['plan_stage']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_after_the_road_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel





    # 发送日报
    def send_daily_messages(self, message_list):

        _logger.info('开始发送系统内部日报！')

        message_str = f"<b>{message_list['examine_customer_delivery_time_message_content']['date']}:{len(message_list['examine_customer_delivery_time_message_content']['message_content'])}个订单已经超过计划完成日期！</b><br/>"
        for message in message_list["examine_customer_delivery_time_message_content"]["message_content"]:
            # message_str += f"订单号:{message['order_number']}   差值:{message['difference']}    报次:{message['not_goods']}<br/>"
            message_str += f"合同日期:{message['customer_delivery_time']}，下单日期：{message['date']}，\
                订单号:{message['order_number']}，\
                属性:{message['order_attribute']}，\
                款号:{message['style_number_base']}，\
                加工类型:{message['processing_type']}，\
                订单数:{message['order_number_value']}，\
                交货数:{message['quantity_goods']}，\
                报次:{message['defective_good_number']}，\
                存量:{message['qualified_stock']}，\
                裁片:{message['cutting_number']}，\
                半成品:{message['no_accomplish_number']}，\
                丢失:{message['lose_quantity']}<br/>"

        message_str += "<br/>"

        _logger.info('开始发送系统内部日报！1')

        message_str += f"<b>{message_list['encapsulation_dg_production_value_message_content']['date']}:各组吊挂产值信息！</b><br/>"
        # if message_list["encapsulation_dg_production_value_message_content"]["dg_yesterday_production_value"] < 15000:
        #     message_str += f"当天吊挂总产值为：{format(message_list['encapsulation_dg_production_value_message_content']['dg_yesterday_production_value'], '0.2f')}<br/>"
        for i in message_list["encapsulation_dg_production_value_message_content"]["dg_yesterday_production_value"]:
            if i['group'][-1] == "后整":
                message_str += f"组别：{i['group'][-1]}，当天吊挂总产量为：{format(i['total_quantity'], '0.2f')}件，\
                    当天人数：{i['people_num']}人，\
                        当天吊挂人均产量：{format(i['total_quantity'] / i['people_num'] if i['people_num'] else 0, '0.2f')}件<br/>"
            else:
                message_str += f"组别：{i['group'][-1]}，当天吊挂总产值为：{format(i['production_value'], '0.2f')}元，当月平均吊挂产值：{format(i['dg_month_avg_value'], '0.2f')}元<br/>"
        # message_str += f"当月平均吊挂产值为：{format(message_list['encapsulation_dg_production_value_message_content']['dg_average_monthly_production_value'], '0.2f')}<br/>"
        


        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！2')
        message_str += f"<b>{message_list['day_qing_day_bi_messages_content']['date']}_{len(message_list['day_qing_day_bi_messages_content']['message_content'])}个组的日清日毕信息:</b><br/>"
        for message in message_list["day_qing_day_bi_messages_content"]["message_content"]:
            if message['group'] == "后道":
                message_str += f"组别:{message['group']}，\
                日期:{message['date']}，\
                    人数:{message['num_people']}，\
                        人均件数:{format(message['number'] / message['num_people'], '0.2f') if message['num_people'] else '人数为0!' }，\
                            吊挂人均件数:{format(message['dg_number'] / message['num_people'], '0.2f') if message['num_people'] else '人数为0!' }，\
                                滞留数:{int(message['stranded_number'])}，\
                                    计划差值:{int(message['plan_difference'])}，\
                                        计划阶段:{message['plan_stage']}<br/>"
            else:
                message_str += f"组别:{message['group']}，\
                日期:{message['date']}，\
                    人数:{message['num_people']}，\
                        人均产值:{format(message['avg_value'], '0.2f')}，\
                            吊挂人均产值:{format(message['dg_avg_value'], '0.2f')}，\
                                滞留数:{int(message['stranded_number'])}，\
                                    计划差值:{int(message['plan_difference'])}，\
                                        计划阶段:{message['plan_stage']}<br/>"


        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！2.1')
        message_str += f"<b>{message_list['general_inspection_abnormal_info']['date']}_{len(message_list['general_inspection_abnormal_info']['message_content'])}总检异常信息:</b><br/>"
        for message in message_list["general_inspection_abnormal_info"]["message_content"]:
            if message['dg_general_number']:
                message_str += f"员工：{message['general1']}，查货数：{message['general_number']}，吊挂查货数:{message['dg_general_number']}，返修数:{message['repair_number']}，吊挂返修数:{message['dg_repair_number']}<br/>"



        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！3')
        message_str += f"<b>{message_list['sheet_materials_messages_content']['date']}_{len(message_list['sheet_materials_messages_content']['message_content'])}个缺少单件用料表的销售订单信息:</b><br/>"
        for message in message_list["sheet_materials_messages_content"]["message_content"]:
            message_str += f"订单日期：{message['order_date']}，客户货期：{message['customer_delivery_time']}，订单:{message['order_number']}，款号:{message['style_number']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！4')
        # message_str += f"<b>共有{sum(len(i['message_content']) for i in message_list['plan_set_messages_messages_content'] if i['message_content'])}条存在组的计划产值有异常:</b><br/>"
        # for day_messages in message_list["plan_set_messages_messages_content"]:
        #     for message in day_messages["message_content"]:
        #         if message['group_name'] in ['裁床', '后道']:
        #             message_str += f"日期:{day_messages['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
        #                 计划总产值:{message['plan_total_value']}，组上计划总产值:{message['group_plan_total_value']}，计划阶段:{message['plan_stage']}<br/>"
        #         else:
        #             message_str += f"日期:{day_messages['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
        #                 计划人均产值:{message['plan_value_sum']}，计划阶段:{message['plan_stage']}<br/>"
        
        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！4')
        message_str += f"<b>{message_list['day_plan_abnormal_info_content']['date']}共有{len(message_list['day_plan_abnormal_info_content']['message_content'])}条日计划异常记录:</b><br/>"
        for message in message_list["day_plan_abnormal_info_content"]["message_content"]:

            if message['group_name'] == '裁床':
                if "plan_total_value" in message and "group_plan_total_value" in message:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划总产值:{message['plan_total_value']}，组上计划总产值:{message['group_plan_total_value']}，计划阶段:{message['plan_stage']}<br/>"
                else:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！<br/>"
                    
            elif message['group_name'] == '后道':
                if "plan_number" in message:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划件数:{message['plan_number']}<br/>"
                else:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！<br/>"
            else:
                if "plan_value_sum" in message:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        计划人均产值:{message['plan_value_sum']}，计划阶段:{message['plan_stage']}<br/>"
                else:
                    message_str += f"日期:{message['date']}，组别:{message['group_name']}，人数:{message['num_people']}，款号:{message['style_number_base']}，\
                        部门和员工小组填写错误！<br/>"
                    
        message_str += "<br/>"


        _logger.info('开始发送系统内部日报！5')
        message_str += f"<b>{message_list['fabric_exception_messages_content']['date']}共有{len(message_list['fabric_exception_messages_content']['message_content'])}条无采购记录的面料入库:</b><br/>"
        for message in message_list["fabric_exception_messages_content"]["message_content"]:
            message_str += f"物料编码:{message}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！6')
        message_str += f"<b>{message_list['supplementary_material_messages_content']['date']}共有{len(message_list['supplementary_material_messages_content']['message_content'])}条无采购记录的物料入库:</b><br/>"
        for message in message_list["supplementary_material_messages_content"]["message_content"]:
            message_str += f"物料编码:{message}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！7')
        message_str += f"<b>{message_list['yesterday_employee_situation_messages_content']['date']}</b><br/>"
        message_str += f"入职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['induction_list'])}<br/>"
        for induction in message_list['yesterday_employee_situation_messages_content']['message_content']['induction_list']:
            message_str += f"{induction['name']}，{induction['job_name']}<br/>"
        message_str += f"离职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['departure_list'])}<br/>"
        for departure in message_list['yesterday_employee_situation_messages_content']['message_content']['departure_list']:
            message_str += f"{departure['name']}，{departure['job_name']}<br/>"
        message_str += f"在职人数:{len(message_list['yesterday_employee_situation_messages_content']['message_content']['yesterday_list'])}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！8')
        message_str += f"<b>{message_list['sales_order_abnormal_plan_date_messages_content']['date']}销售订单计划完成日期存在问题！</b><br/>"
        for message in message_list["sales_order_abnormal_plan_date_messages_content"]["message_content"]:
            if message['processing_type'] == "外发":
                if not message['customer_goods_time']:
                    message_str += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，加工类型:{message['processing_type']}，无客户货期！<br/>"
            else:
                message_str += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['date']}，订单编号:{message['order_number']}，计划日期:{message['planned_completion_date']}，计算日期:{message['real_date']}，加工类型:{message['processing_type']}<br/>"

        message_str += "<br/>"

        # message_str += f"<b>{message_list['statistical_summary_abnormal_messages_content']['date']}共有{len(message_list['statistical_summary_abnormal_messages_content']['message_content'])}条统计汇总存在问题！</b><br/>"
        # for message in message_list["statistical_summary_abnormal_messages_content"]["message_content"]:
        #     message_str += f"订单号:{message['order_number']}，款号:{message['style_number']}，异常信息:{message['exception_info']}， 差值：{message['difference']}<br/>"

        # message_str += "<br/>"
        _logger.info('开始发送系统内部日报！9')
        message_str += f"<b>{message_list['fabric_procurement_messages_content']['date']}共有{len(message_list['fabric_procurement_messages_content']['message_content'])}条面辅料采购后三天没有仓库入库的记录！</b><br/>"
        for message in message_list["fabric_procurement_messages_content"]["message_content"]:
            message_str += f"物料单号:{message}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！10')
        message_str += f"<b>{message_list['monthly_plan_abnormal_messages_content']['date']}共有{len(message_list['monthly_plan_abnormal_messages_content']['message_content'])}条月计划异常信息记录！</b><br/>"
        for message in message_list["monthly_plan_abnormal_messages_content"]["message_content"]:
            message_str += f"客户货期：{message['customer_delivery_time']}，下单日期：{message['order_date']}，订单编号:{message['order_number']}，款号:{message['style_number']}，计划上线日期:{message['plan_online_date']}，计划交货日期:{message['production_delivery_time']}，计算交货日期:{message['real_date']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！11')
        message_str += f"<b>{message_list['raw_materials_order_abnormal_info']['date']}共有{len(message_list['raw_materials_order_abnormal_info']['message_content'])}个订单的产前准备计划物料异常！</b><br/>"
        for message in message_list["raw_materials_order_abnormal_info"]["message_content"]:
            message_str += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_number']}，原因:{message['cause']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！12')
        message_str += f"<b>{message_list['outbound_order_abnormal_info']['date']}共有{len(message_list['outbound_order_abnormal_info']['message_content'])}个订单未创建外发订单！</b><br/>"
        for message in message_list["outbound_order_abnormal_info"]["message_content"]:
            message_str += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_number']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！13')
        message_str += f"<b>{message_list['material_summary_sheet_abnormal_info']['date']}共有{len(message_list['material_summary_sheet_abnormal_info']['message_content'])}个物料汇总数据异常的记录！</b><br/>"
        for message in message_list["material_summary_sheet_abnormal_info"]["message_content"]:
            message_str += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_id']}，款号:{message['style_number']}，物料名称：{message['material_name']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！14')
        message_str += f"<b>{message_list['monthly_plan_material_ready_abnormal_info']['date']}共有{len(message_list['monthly_plan_material_ready_abnormal_info']['message_content'])}个月计划上线日期前一天面辅料齐备异常的采购记录！</b><br/>"
        for message in message_list["monthly_plan_material_ready_abnormal_info"]["message_content"]:
            message_str += f"客户货期:{message['customer_delivery_time']}，下单日期：{message['order_number_date']}，订单编号:{message['order_id'][-1]}，款号:{message['style_number'][-1]}，物料编号:{message['material_code'][-1] if message['material_code'] else '无'}，物料名称：{message['material_name']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！15')
        message_str += f"<b>{message_list['monthly_plan_cutting_bed_production_abnormal_info']['date']}共有{len(message_list['monthly_plan_cutting_bed_production_abnormal_info']['message_content'])}个月计划上线日期前一天裁床产量异常的记录！</b><br/>"
        for message in message_list["monthly_plan_cutting_bed_production_abnormal_info"]["message_content"]:
            message_str += f"合同日期:{message['contract_date']}，订单日期:{message['order_date']}，订单编号:{message['order_number']}，\
                加工类型:{message['processing_type']}，款号:{message['style_number']}，订单件数{message['order_quantity']}，计划件数:{message['plan_number']}，\
                    完成件数：{message['cutting_bed_production']}<br/>"

        message_str += "<br/>"
        _logger.info('开始发送系统内部日报！16')
        message_str += f"<b>{message_list['sales_order_no_month_plan_abnormal_info']['date']}共有{len(message_list['sales_order_no_month_plan_abnormal_info']['message_content'])}个销售订单创建后第二天没有月计划的记录！</b><br/>"
        for message in message_list["sales_order_no_month_plan_abnormal_info"]["message_content"]:
            message_str += f"订单编号:{message['order_number']}，款号:{message['style_number']}，原因：{message['cause']}<br/>"

        _logger.info('开始发送系统内部日报！17')
        message_str += "<br/>"
        message_str += f"<b>{message_list['b2b_return_and_client_ware_abnormal_info']['date']}共有{len(message_list['b2b_return_and_client_ware_abnormal_info']['message_content'])}个B2B展厅退货和返修客仓件数不相符的款！</b><br/>"
        for message in message_list["b2b_return_and_client_ware_abnormal_info"]["message_content"]:
            message_str += f"款号:{message['style_number']}，质量：{message['quality']}，件数：{message['number']}, 客仓件数：{message['cangkujianshu']}<br/>"

        _logger.info('开始发送系统内部日报！18')
        message_str += "<br/>"
        message_str += f"<b>{message_list['b2b_return_and_finished_product_ware_info']['date']}共有{len(message_list['b2b_return_and_finished_product_ware_info']['message_content'])}个获取B2B展厅退货和仓库入库件数不相符的记录！</b><br/>"
        for message in message_list["b2b_return_and_finished_product_ware_info"]["message_content"]:
            message_str += f"款号:{message['style_number']}，质量：{message['quality']}，件数：{message['number']}，仓库件数：{message['cangkujianshu']}<br/>"

        _logger.info('开始发送系统内部日报！19')
        message_str += "<br/>"
        message_str += f"<b>{message_list['fsn_sales_return_and_finished_product_ware_info']['date']}共有{len(message_list['fsn_sales_return_and_finished_product_ware_info']['message_content'])}个销售售后退货和仓库入库件数不相符的记录！</b><br/>"
        for message in message_list["fsn_sales_return_and_finished_product_ware_info"]["message_content"]:
            message_str += f"订单号:{message['order_id']}，款号:{message['style_number']}，质量：{message['quality']}，件数：{message['number']}，仓库件数：{message['cangkujianshu']}<br/>"

        _logger.info('开始发送系统内部日报！20')
        message_str += "<br/>"
        message_str += f"<b>{message_list['after_sales_return_goods_info']['date']}新增{len(message_list['after_sales_return_goods_info']['message_content'])}个销售售后退货和B2B展厅退货记录！</b><br/>"
        for message in message_list["after_sales_return_goods_info"]["message_content"]:
            message_str += f"类型：{message['type']}，客户：{message['customer_name']}，款号:{message['style_number']}，质量：{message['quality']}，件数：{message['number']}<br/>"
        _logger.info('开始发送系统内部日报！21')
        message_str += "<br/>"
        message_str += f"<b>{message_list['production_drop_documents_warehouse_info']['date']}共有{len(message_list['production_drop_documents_warehouse_info']['message_content'])}个产前准备人工核算和面辅料出库对比记录！</b><br/>"
        for message in message_list["production_drop_documents_warehouse_info"]["message_content"]:
            message_str += f"类型：{message['type']}，订单号：{message['order_id']}，款号:{message['style_number']}，物料名称：{message['material_name']}，计划数量：{message['planned_dosage']}，出库数量：{message['cangkshuliang']}<br/>"

        _logger.info('开始发送系统内部日报！22')
        message_str += "<br/>"
        message_str += f"<b>{message_list['schedule_production_abnormal_info']['date']}共有{len(message_list['schedule_production_abnormal_info']['message_content'])}个生产进度表裁床数和仓库不符的记录！</b><br/>"
        for message in message_list["schedule_production_abnormal_info"]["message_content"]:
            message_str += f"合同日期：{message['date_contract']}，下单日期：{message['date_order']}，订单号：{message['order_number']}，加工类型：{message['processing_type']}，款号:{message['style_number']}，尺码:{message['size']}，\
                订单数量:{message['quantity_order']}，裁剪数量：{message['quantity_cutting']}，仓库存量：{message['warehouse']}，报次库存：{message['defective_number']}，\
            裁片数量:{message['cutting_number']}，半成品数量：{message['no_accomplish_number']}<br/>"

        _logger.info('开始发送系统内部日报！23')
        message_str += "<br/>"
        message_str += f"<b>{message_list['middle_check_day_qing_day_bi_info']['date']}共有{len(message_list['middle_check_day_qing_day_bi_info']['message_content'])}个中查日清日毕异常记录！</b><br/>"
        for message in message_list["middle_check_day_qing_day_bi_info"]["message_content"]:
            message_str += f"日期：{message['date']}，组别：{message['group']}，款号:{message['style_number']}，中查数量：{message['middle_check_number']}，上一道工序数量：{message['last_process_number']}<br/>"

        _logger.info('开始发送系统内部日报！24')
        message_str += "<br/>"
        message_str += f"<b>{message_list['outsource_order_delay_time_info']['date']}共有{len(message_list['outsource_order_delay_time_info']['message_content'])}个外发逾期异常记录！</b><br/>"
        for message in message_list["outsource_order_delay_time_info"]["message_content"]:
            message_str += f"客户货期：{message['contract_date']}，下单日期：{message['date_order']}，负责人：{message['responsible_person']:3}，\
                工厂：{message['processing_plant']}，订单：{message['order_number']}，订单数量：{message['order_quantity']}，实际交货数：{message['actual_delivered_quantity']}，\
                    存量：{message['stock']}，报次件数：{message['defective_goods']}，逾期件数:{message['number']}，逾期天数：{message['overdue']}<br/>"

        _logger.info('开始发送系统内部日报！25')
        message_str += "<br/>"
        message_str += f"<b>{message_list['client_ware_customer_return_info']['date']}近7天共有{len(message_list['client_ware_customer_return_info']['message_content'])}个客仓客户退货信息！</b><br/>"
        for message in message_list["client_ware_customer_return_info"]["message_content"]:
            message_str += f"退货日期：{message['dDate']}，客户货期：{message['customer_delivery_time']}，订单号：{message['order_number']}，款号：{message['style_number']}，次品退货数:{message['repair_number']}<br/>"


        _logger.info('开始发送系统内部日报！26')
        message_str += "<br/>"
        message_str += f"<b>{message_list['prenatal_preparation_progress_anomaly_info']['date']}共有{len(message_list['prenatal_preparation_progress_anomaly_info']['message_content'])}个计划上线前一天产前准备进度表异常！</b><br/>"
        for message in message_list["prenatal_preparation_progress_anomaly_info"]["message_content"]:
            message_str += f"订单号：{message['订单号']}，款号：{message['款号']}，异常项目:{'，'.join(message['demo_list'])}<br/>"


        _logger.info('开始发送系统内部日报！27')
        message_str += "<br/>"
        message_str += f"<b>{message_list['monthly_plan_overdue_info']['date']}共有{len(message_list['monthly_plan_overdue_info']['message_content'])}个月计划逾期异常信息！</b><br/>"
        for message in message_list["monthly_plan_overdue_info"]["message_content"]:
            message_str += f"客户货期：{message['customer_delivery_time']}，订单号：{message['order_number']}，款号：{message['style_number']}，生产组别:{message['group']}，\
                车间交货差异：{message['difference_delivery']}，后道交货差异：{message['factory_delivery_variance']}<br/>"


        _logger.info('开始发送系统内部日报！28')
        message_str += "<br/>"
        message_str += f"<b>{message_list['first_eight_pieces_abnormal_info']['date']}共有{len(message_list['first_eight_pieces_abnormal_info']['message_content'])}个根据月计划上线2天后无首八件的异常信息！</b><br/>"
        for message in message_list["first_eight_pieces_abnormal_info"]["message_content"]:
            message_str += f"客户货期：{message['customer_delivery_time']}，订单号：{message['order_number']}，款号：{message['style_number']}，上线日期:{message['plan_online_date']}<br/>"


        _logger.info('开始发送系统内部日报！29')
        message_str += "<br/>"
        message_str += f"<b>{message_list['material_summary_sheet_abnormal_info2']['date']}共有{len(message_list['material_summary_sheet_abnormal_info2']['message_content'])}个面辅料汇总计划用量和实际用量异常信息！</b><br/>"
        # for message in message_list["material_summary_sheet_abnormal_info2"]["message_content"]:
        #     message_str += f"客户货期：{message['date_contract']}，订单号：{message['order_id']}，款号：{message['style_number']}，物料名称:{message['material_name']}，" \
        #                    f"计划用量：{message['plan_dosage']}，实际用量：{message['actual_dosage']}<br/>"


        _logger.info('开始发送系统内部日报！30')
        message_str += "<br/>"
        message_str += f"<b>{message_list['outsource_order_no_person_charge']['date']}共有{len(message_list['outsource_order_no_person_charge']['message_content'])}个外发订单未填写负责人的记录！</b><br/>"
        for message in message_list["outsource_order_no_person_charge"]["message_content"]:
            message_str += f"客户货期：{message['customer_delivery_time']}，订单号：{message['order_number']}<br/>"



        _logger.info('发送系统内部日报成功！')

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
