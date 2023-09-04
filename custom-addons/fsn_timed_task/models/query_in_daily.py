from odoo import models, fields, api
from datetime import datetime, timedelta


class QueryInDaily(models.TransientModel):
    """中查罚"""
    _inherit = "fsn_daily"

    def quantity_discrepancy(self):
        """"""
        # 　获取前一天的日期
        # 获取昨天的日期，去除每周日
        previous_day = datetime.now().date() - timedelta(days=1)

        if previous_day.weekday() == 6:  # 如果昨天是周日，不执行查询
            deliveries = []
        else:
            deliveries = self.env['wechat.delivery'].search([('date', '>=', previous_day)])
        result_list = []
        unique_list = []
        for deliver in deliveries:
            # 获取应交数
            hangs = self.env['suspension_system_station_summary'].search([('dDate', '>=', deliver.date),
                                                                          ('group', '=', deliver.group.id),
                                                                          ('order_number_show', '=',
                                                                           deliver.order_number),
                                                                          ('MONo', '=', deliver.style_number)])

            for han in hangs:
                if deliver.number_of_bulk_deliveries < han.total_quantity:
                    result_list.append({'name': deliver.check_in_name.id,
                                        'delivery': deliver.number_of_bulk_deliveries,
                                        'total': han.total_quantity,
                                        'order_number': han.order_number_show,
                                        'style_number': han.MONo
                                        })
        unique_dict = {}
        for result in result_list:
            key = result['order_number'] + result['style_number']
            unique_dict[key] = result
            unique_list = list(unique_dict.values())
        return unique_list


    def undelivered(self):
        """未交货处罚"""
        query_name = self.env['hr.employee'].search(
            [("job_id.name", "=", "中查"), ("is_delete", "=", False), ('name', '=', '郭长洲')])
        query_five = self.env['hr.employee'].search(
            [("job_id.name", "=", "中查"), ("is_delete", "=", False), ('name', '=', '石柳')])

        previous_day = datetime.now().date() - timedelta(days=1)
        result_list = []

        deliveries = self.env['wechat.delivery'].search([('date', '=', previous_day)])

        is_group_one_found = any(deliver.group.group == '车缝二组' for deliver in deliveries)
        is_group_five_found = any(deliver.group.group == '车缝五组' for deliver in deliveries)

        if not is_group_one_found:
            result_list.append({
                'name': query_name.id
            })

        if not is_group_five_found:
            result_list.append({
                'name': query_five.id
            })

        return result_list
