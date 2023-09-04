
from odoo import http
import json

from collections import Counter


class WorkshopPieChart(http.Controller):
    # 获取薪资数据
    @http.route('/get_salary_list', auth='public', type='http', methods=['GET'])
    def get_salary_list(self, **kw):

        date = kw.get("date")

        salary_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("is_delete_date", "=", False),
            ("contract", "in", ["正式工(计件工资)", "临时工", "实习生(计件)"])
            ])
        

        salary_list = [
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 < 4000)), "name": "4000以下" },
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 >= 4000 and x.salary_payable2 < 5000)), "name": "4000-4999" },
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 >= 5000 and x.salary_payable2 < 6000)), "name": "5000-5999" },
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 >= 6000 and x.salary_payable2 < 7000)), "name": "6000-6999" },
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 >= 7000 and x.salary_payable2 < 8000)), "name": "7000-7999" },
            { "value": len(salary_objs.filtered(lambda x: x.salary_payable2 >= 8000)), "name": "8000及以上" },
        ]


        return json.dumps({'status': "1", 'messages': "成功", 'data': salary_list})

    # 获取效率数据
    @http.route('/get_efficiency_list', auth='public', type='http', methods=['GET'])
    def get_efficiency_list(self, **kw):

        date = kw.get("date")

        salary_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("is_delete_date", "=", False),
            ("contract", "in", ["正式工(计件工资)", "临时工", "实习生(计件)"])])

        efficiency_list = [
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio < 30)), "name": "30以下" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 30 and x.month_workpiece_ratio < 40)), "name": "30-39.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 40 and x.month_workpiece_ratio < 50)), "name": "40-49.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 50 and x.month_workpiece_ratio < 60)), "name": "50-59.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 60 and x.month_workpiece_ratio < 70)), "name": "60-69.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 70 and x.month_workpiece_ratio < 80)), "name": "70-79.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 80 and x.month_workpiece_ratio < 90)), "name": "80-89.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 90 and x.month_workpiece_ratio < 100)), "name": "90-99.99" },
            { "value": len(salary_objs.filtered(lambda x: x.month_workpiece_ratio >= 100)), "name": "100及以上" },
        ]


        return json.dumps({'status': "1", 'messages': "成功", 'data': efficiency_list})

    # 获取日均薪资数据
    @http.route('/get_day_average_salary_list', auth='public', type='http', methods=['GET'])
    def get_day_average_salary_list(self, **kw):

        date = kw.get("date")

        boundary_list = [4000, 5000, 6000, 7000, 8000]

        salary_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("is_delete_date", "=", False),
            ("contract", "in", ["正式工(计件工资)", "临时工", "实习生(计件)"])])

        # 获取应出勤天数
        collection_should_attend = Counter(salary_objs.mapped('should_attend'))
        should_attend = collection_should_attend.most_common(1)[0][0]


        # 获取边界
        def get_boundary(boundary):
            return int(boundary / should_attend)


        day_average_boundary_list = list(map(get_boundary, boundary_list))


        day_average_salary_list = [
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary < day_average_boundary_list[0])), "name": f"{day_average_boundary_list[0]}({boundary_list[0]})以下" },
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[0] and x.day_average_salary < day_average_boundary_list[1])), "name": f"{day_average_boundary_list[0]}-{day_average_boundary_list[1]}({boundary_list[0]}-{boundary_list[1]-1})" },
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[1] and x.day_average_salary < day_average_boundary_list[2])), "name": f"{day_average_boundary_list[1]}-{day_average_boundary_list[2]}({boundary_list[1]}-{boundary_list[2]-1})" },
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[2] and x.day_average_salary < day_average_boundary_list[3])), "name": f"{day_average_boundary_list[2]}-{day_average_boundary_list[3]}({boundary_list[2]}-{boundary_list[3]-1})" },
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[3] and x.day_average_salary < day_average_boundary_list[4])), "name": f"{day_average_boundary_list[3]}-{day_average_boundary_list[4]}({boundary_list[3]}-{boundary_list[4]-1})" },
            { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[4])), "name": f"{day_average_boundary_list[4]}({boundary_list[4]})及以上" },
        ]


        return json.dumps({'status': "1", 'messages': "成功", 'data': day_average_salary_list})



    # 获取日均薪资数据(整数分布)
    @http.route('/get_day_average_salary_integer_list', auth='public', type='http', methods=['GET'])
    def get_day_average_salary_integer_list(self, **kw):

        date = kw.get("date")

        day_average_boundary_list = [200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300]

        salary_objs = http.request.env["payroll1"].sudo().search([
            ("date", "=", date),
            ("is_delete_date", "=", False),
            ("contract", "in", ["正式工(计件工资)", "临时工", "实习生(计件)"])])
        day_average_salary_list = []
        for index, value in enumerate(day_average_boundary_list):
            if index == 0:
                day_average_salary_list.append(
                    {"value": len(salary_objs.filtered(lambda x: x.day_average_salary < value)), "name": f"{value}以下" }
                )
                day_average_salary_list.append(
                    { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[index] and x.day_average_salary < day_average_boundary_list[index + 1])), "name": f"{day_average_boundary_list[index]}-{day_average_boundary_list[index + 1]-1}"},
                )
            elif index == 10:
                day_average_salary_list.append(
                    {"value": len(salary_objs.filtered(lambda x: x.day_average_salary >= value)), "name": f"{value}及以上" }
                )
            else:
                day_average_salary_list.append(
                    { "value": len(salary_objs.filtered(lambda x: x.day_average_salary >= day_average_boundary_list[index] and x.day_average_salary < day_average_boundary_list[index + 1])), "name": f"{day_average_boundary_list[index]}-{day_average_boundary_list[index + 1]-1}"},
                )

        return json.dumps({'status': "1", 'messages': "成功", 'data': day_average_salary_list})