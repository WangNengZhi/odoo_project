from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
from datetime import timedelta, datetime
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)

from utils import weixin_utils


class Channel(models.Model):
    _inherit = 'mail.channel'


    def get_sale_order_not_paid(self):
        """获取销售订单大于30天未付款"""
        date_threshold = datetime.now() - timedelta(days=30)

        domain = [
            ('date', '<', date_threshold.strftime('%Y-%m-%d')),
            ('fsn_payment_state', '=', '未付款'),
            # ('fsn_approval_status', '=', "未审批")
        ]
        
        orders = self.env['fsn_sales_order'].search(domain)
        # print([{"name": i.name, "fsn_delivery_date": i.fsn_delivery_date, "fsn_customer": i.fsn_customer_id.name, "amount": sum(i.after_tax_total)} for i in orders])
        results = []
        for order in orders:
            total_amount = sum([order.after_tax_total])
            result = {
                "name": order.name,
                "fsn_delivery_date": order.fsn_delivery_date,
                "fsn_customer": order.fsn_customer_id.name,
                "amount": total_amount
            }
            results.append(result)
        return results


    def get_sale_order_paid(self):
        """获取销售订单已付款"""
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = start_date + relativedelta(day=31)
        domain = [
            ('fsn_delivery_date', '>=', start_date),
            ('fsn_delivery_date', '<=', end_date),
            ('fsn_payment_state', '=', '已付款'),
        ]
        orders = self.env['fsn_sales_order'].search(domain)
        return orders.mapped('name')

    def get_sale_order_not_been_paid(self):
        """获取销售订单未付款"""
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = start_date + relativedelta(day=31)
        domain = [
            ('fsn_delivery_date', '>=', start_date),
            ('fsn_delivery_date', '<=', end_date),
            ('fsn_payment_state', '=', '未付款')
        ]

        orders = self.env['fsn_sales_order'].search(domain)
        return orders.mapped('name')

    def get_current_month_order_amount(self):
        """获取当月订单额"""
        today = date.today()
        # 计算当月起始日期和结束日期
        start_date = date(today.year, today.month, 1)
        end_date = start_date + relativedelta(day=31)

        domain = [
            ('fsn_delivery_date', '>=', start_date),
            ('fsn_delivery_date', '<=', end_date),
        ]
        order_amount = self.env['fsn_sales_order'].search(domain).mapped('after_tax_total')
        total_amount = sum(order_amount)
        result = {'amount': total_amount}
        return result

    def get_no_sales_order_number(self):
        """获取销售订单没有销售订单号"""
        order_list = self.env['fsn_sales_order'].search([('sale_pro_ids', '=', False)])
        return order_list
    

    def get_time_limit_not_business_opportunity_record(self, today):
        ''' 获取期限无商机的销售人员'''
        
        emp_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False), ("job_id.name", "=", "销售专员")])

        abnormal_list = []

        for emp_obj in emp_objs:

            def get_emp_recruitment_record_list(n):
                for i in range(1, n+1):
                    temp_date = today - timedelta(days=i)
                    if self.env['fsn_business_opportunity'].sudo().search([("date", "=", temp_date), ("sales_staff_id", "=", emp_obj.id)]):
                        yield False
                    else:
                        yield True

            if all(get_emp_recruitment_record_list(3)):
                
                abnormal_list.append({"emp_id": emp_obj.id, "name": emp_obj.name})
  
        return {"date": today, "message_content": abnormal_list}
    
    def all_unpaid_orders(self):
        """获取全部未付款订单以及金额"""
        unpaid_orders = self.env['fsn_sales_order'].search([('fsn_payment_state', '=', '未付款')])
        total_amount = sum(order.after_tax_total for order in unpaid_orders)
        result = {
            "unpaid_order_count": len(unpaid_orders),
            "total_amount": total_amount
        }
        return result


    def unfinished_orders(self):
        """获取30天未完成订单客户名"""
        date_threshold = datetime.now() - timedelta(days=30)

        names = []

        orders = self.env['fsn_sales_order'].search([('date', '<', date_threshold.strftime('%Y-%m-%d')),
                                                     ('state', '=', '未完成')])
        for order in orders:
            names.append({
                'name': order.fsn_customer_id.name
            })
        return names

    def send_sales_daily_newspaper_messages(self, today):
        ''' 发送销售频道日报'''

        message_content = {}
        # 销售订单大于30天未付款
        message_content['get_sale_order_not_paid'] = self.get_sale_order_not_paid()

        # 销售订单已付款
        message_content['get_sale_order_paid'] = self.get_sale_order_paid()
        #  销售订单未付款
        message_content['get_sale_order_not_been_paid'] = self.get_sale_order_not_been_paid()
        # 当月订单额
        message_content['get_current_month_order_amount'] = self.get_current_month_order_amount()
        # 获取销售订单没有销售订单号
        message_content['get_no_sales_order_number'] = self.get_no_sales_order_number()
        # 获取期限无商机的销售人员
        message_content['time_limit_not_business_opportunity_record'] = self.get_time_limit_not_business_opportunity_record(today)

        # 获取全部未付款订单以及金额
        message_content['unpaid_order'] = self.all_unpaid_orders()

        # 获取30天未完成订单客户名
        message_content['unfinished_orders'] = self.unfinished_orders()


        self.send_workwx_newspaper_messages(today, message_content)

        # 消息
        message_str = f"{today}:<br/>"
        message_str += f"全部未付款订单：{message_content['unpaid_order']['unpaid_order_count']}条，金额：{message_content['unpaid_order']['total_amount']}<br/>"
        message_str += f"当月订单额：{message_content['get_current_month_order_amount']['amount']}元<br/>"
        message_str += f"当月已付款订单数：{len(message_content['get_sale_order_paid'])}个<br/>"
        message_str += f"当月未付款订单数：{len(message_content['get_sale_order_not_been_paid'])}个<br/>"

        # message_str += f"{len(message_content['get_sale_order_not_paid'])}条销售订单大于30天未完成，总金额{(i['amount'] for i in message_content['get_sale_order_not_paid'])}:<br/>"
        message_str += f"{len(message_content['get_sale_order_not_paid'])}条销售订单大于30天未完成，总金额{sum(i['amount'] for i in message_content['get_sale_order_not_paid'])}:<br/>"
        for i in message_content["get_sale_order_not_paid"]:
            message_str += f"销售订单编号：{i['name']}，合同日期：{i['fsn_delivery_date']}，客户：{i['fsn_customer']}<br/>"
        message_str += f"{len(message_content['get_no_sales_order_number'])}条销售订单沒有生产订单号:<br/>"
        for order in message_content['get_no_sales_order_number']:
            message_str += f"销售订单号：{order.name}<br/>"

        message_str += f"{len(message_content['unfinished_orders'])}条销售订单大于30天未完成客户名称<br/>"
        for unfinished in message_content['unfinished_orders']:
            message_str += f"客户名称：{unfinished['name']}"

        message_str += "<br/>"

        message_str += f"{len(message_content['time_limit_not_business_opportunity_record']['message_content'])}条连续三天没有商机记录:<br/>"
        for messges in message_content['time_limit_not_business_opportunity_record']['message_content']:
            message_str += f"员工：{messges['name']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.browse(self.env.ref("fsn_timed_task.fsn_sales_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel


    def send_workwx_newspaper_messages(self, today, message_content):
        ''' 发送企业微信销售日报'''

        messages_list = []

        get_sale_order_paid = f"{today}:\n"
        get_sale_order_paid += f"当月订单额：{message_content['get_current_month_order_amount']['amount']}元\n"
        get_sale_order_paid += f"当月已付款订单数：{len(message_content['get_sale_order_paid'])}个\n"
        get_sale_order_paid += f"当月未付款订单数：{len(message_content['get_sale_order_not_been_paid'])}个\n"
        get_sale_order_paid += f"{len(message_content['get_sale_order_not_paid'])}条销售订单大于30天未付款:\n"
        for i in message_content["get_sale_order_not_paid"]:
            get_sale_order_paid += f"销售订单编号：{i['name']}，合同日期：{i['fsn_delivery_date']}，客户：{i['fsn_customer']}\n"
        get_sale_order_paid += f"{len(message_content['get_no_sales_order_number'])}条销售订单沒有生产订单号:\n"
        for order in message_content['get_no_sales_order_number']:
            get_sale_order_paid += f"销售订单号：{order.name}\n"
        messages_list.append(get_sale_order_paid)

        def send_weixin_messages(messages):
            weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.SALES_GROUP)  # 销售群

        for messages in messages_list:
            send_weixin_messages(messages)
