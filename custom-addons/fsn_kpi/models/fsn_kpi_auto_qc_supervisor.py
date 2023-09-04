from odoo import api, fields, models



class FsnKpiLine(models.Model):
    _inherit = 'fsn_kpi_line'


    ''' 品控主管'''

    # 总检返修率
    def always_check_rate_repair(self) -> float:
        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")

            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)


            repair_ratio_list = []

            extensive_repair_list = []

            for day in days_list:
                
                posterior_passage_statistical_objs = self.env['posterior_passage_statistical'].sudo().search([("dDate", "=", day)])
                
                if posterior_passage_statistical_objs:

                    day_repair_ratio_list = posterior_passage_statistical_objs.mapped("repair_ratio")

                    repair_ratio_list.append(sum(day_repair_ratio_list) / len(day_repair_ratio_list))

                    extensive_repair_list.extend(i for i in posterior_passage_statistical_objs.mapped("repair_quantity") if i > 20)

            if repair_ratio_list:
                repair_ratio = sum(repair_ratio_list) / len(repair_ratio_list)
            else:
                repair_ratio = 0
    

            if repair_ratio > 10:
                
                evaluation_score = record.score - (2 * int(repair_ratio - 10)) - (5 * len(extensive_repair_list))
            
            else:

                evaluation_score = record.score - (5 * len(extensive_repair_list))
            

            return evaluation_score if evaluation_score > 0 else 0


    # 客仓返修率
    def client_warehouse_rate_repair(self) -> float:
        for record in self:
            
            year, month = record.fsn_kpi_id.year_month.split("-")

            days_list = self.get_this_month_days(int(year), int(month), self.fsn_kpi_id.employee_id.entry_time, self.fsn_kpi_id.employee_id.is_delete_date)

            days_list = self.get_actual_attendance_days(days_list)

            repair_ratio_list = []

            extensive_repair_list = []

            for day in days_list:

                client_ware_objs = self.env['client_ware'].sudo().search([("dDate", "=", day)])

                if client_ware_objs:

                    day_repair_ratio_list = client_ware_objs.mapped("repair_ratio")

                    repair_ratio_list.append(sum(day_repair_ratio_list) / len(day_repair_ratio_list))

                    extensive_repair_list.extend(i for i in client_ware_objs.mapped("repair_number") if i > 20)

            if repair_ratio_list:
                repair_ratio = sum(repair_ratio_list) / len(repair_ratio_list)
            else:
                repair_ratio = 0

            if repair_ratio > 10:
                evaluation_score = record.score - (3 * int(repair_ratio - 2)) - (5 * len(extensive_repair_list))
            else:
                evaluation_score = record.score - (5 * len(extensive_repair_list))

            return evaluation_score if evaluation_score > 0 else 0