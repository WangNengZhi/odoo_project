from odoo import api, fields, models



class FsnKpiLine(models.Model):
    _inherit = 'fsn_kpi_line'


    ''' 总检'''

    # 客户合格率
    def customer_qualification_rate(self) -> float:
        for record in self:
            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))

            suspension_system_station_summary_list = self.env['suspension_system_station_summary'].sudo().read_group(
                [("dDate", ">=", this_month_start), ("dDate", "<=", this_month_end), ("employee_id", "=", self.fsn_kpi_id.employee_id.id)],
                ['total_quantity'],
                groupby="style_number"
            )

            check_cargo_count = sum(i['total_quantity'] for i in suspension_system_station_summary_list)

            repair_rate_list = []

            for suspension_system_station_summary in suspension_system_station_summary_list:

                repair_number = sum(self.env['suspension_system_rework'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("style_number", "=", suspension_system_station_summary['style_number'][0]),
                    ("qc_type", "=", "尾查")]).mapped("number"))

                repair_rate = int(((repair_number / suspension_system_station_summary['total_quantity']) - 0.03) * 100)

                if repair_rate > 0:
                    repair_rate_list.append(repair_rate)

            
            client_ware_objs = self.env['client_ware'].sudo().search([
                ("dDate", ">=", this_month_start),
                ("dDate", "<=", this_month_end),
                ("general", "like", self.fsn_kpi_id.employee_id.name)
            ])
            for client_ware_obj in client_ware_objs:
                
                client_ware_repair_rate = int((client_ware_obj.repair_ratio / len(client_ware_obj.general.split(" "))) - 3)
                if client_ware_repair_rate > 0:
                    repair_rate_list.append(client_ware_repair_rate)

            evaluation_score = record.score - sum(repair_rate_list)

            return evaluation_score if evaluation_score > 0 else 0
    

    # 总检吊挂效率
    def always_check_efficiency(self) -> float:
        for record in self:

            year, month = record.fsn_kpi_id.year_month.split("-")
            this_month_start, this_month_end = self.set_begin_and_end(int(year), int(month))

            automatic_efficiency_table_objs = self.env['automatic_efficiency_table'].sudo().search([("date", ">=", this_month_start), ("date", "<=", this_month_end), ("employee_id", "=", record.fsn_kpi_id.employee_id.id)])
            
            always_check_efficiency = sum(automatic_efficiency_table_objs.mapped("efficiency")) / len(automatic_efficiency_table_objs)

            evaluation_score = record.score - int(100 - always_check_efficiency)

            return evaluation_score if evaluation_score > 0 else 0