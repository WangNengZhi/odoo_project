from odoo import api, fields, models



class FsnKpiLine(models.Model):
    _inherit = 'fsn_kpi_line'


    ''' 中查'''

    # 生产过程控制
    def middle_check_process_control(self):
        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))


            dg_total_quantity_list = self.env['suspension_system_station_summary'].sudo().search([
                ("employee_id", "=", self.fsn_kpi_id.employee_id.id),
                ("dDate", ">=", this_month_start),
                ("dDate", "<=", this_month_end)
            ]).mapped("total_quantity")

            print(dg_total_quantity_list)


            rework_number_list = self.env['suspension_system_rework'].sudo().search([
                ("employee_id", "=", self.fsn_kpi_id.employee_id.id),
                ("date", ">=", this_month_start),
                ("date", "<=", this_month_end)
            ]).mapped("number")

            print(rework_number_list)

            value = record.score - int((sum(rework_number_list) / sum(dg_total_quantity_list)) * 100)

            return value if value > 0 else 0


    # 漏查
    def middle_check_missed(self):
        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))

            suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([("dDate", ">=", this_month_start), ("dDate", "<=", this_month_end), ("employee_id", "=", record.fsn_kpi_id.employee_id.id)])
            
            suspension_system_rework_objs = self.env['suspension_system_rework'].sudo().search([("date", ">=", this_month_start), ("date", "<=", this_month_end), ("employee_id", "=", record.fsn_kpi_id.employee_id.id)])

            missed_rate = sum(suspension_system_rework_objs.mapped("number")) / sum(suspension_system_station_summary_objs.mapped("total_quantity"))

            middle_check_missed = record.score - int(missed_rate)

            return middle_check_missed if middle_check_missed > 0 else 0


    # 日清日币
    def middle_check_day_qing_day_bi(self):

        map_group = {
            "车缝一组": "1",
            "车缝二组": "2",
            "车缝三组": "3",
            "车缝四组": "4",
            "车缝五组": "5",
            "车缝六组": "6",
            "车缝七组": "7",
            "车缝八组": "8",
            "车缝九组": "9",
        }

        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")
            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)

            month_stranded_number_list = []

            for day in days_list:

                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", "=", day),
                    ("employee_id", "=", self.fsn_kpi_id.employee_id.id),
                    ("group.department_id", "=", "车间")
                ])
                
                stranded_number_list = self.env['day_qing_day_bi'].sudo().search_read([("date", "=", day), ("group", "=", map_group.get(suspension_system_station_summary_objs.mapped("group").group))], ['stranded_number'])

                month_stranded_number_list.extend(i['stranded_number'] for i in stranded_number_list)

            score = record.score - sum(month_stranded_number_list)

            return score if score > 0 else 0