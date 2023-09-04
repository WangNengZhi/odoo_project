from datetime import timedelta
from odoo import api, fields, models


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'


    # 获取昨天计划数据
    def get_yesterday_plan_data(self):

        # 获取前一天的日期
        today_time = fields.Datetime.now()
        today = today_time.date() - timedelta(days=1)

        while True:

            # 查询前一天的记录
            planning_slot_obj_list = self.env["planning.slot"].sudo().read_group(
                domain = [('dDate', '=', today)],
                fields = ["staff_group", "plan_number", "actual_number"],
                groupby = ["staff_group"]
                )

            if planning_slot_obj_list:

                for i in planning_slot_obj_list:
                    i["progress_bar"] = (i["actual_number"] / i["plan_number"]) * 100

                break

            else:
                today = today - timedelta(days=1)

        return {"planning_slot_obj_list": planning_slot_obj_list, "today": today}


        # credit_groups = analytic_line_obj.read_group(
        #     domain=domain + [('amount', '>=', 0.0)],
        #     fields=['account_id', 'currency_id', 'amount'],
        #     groupby=['account_id', 'currency_id'],
        #     lazy=False,
        # )