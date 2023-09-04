# -*- coding: utf-8 -*-
from cmath import log
from dbm import dumb
from lib2to3.pgen2 import token
import re
from odoo import http
import jinja2
import json
from datetime import date, timedelta, datetime
import requests
import itertools
import re
from operator import itemgetter



loader = jinja2.PackageLoader('custom-addons.fsn_data_screen', "static")
env = jinja2.Environment(loader=loader, autoescape=True)



class FsnDataScreen(http.Controller):

    # 加载页面
    @http.route('/group_output/group_output/', auth='public')
    def group_output(self, **kw):

        template = env.get_template('/src/xml/index.html')    # 获取一个模板文件
        page = template.render()   # 渲染

        return page


    # 获取吊挂接口信息
    @http.route('/get_dg_api_messages/', auth='public', type='http', methods=['GET'])
    def get_dg_api_messages(self, **kw):

        start_time = datetime.now()
        # 开始日期:今天日期
        start_date = start_time.date()
        # 结束日期:明天日期
        end_date = start_date + timedelta(days=1)

        dg_host = http.request.env.company.dg_host      # ip
        dg_port = http.request.env.company.dg_port      # 端口号

        data = {
            "dg_host": dg_host,
            "dg_port": dg_port,
            "start_date": str(start_date),
            "end_date": str(end_date)
            }

        return json.dumps(data)


    # 获取吊挂组信息
    @http.route('/get_check_position_settings/', auth='public', type='http', methods=['GET'])
    def get_check_position_settings(self, **kw):

        start_time = datetime.now()
        # 开始日期:今天日期
        start_date = start_time.date()
        # 结束日期:明天日期
        end_date = start_date + timedelta(days=1)

        dg_host = http.request.env.company.dg_host      # ip
        dg_port = http.request.env.company.dg_port      # 端口号

        check_position_settings_objs = http.request.env["check_position_settings"].sudo().search([])

        tem_list = []

        for check_position_settings_obj in check_position_settings_objs:

            line_list = []

            for position_line_obj in check_position_settings_obj.position_line_ids:
                line_list.append(position_line_obj.position)

            tem_list.append({"group": check_position_settings_obj.group, "line": line_list})

        data = {
            "data": tem_list,
            "dg_host": dg_host,
            "dg_port": dg_port,
            "start_date": str(start_date),
            "end_date": str(end_date)
            }

        return json.dumps(data)


    # 获取FSNERP吊挂系统明细信息
    @http.route('/get_fsn_sys_dg_detail/', auth='public', type='http', methods=['GET'])
    def get_fsn_sys_dg_detail(self, **kw):

        today_time = datetime.now()
        # 今天日期
        today = today_time.date()

        # dd = '2021-12-24 11:00:00'
        # dd = datetime.strptime(dd, "%Y-%m-%d %H:%M:%S").date()

        # 查询当天的吊挂系统产量产值记录，按员工排序
        objs = http.request.env["suspension_system_station_summary"].sudo().search([("dDate", "=", today)], order="employee_id")

        data_list = []

        for employee_id, employee_id_objs in itertools.groupby(objs, key=lambda x:(x.employee_id.id)):     # 再按站号, 员工, 款号分组

            employee_id_objs_list = list(employee_id_objs)   # 转换成列表

            group = employee_id_objs_list[0].group.group  # 组别
            staff_name = employee_id_objs_list[0].employee_id.name     # 员工名称
            output = 0  # 产量
            production_value = 0    # 产值
            workpiece_ratio = 0     # 效率

            for employee_id_obj in employee_id_objs_list:

                output = output + employee_id_obj.total_quantity
                production_value = production_value + employee_id_obj.production_value
                workpiece_ratio = workpiece_ratio + employee_id_obj.workpiece_ratio

            data_list.append({
                "group": group,     # 组别
                "staff_name": staff_name,   # 员工名称
                "output": output,   # 产量
                "production_value": production_value,   # 产值
                "workpiece_ratio": workpiece_ratio,     # 效率
            })

            data_list.sort(key=lambda x: x["group"], reverse=False)     # 先按站号, 员工, 款号排序

        return json.dumps({"data": data_list})


    # 获取款号价格
    @http.route('/get_mono_price/', auth='public', type='http', methods=['GET'])
    def get_mono_price(self, **kw):

        style_number = kw["mono"]   # 款式编号

        ib_detail_obj = http.request.env["ib.detail"].sudo().search([("style_number", "=", style_number.strip())])

        return json.dumps({"price": ib_detail_obj.price})




    # 获取页面刷新频率
    @http.route('/get_refresh_rate/', auth='public', type='http', methods=['GET'])
    def get_refresh_rate(self, **kw):

        view_name = kw["view_name"]   # 视图名称

        data_refresh_frequency_obj = http.request.env["data_refresh_frequency"].sudo().search([("data_page", "=", view_name)])

        return json.dumps({"refresh_frequency": data_refresh_frequency_obj.refresh_frequency})



    # 获取在职员工人数
    @http.route('/get_number_employees/', auth='public', type='http', methods=['GET'])
    def get_number_employees(self, **kw):

        # 查询没有离职的员工你数
        number_employees = http.request.env["hr.employee"].sudo().search_count([("is_delete", "=", False)])

        return json.dumps({"number_employees": number_employees})


    # 获取订单数
    @http.route('/get_number_orders/', auth='public', type='http', methods=['GET'])
    def get_number_orders(self, **kw):

        # 获取订单数
        number_orders = http.request.env["sale_pro.sale_pro"].sudo().search_count([])

        return json.dumps({"number_orders": number_orders})



    # 获取月产值(不包含当天)
    @http.route('/get_month_output_value/', auth='public', type='http', methods=['GET'])
    def get_month_output_value(self, **kw):

        today_time = datetime.now()
        # 今天日期
        today = today_time.date()
        # 昨天日期
        yesterday = today - timedelta(days=1)
        # 获取当月第一天
        month_first_day = datetime.strptime(f"{today.year}-{today.month}-1", '%Y-%m-%d')


        month_output_value = 0

        # 如果当月第一天和昨天日期在同一个月
        if month_first_day.month == yesterday.month:

            pro_pro_objs = http.request.env["pro.pro"].sudo().search([
                ("date", ">=", month_first_day),
                ("date", "<=", yesterday)
            ])

            for pro_pro_obj in pro_pro_objs:
                month_output_value = month_output_value + pro_pro_obj.pro_value


        return json.dumps({"month_output_value": month_output_value})




    # 获取当日计划数据(分组)
    @http.route('/get_today_plan/', auth='public', type='http', methods=['GET'])
    def get_today_plan(self, **kw):

        CN_NUM = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            }


        today_time = datetime.now()
        # 今天日期
        today = today_time.date()

        planning_slot_objs = http.request.env["planning.slot"].sudo().search([
            ("dDate", "=", today)
        ])

        today_plan_data = []

        for planning_slot_obj in planning_slot_objs:

            staff_group = re.sub("\D", "", planning_slot_obj.staff_group)

            if staff_group:

                # 是否已经存在
                is_there_are = False

                for rec in today_plan_data:
                    if rec["staff_group"] == CN_NUM[staff_group]:
                        is_there_are = True

                        rec["plan_number"] = rec["plan_number"] + planning_slot_obj.plan_number

                if is_there_are:
                    pass
                else:

                    today_plan_data.append({
                        "dDate": str(planning_slot_obj.dDate),
                        "staff_group": CN_NUM[staff_group],
                        "plan_number": planning_slot_obj.plan_number,
                    })

        return json.dumps({"today_plan_data": today_plan_data})


    # 获取车间计划总数
    @http.route('/get_today_plan_workshop/', auth='public', type='http', methods=['GET'])
    def get_today_plan_workshop(self, **kw):

        if "today" in kw:
            today = kw["today"]
        else:
            today_time = datetime.now()
            # 今天日期
            today = today_time.date()

        if kw["dashboard_name"] == "车间":

            planning_slot_objs = http.request.env["planning.slot"].sudo().search([
                ("dDate", "=", today),
                ("staff_group", "like", "组")
            ])

        else:
            planning_slot_objs = http.request.env["planning.slot"].sudo().search([
                ("dDate", "=", today),
                ("staff_group", "like", kw["dashboard_name"])
            ])


        plan_count = 0

        for planning_slot_obj in planning_slot_objs:

            plan_count = plan_count + planning_slot_obj.plan_number

        return json.dumps({"plan_count": plan_count})




    # 获取最近日期各组返修率
    @http.route('/get_recently_group_statistical/', auth='public', type='http', methods=['GET'])
    def get_recently_group_statistical(self, **kw):


        today_time = datetime.now()
        # 今天日期
        today = today_time.date()

        while True:

            group_statistical_objs = http.request.env["group_statistical"].sudo().search([("dDate", "=", today)])

            if group_statistical_objs:
                break
            else:
                today = today - timedelta(days=1)


        recently_group_statistical = []

        for group_statistical_obj in group_statistical_objs:

            recently_group_statistical.append({
                "dDate": str(group_statistical_obj.dDate),
                "group": group_statistical_obj.group,
                "assess_index": group_statistical_obj.repair_ratio,
            })




        recently_group_statistical = sorted(recently_group_statistical, key=itemgetter('assess_index'), reverse=True)



        return json.dumps({"date": str(today), "recently_group_statistical": recently_group_statistical})



    # 获取最近一天的裁床产值
    @http.route('/get_recently_cutting_bed/', auth='public', type='http', methods=['GET'])
    def get_recently_cutting_bed(self, **kw):

        today_time = datetime.now()
        # 今天日期
        today = today_time.date()

        while True:

            cutting_bed_number_list = http.request.env["cutting_bed"].sudo().search([("date", "=", today)]).mapped('number')

            if cutting_bed_number_list:
                break
            else:
                today = today - timedelta(days=1)


        return json.dumps({"today": str(today),  "cutting_bed_count": sum(cutting_bed_number_list)})


    # 获取订单上的未完成和未上线的制单数(获取仓库出库比例)
    @http.route('/get_order_voucher_number/', auth='public', type='http', methods=['GET'])
    def get_order_voucher_number(self, **kw):

        sale_pro_objs = http.request.env["sale_pro.sale_pro"].sudo().search([
            ("is_finish", "in", ["未上线", "未完成"]),
        ])

        order_voucher_number = 0    # 订单制单数

        outbound_output = 0     # 出库产值

        for sale_pro_obj in sale_pro_objs:

            order_voucher_number = order_voucher_number + sum(sale_pro_obj.ib_detail_ids.mapped('z_totle'))

            for ib_detail_obj in sale_pro_obj.ib_detail_ids:

                warehouse_out_objs_number_list = http.request.env["warehouse_out"].sudo().search([
                    ("style_number", "=", ib_detail_obj.id)
                ]).mapped('number')

                outbound_output = outbound_output + sum(warehouse_out_objs_number_list)

        return json.dumps({"warehouse_outbound_progress": outbound_output / order_voucher_number})





    # 获取萤石云token
    def get_yingshi_token(self):

        appKey = http.request.env.ref("fsn_setting.yingshi_cloud_setting_key").value
        appSecret = http.request.env.ref("fsn_setting.yingshi_cloud_setting_value").value

        url = f"https://open.ys7.com/api/lapp/token/get?appKey={appKey}&appSecret={appSecret}"
        res = requests.post(url)
        res_data = json.loads(res.text)


        if "data" in res_data:

            return {"accessToken": res_data['data']['accessToken'], "expireTime": res_data['data']['expireTime']}

        else:
            return False


    # 获取萤石云直播地址
    @http.route('/get_yingshi_video_url/', auth='public', type='http', methods=['GET'])
    def get_yingshi_video_url(self, **kw):


        # self.env['ir.config_parameter'].sudo().set_param('account_integration_jdy.client_id', self.jdy_client_id)
        accessToken = http.request.env['ir.config_parameter'].sudo().get_param('yingshi.accessToken')
        expireTime = http.request.env['ir.config_parameter'].sudo().get_param('yingshi.expireTime')
        # token_expire_time = datetime.strptime(token_expire_time, "%Y-%m-%d %H:%M:%S")

        if accessToken and expireTime:
            # 当前时间
            today_time = datetime.now()
            # 转时间戳
            today_time = today_time.timestamp()

            if today_time > int(expireTime[0:-3]):

                # 获取萤石云token数据
                data = self.get_yingshi_token()
                # token保存到系统参数
                accessToken = data.get("accessToken")
                http.request.env['ir.config_parameter'].sudo().set_param('yingshi.accessToken', accessToken)
                # 过期时间保存到系统参数
                expireTime = data.get("expireTime")
                http.request.env['ir.config_parameter'].sudo().set_param('yingshi.expireTime', expireTime)


        else:
            # 获取萤石云token数据
            data = self.get_yingshi_token()
            # token保存到系统参数
            accessToken = data.get("accessToken")
            http.request.env['ir.config_parameter'].sudo().set_param('yingshi.accessToken', accessToken)
            # 过期时间保存到系统参数
            expireTime = data.get("expireTime")
            http.request.env['ir.config_parameter'].sudo().set_param('yingshi.expireTime', expireTime)


        # 获取萤石云设备信息
        device_name = kw.get("device_name")
        yingshi_equipment_info_objs = http.request.env["yingshi_equipment_info"].sudo().search([("device_name", "=", device_name)])

        # 设备序列号
        device_serial_number = yingshi_equipment_info_objs.device_serial_number
        # 通道编号
        device_channel_number = yingshi_equipment_info_objs.device_channel_number
        # 视频地址
        video_url = f"https://open.ys7.com/jssdk/theme.html?url=ezopen://open.ys7.com/{device_serial_number}/{device_channel_number}.live&accessToken={accessToken}&id=ysopen"

        return json.dumps({"video_url": video_url})










