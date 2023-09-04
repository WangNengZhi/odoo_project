from datetime import datetime, timedelta
from collections import defaultdict
from odoo import models, fields, api


class working_hours_and_processes(models.TransientModel):
    """工时工序日报"""
    _inherit = "fsn_daily"

    def obtain_work_hours_operation(self):
        """获取工时工序款号价格"""
        # 获取当前日期
        # current_date = datetime.now().date()
        # 获取年初日期
        # year_start_date = datetime(current_date.year, 1, 1).date()

        today_date = datetime.now().date()
        # 计算前三天的日期
        three_days_ago = today_date - timedelta(days=3)

        working_hours = self.env['on.work'].search([('date1', '>=', three_days_ago.strftime('%Y-%m-%d')),
                                                    ('date1', '<=',today_date.strftime('%Y-%m-%d'))])
        today = datetime.now().date()
        result_list = []

        for working in working_hours:
            if working.contract_type == "正式工(计件工资)":
                formal_worker = self.env['work.work'].search([('order_number', '=', working.order_number.id),
                                                    ('employee_id', '=', working.employee_id)])
                for formal in formal_worker:
                    if formal.standard_price != working.standard_price:
                        result_dict = {
                            'date': working.date1,
                            'order_no': working.order_no.order_number,
                            'style_number': working.order_number.style_number,
                            'employee_id': working.employee_id,
                            'standard_price': working.standard_price,
                            'timesheet_standard_price': formal.standard_price
                        }
                        result_list.append(result_dict)

            if working.contract_type == "临时工":
                temporary_workers = self.env['temporary_workers_apply'].search([('order_id', '=', working.order_no.id),
                                                                                ('style_number', '=', working.order_number.id),
                                                                                ('process_no', '=', working.employee_id)])

                for temporary in temporary_workers:
                    if temporary.apply_price != working.standard_price:
                        result_dict = {
                            'date': working.date1,
                            'order_no': working.order_no.order_number,
                            'style_number': working.order_number.style_number,
                            'employee_id': working.employee_id,
                            'standard_price': working.standard_price,
                            'timesheet_standard_price': temporary.apply_price
                        }
                        result_list.append(result_dict)
        return {'today': today, 'result': result_list}

    def number_of_working_hours_and_processes(self):
        """获取工时工序现场工序件数"""

        current_date = datetime.now().date()
        # # # 获取年初日期
        # year_start_date = datetime(current_date.year, 1, 1).date()

        today_date = datetime.now().date()
        # 计算前三天的日期
        three_days_ago = today_date - timedelta(days=3)
        #
        # # processes = self.env['on.work'].search([('date1', '>=', three_days_ago.strftime('%Y-%m-%d')),
        # #                                         ('date1', '<=', today_date.strftime('%Y-%m-%d'))])
        #
        # processes = self.env['on.work'].search([('date1', '>=', year_start_date),
        #                                         ('date1', '<=', current_date)])
        #
        # # 使用字典来记录每个订单号和款号的工序号的累计工时
        # sum_by_key = {}
        #
        # for process in processes:
        #     key = (process.order_no.id, process.order_number.id, process.employee_id)
        #     if key not in sum_by_key:
        #         sum_by_key[key] = process.over_number
        #     else:
        #         sum_by_key[key] += process.over_number
        #
        # result_list = []
        #
        # for key, value in sum_by_key.items():
        #     order_number_id, style_number_id, employee_id = key
        #     production_schedules = self.env['schedule_production'].search([
        #         ('order_number', '=', order_number_id),
        #         ('style_number', '=', style_number_id),
        #     ])
        #
        #     for production in production_schedules:
        #         if production.qualified_stock != value:
        #             result_dict = {
        #                 "order_number": production.order_number.order_number,
        #                 "style_number": production.style_number.style_number,
        #                 'process_number': employee_id,
        #                 "number_of_working_hours": value,
        #                 "production_progress_pieces": production.qualified_stock,
        #             }
        #             result_list.append(result_dict)
        # return {'today': current_date, 'result': result_list}

        processes = self.env['on.work'].search([('date1', '>=', three_days_ago.strftime('%Y-%m-%d')),
                                                ('date1', '<=', today_date.strftime('%Y-%m-%d'))])

        # 使用字典来记录每个订单号和款号的累计qualified_stock值
        sum_by_key = defaultdict(int)

        for process in processes:
            # key = (process.order_no.id, process.order_number.id, process.employee_id)
            key = (process.order_no.id, process.order_number.id)
            sum_by_key[key] += process.over_number

        result_list = []

        for key, value in sum_by_key.items():
            # employee_id, order_number_id, style_number_id = key
            order_number_id, style_number_id = key
            total_qualified_stock = value

            production_schedules = self.env['schedule_production'].search([
                ('order_number', '=', order_number_id),
                ('style_number', '=', style_number_id),
            ])

            for production in production_schedules:
                total_qualified_stock += production.qualified_stock

                if total_qualified_stock != value:
                    result_dict = {
                        "order_number": production.order_number.order_number,
                        "style_number": production.style_number.style_number,
                        "number_of_working_hours": value,
                        # 'process_number': employee_id,
                        "production_progress_pieces": total_qualified_stock,
                    }
                    result_list.append(result_dict)
        return {'today': current_date, 'result': result_list}


class Channel(models.Model):
    _inherit = 'mail.channel'

    def send_daily_report_of_working_hours_and_processes(self):
        """发送工时工序日报，现场工序原单价和工时单单价不符"""
        message_content = {}

        message_content['hours_operation'] = self.env['fsn_daily'].sudo().obtain_work_hours_operation()

        message_content['number_of_working'] = self.env['fsn_daily'].sudo().number_of_working_hours_and_processes()

        message_str = f"<b>{message_content['hours_operation']['today']}共有：" \
                      f"{len(message_content['hours_operation']['result'])}条现场工序源单价与工时单原单价不符</b><br/>"
        # for message in message_content['hours_operation']['result']:
        #     message_str += f"日期：{message['date']}，订单号：{message['order_no']}，款号：{message['style_number']}，" \
        #                    f"工序号：{message['employee_id']}，现场工序原单价：{message['standard_price']}， 工时单原单价：{message['timesheet_standard_price']}<br/>"

        message_str += '<br/>'

        message_str += f"<b>{message_content['number_of_working']['today']}共有：" \
                       f"{len(message_content['number_of_working']['result'])}条现场工序件数与生产进度表存量不符</b><br/>"
        # for message in message_content['number_of_working']['result']:
        #     message_str += f"订单号：{message['order_number']}，款号：{message['style_number']}，现场工序件数：{message['number_of_working_hours']}，生产进度存量：{message['production_progress_pieces']}<br/>"

        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].browse(self.env.ref("fsn_timed_task.fsn_ie_daily_inspect_channel").id)

        channel.sudo().message_post(body=message_str, author_id=odoobot_id, message_type="notification",
                                    subtype_xmlid="mail.mt_comment")
        return channel
