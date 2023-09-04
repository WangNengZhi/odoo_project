from odoo import api, fields, models

class FsnKpiLine(models.Model):
    _inherit = 'fsn_kpi_line'

    ''' 自动考核内置方法'''


    def automatic_assessment(self):
        for record in self:
            record.evaluation_score = getattr(record, record.assess_project.method_name)()

    ''' 摄影师'''
    # 发布完成率
    def release_completion_rate(self) -> float:
        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")

            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)

            percentage_complete = sum(self.env['ec_video_data'].sudo().search_count([("date", "=", day), ("author_id", "=", self.fsn_kpi_id.employee_id.id)]) / 5 for day in days_list) / len(days_list)

            if percentage_complete >= 1:
                return 10.0
            elif percentage_complete >= 0.8:
                return 8.0
            elif percentage_complete >= 0.5:
                return 5.0
            else:
                return 0.0
    

    # 完播率
    def complete_play_rate(self) -> float:
        for record in self:
            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))

            seeding_rate_list = self.env['ec_video_data'].sudo().search([
                ("date", ">=", this_month_start),
                ("date", "<=", this_month_end),
                ("author_id", "=", self.fsn_kpi_id.employee_id.id),
            ]).mapped("seeding_rate")

            seeding_rate = sum(seeding_rate_list) / len(seeding_rate_list)

            if seeding_rate >= 0.5:
                return 20.0
            elif seeding_rate >= 0.3:
                return 15.0
            elif seeding_rate >= 0.2:
                return 10.0
            else:
                 return 5.0


    # 点赞率
    def give_a_like_rate(self) -> float:
        for record in self:
            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))

            thumb_up_rate_list = self.env['ec_video_data'].sudo().search([
                ("date", ">=", this_month_start),
                ("date", "<=", this_month_end),
                ("author_id", "=", self.fsn_kpi_id.employee_id.id),
            ]).mapped("thumb_up_rate")

            seeding_rate = sum(thumb_up_rate_list) / len(thumb_up_rate_list)

            if seeding_rate >= 0.05:
                return 10.0
            elif seeding_rate >= 0.03:
                return 8.0
            elif seeding_rate >= 0.02:
                return 5.0
            else:
                return 0.0

    # 视频引入流量
    def video_introduction_traffic(self) -> float:
        for record in self:
            year, month = record.fsn_kpi_id.year_month.split("-")
            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)

            video_introduction_traffic_list = self.env['ec_flow_channel'].sudo().search([
                ("date", "in", days_list),
            ]).mapped("short_video_diversion_traffic")
            
            video_introduction_traffic = (sum(video_introduction_traffic_list) / len(video_introduction_traffic_list)) / 100

            if video_introduction_traffic >= 0.1:
                return 10.0
            elif video_introduction_traffic >= 0.05:
                return 8.0
            elif video_introduction_traffic >= 0.01:
                return 5.0
            else:
                return 0.0

    # ROI（视频）
    def roi_video(self) -> float:
        for record in self:
            year, month = record.fsn_kpi_id.year_month.split("-")
            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)

            data_list = []

            for day in days_list:
                ec_product_data_objs = self.env['ec_product_data'].sudo().search([("date", "=", day)])

                ec_live_data_collect_objs = self.env['ec_live_data_collect'].sudo().search([("date", "=", day)])

                cost_of_advertising = sum(i.qian_chuan_cost + i.shop_will_push + i.shake_plus for i in ec_live_data_collect_objs) / len(ec_product_data_objs)

                for ec_product_data_obj in ec_product_data_objs:    # 循环商品
                    # 订单数 - 退货数
                    number = ec_product_data_obj.order_quantity - ec_product_data_obj.return_goods_quantity
                    if number:
                        data_list.append(((ec_product_data_obj.price * number) - ((ec_product_data_obj.cost * number) + cost_of_advertising)) / ((ec_product_data_obj.cost * number) + cost_of_advertising))

            roi_video = sum(data_list) / len(data_list)

            if roi_video >= 3:
                return 10.0
            elif roi_video >= 1.8:
                return 8.0
            elif roi_video >= 1.0:
                return 5.0
            else:
                return 0




