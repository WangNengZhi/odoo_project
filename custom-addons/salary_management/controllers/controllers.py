# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import ValidationError
from odoo import http
import pymssql
import json
import calendar
import datetime




class HrPay(http.Controller):

    @http.route('/salary_refresh', auth='user', type='json')
    def sync_record(self, **kw):
        start_time = kw['start_time']
        end_time = kw['end_time']
        totle_time = str(start_time) + '-' + str(end_time)

        # 只查询 离职时间大于当月1号 并且入职时间小于当月当月最后一天 已经未离职的员工
        min_time = datetime.date(int(start_time), int(end_time), 1)
        last_day = calendar.monthrange(int(start_time), int(end_time))[1]
        max_time = datetime.date(int(start_time), int(end_time), last_day)
        demo = http.request.env["hr.employee"].sudo().search([('entry_time', '<=', max_time), '|',("is_delete_date", ">=", min_time), ('is_delete_date', '=', False)])

        math_month, month_math = calendar.monthrange(int(start_time), int(end_time))
        #  最大的时间 month_math      最低的时间1
        new_time = str(start_time) + '-' + str(end_time) + '-' + str(1)
        new_time = datetime.datetime.strptime(new_time, '%Y-%m-%d')

        end_time = str(start_time) + '-' + str(end_time) + '-' + str(month_math)
        for record in demo:


            if record.is_it_a_temporary_worker == "外包(计时)" or record.is_it_a_temporary_worker == "外包(计件)":

                continue

            demo1 = http.request.env["salary"].sudo().search([('date', '=', totle_time), ('name', '=', record.name)])
            if demo1:
                pass
            else:
                if record.entry_time:
                    entry_time = datetime.datetime.strptime(str(record.entry_time), '%Y-%m-%d')
                else:
                    raise ValidationError('%s入职时间没有写' % record.name)
                if record.is_delete_date:
                    is_delete_date = datetime.datetime.strptime(str(record.is_delete_date), '%Y-%m-%d')
                    if entry_time <= new_time and is_delete_date > new_time:
                        http.request.env["salary"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                    elif entry_time > new_time and is_delete_date > new_time:
                        http.request.env["salary"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                else:
                    if entry_time <= new_time:
                        http.request.env["salary"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                    elif entry_time > new_time:
                        http.request.env["salary"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })

        return json.dumps({'status': "1", 'messages': "成功！"})



    @http.route('/get_payroll1_record', auth='user', type='json')
    def get_payroll1_record(self, **kw):
        start_time = kw['start_time']
        end_time = kw['end_time']
        totle_time = str(start_time) + '-' + str(end_time)

        # 只查询 离职时间大于当月1号 并且入职时间小于当月当月最后一天 已经未离职的员工
        min_time = datetime.date(int(start_time), int(end_time), 1)
        last_day = calendar.monthrange(int(start_time), int(end_time))[1]
        max_time = datetime.date(int(start_time), int(end_time), last_day)
        demo = http.request.env["hr.employee"].sudo().search([('entry_time', '<=', max_time), '|',("is_delete_date", ">=", min_time), ('is_delete_date', '=', False)])

        math_month, month_math = calendar.monthrange(int(start_time), int(end_time))
        #  最大的时间 month_math      最低的时间1
        new_time = str(start_time) + '-' + str(end_time) + '-' + str(1)
        new_time = datetime.datetime.strptime(new_time, '%Y-%m-%d')

        end_time = str(start_time) + '-' + str(end_time) + '-' + str(month_math)
        for record in demo:


            if record.is_it_a_temporary_worker == "外包(计时)" or record.is_it_a_temporary_worker == "外包(计件)":

                continue

            demo1 = http.request.env["payroll1"].sudo().search([('date', '=', totle_time), ('name', '=', record.name)])
            if demo1:
                pass
            else:
                if record.entry_time:
                    entry_time = datetime.datetime.strptime(str(record.entry_time), '%Y-%m-%d')
                else:
                    raise ValidationError('%s入职时间没有写' % record.name)
                if record.is_delete_date:
                    is_delete_date = datetime.datetime.strptime(str(record.is_delete_date), '%Y-%m-%d')
                    if entry_time <= new_time and is_delete_date > new_time:
                        http.request.env["payroll1"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                    elif entry_time > new_time and is_delete_date > new_time:
                        http.request.env["payroll1"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                else:
                    if entry_time <= new_time:
                        http.request.env["payroll1"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })
                    elif entry_time > new_time:
                        http.request.env["payroll1"].sudo().create({
                            'date': totle_time,
                            'name': record.id
                        })

        return json.dumps({'status': "1", 'messages': "成功！"})



    # 一件生成日历周六周日
    @http.route('/generate_calendar', auth='user', type='json')
    def generate_calendar(self, **kw):

        # 获取指定月份的全部天数
        year, month = kw["month"].split("-")
        year = int(year)
        month = int(month)
        num_days = calendar.monthrange(year, month)[1]
        days = [datetime.date(year, month, day) for day in range(1, num_days+1)]

        for day in days:
            if day.weekday() + 1 == 7:

                custom_calendar_ids = http.request.env["custom.calendar"].sudo().search([("date", "=", day)])
                if custom_calendar_ids:
                    pass
                else:
                    http.request.env["custom.calendar"].sudo().create({
                        'date': day,
                        'reason': "周日",
                    })
            elif day.weekday() + 1 == 6:

                custom_calendar_ids = http.request.env["custom.calendar"].sudo().search([("date", "=", day)])
                if custom_calendar_ids:
                    pass
                else:
                    # 上周六
                    last_week_day = day - datetime.timedelta(days=7)
                    last_week_custom_calendar_ids = http.request.env["custom.calendar"].sudo().search([("date", "=", last_week_day)])

                    custom_calendar_id = http.request.env["custom.calendar"].sudo().create({
                        'date': day,
                        'reason': "周六,仅双休休息",
                    })
                    for line in custom_calendar_id.custom_calendar_line_ids:
                            line.sudo().write({
                                "state": "仅双休休息"
                            })

            else:
                pass

        return json.dumps({'status': "1", 'messages': "成功！"})


    @http.route('/query_payroll1_restriction_switch', auth='public', type='http', methods=['GET'])
    def query_payroll1_restriction_switch(self, **kw):

        model_name = kw.get("model_name")

        print(model_name)

        ir_model_id = http.request.env['ir.model']._get(model_name).id

        salary_lock_setting_obj = http.request.env["salary_lock_setting"].sudo().search([("model_id", "=", ir_model_id)])

        return salary_lock_setting_obj.is_operable


    @http.route('/set_payroll1_restriction_switch', auth='public', type='http', methods=['GET'])
    def set_payroll1_restriction_switch(self, **kw):

        model_name = kw.get("model_name")
        is_operable_value = kw.get("is_operable_value")

        ir_model_id = http.request.env['ir.model']._get(model_name).id

        salary_lock_setting_obj = http.request.env["salary_lock_setting"].sudo().search([("model_id", "=", ir_model_id)])

        salary_lock_setting_obj.is_operable = is_operable_value