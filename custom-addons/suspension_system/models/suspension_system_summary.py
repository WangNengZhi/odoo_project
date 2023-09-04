from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import requests
import json
from functools import reduce
from utils import weixin_utils

class SuspensionSystemSummary(models.Model):
    _name = 'suspension_system_summary'
    _description = '吊挂组产量汇总'
    # _rec_name = 'group'
    _order = "dDate desc"


    dDate = fields.Date(string="日期")
    date_host = fields.Integer(string="时间")
    group = fields.Many2one('check_position_settings', string='组别')
    people_number = fields.Integer(string="人数")
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号（对象）')
    order_number_show = fields.Char(string="订单号")
    style_number = fields.Many2one('ib.detail', string='款号（对象）')
    MONo = fields.Char(string="款号")
    product_size = fields.Many2one("fsn_size", string="尺码")
    production_value = fields.Float(string="产值", compute="set_production_value", store=True)
    total_quantity = fields.Integer(string="总件数")
    on_the_day_difference = fields.Integer(string="件数差值", compute="set_on_the_day_difference", store=True, group_operator='avg')
    # suspension_system_summary_line_ids = fields.One2many("suspension_system_details", "suspension_system_summary_id", string="吊挂组产量汇总明细ids")

    production_value_difference = fields.Float(string="产值差值", compute="set_production_value_difference", store=True)

    last_record = fields.Many2one("suspension_system_summary", string="上一个小时的记录")


    # 重新显示名称方法
    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.dDate}-{record.group.group}-{record.date_host}"
            result.append((record.id, rec_name))
        return result


    # 计算人数
    def set_people_number(self):
        for record in self:

            tem_var = 0

            suspension_system_station_summary_objs = self.env["suspension_system_station_summary"].sudo().search([
                ("dDate", "=", record.dDate),   # 日期
                ("group", "=", record.group.id),    # 组别
                ("MONo", "=", record.MONo),     # 款号
            ])

            # 根据员工去重
            suspension_system_station_summary_objs = reduce(lambda y,x:y if (x.employee_id.id in [i.employee_id.id for i in y]) else (lambda z,u:(z.append(u),z))(y,x)[1],suspension_system_station_summary_objs,[])

            for suspension_system_station_summary_obj in suspension_system_station_summary_objs:

                is_active = False   # 是否活跃
                for line_obj in suspension_system_station_summary_obj.line_lds:

                    if line_obj.is_update:
                        is_active = True

                if is_active:
                    tem_var = tem_var + 1

            return tem_var


    # 设置和上一天的产值差值
    @api.depends('production_value')
    def set_production_value_difference(self):

        for record in self:
            yesterday = record.dDate - timedelta(days=1)

            yesterday_production_value_list = self.sudo().search([
                ("dDate", "=", yesterday),
                ("date_host", "=", record.date_host),
                ("group", "=", record.group.id),
                ]).mapped('production_value')

            today_production_value_list = self.sudo().search([
                ("dDate", "=", record.dDate),
                ("date_host", "=", record.date_host),
                ("group", "=", record.group.id),
                ]).mapped('production_value')

            record.production_value_difference = sum(today_production_value_list) - sum(yesterday_production_value_list)


    # 设置和上一天的件数差值
    @api.depends('total_quantity')
    def set_on_the_day_difference(self):

        for record in self:

            if record.total_quantity != 0:

                # 各种颜色的款号列表
                MONo_list = []
                # 字符串切割奖款号的款号和颜色代码分开
                tem_str_list = record.MONo.split("-")
                # 查询款号列表中具有相同款号部分的 全部款号
                ib_detail_objs = self.env["ib.detail"].sudo().search([
                    ("style_number", "like", tem_str_list[0])
                ])
                # 奖查询出来的款号名称加入到列表中
                for ib_detail_obj in ib_detail_objs:
                    MONo_list.append(ib_detail_obj.style_number)

                on_a_suspension_system_summary_objs = self.env["suspension_system_summary"].sudo().search([
                    # ("dDate", "=", on_a_date),      # 日期
                    ("group", "=", record.group.id),       # 组别
                    ("date_host", "=", record.date_host),    # 时间
                    ("MONo", "in", MONo_list),     # 款号
                ])

                tem_list = []
                for on_a_suspension_system_summary_obj in on_a_suspension_system_summary_objs:

                    if on_a_suspension_system_summary_obj.dDate < record.dDate:

                        tem_list.append({
                            "MONo": on_a_suspension_system_summary_obj.MONo,    # 款号
                            "dDate": on_a_suspension_system_summary_obj.dDate,      # 日期
                            "total_quantity": on_a_suspension_system_summary_obj.total_quantity,    # 总件数
                        })

                if tem_list:
                    tem_list.sort(key=lambda x:x['dDate'], reverse=True)

                    summary_objs = self.env["suspension_system_summary"].sudo().search([
                        ("dDate", "=", tem_list[0]["dDate"]),      # 日期
                        ("group", "=", record.group.id),       # 组别
                        ("date_host", "=", record.date_host),    # 时间
                        ("MONo", "in", MONo_list),     # 款号
                    ])

                    tem_total_quantity = 0

                    for summary_obj in summary_objs:

                        tem_total_quantity = tem_total_quantity + summary_obj.total_quantity


                    present_summary_objs = self.env["suspension_system_summary"].sudo().search([
                        ("dDate", "=", record.dDate),      # 日期
                        ("group", "=", record.group.id),       # 组别
                        ("date_host", "=", record.date_host),    # 时间
                        ("MONo", "in", MONo_list),     # 款号
                    ])
                    present_tem_total_quantity = 0

                    for present_summary_obj in present_summary_objs:
                        present_tem_total_quantity = present_tem_total_quantity + present_summary_obj.total_quantity

                    # record.on_the_day_difference = record.total_quantity - tem_list[0]["total_quantity"]
                    record.on_the_day_difference = present_tem_total_quantity - tem_total_quantity
                else:
                    record.on_the_day_difference = 0




    # 计算产值
    @api.depends('total_quantity', 'order_number', 'order_number.order_price')
    def set_production_value(self):
        for record in self:

            record.production_value = record.total_quantity * float(record.order_number.order_price)



    # 记录上的件数和产值全部设置为0
    def empty_records(self, start_time):

        # 查询汇总表是否已经存在数据
        suspension_system_summary_objs = self.env["suspension_system_summary"].sudo().search([
            ("dDate", "=", start_time),
        ])
        for suspension_system_summary_obj in suspension_system_summary_objs:
            suspension_system_summary_obj.sudo().write({
                "total_quantity": 0,
                # "production_value": 0,
            })


    # 远程调用同步吊挂数据
    def sync_data(self):
        self._sync_data()

        return True

    def _sync_data(self, today=None):

        if not today:
            today = fields.Date.today()

        # 开始日期:今天日期
        start_date = today
        # 结束日期:明天日期
        end_date = start_date + timedelta(days=1)

        # 执行前先把今天的记录上的件数和产值全部设置为0
        self.empty_records(start_date)

        dg_host = self.env.company.dg_host      # ip
        dg_port = self.env.company.dg_port      # 端口号

        check_position_settings_objs = self.env["check_position_settings"].sudo().search([])

        for check_position_settings_obj in check_position_settings_objs:

            for position_line_obj in check_position_settings_obj.position_line_ids.filtered(lambda x: x.type in ["中查", "总检"]):
                # 从接口获取数据
                url = f"http://{dg_host}:{dg_port}/DgApi/Details?BeginTime={start_date}&EndTime={end_date}&StationID={position_line_obj.position}&WorkLine={check_position_settings_obj.group}"
                res = requests.get(url)
                res.encoding = 'utf-8'
                data_list = json.loads(res.text).get("Data")

                if not data_list:
                    ''' 如果没有数据, 则直接跳过'''
                    continue
                
                data_list = [i for i in data_list if i['InsOrder'] == 1]    # 去掉返修的

                for data_record in data_list:

                    # 时间字段格式化
                    BeginTime = data_record.get("BeginTime", None).replace("T", " ")
                    EndTime = data_record.get("EndTime", None).replace("T", " ")

                    BeginTime = datetime.strptime(BeginTime[0: 19], "%Y-%m-%d %H:%M:%S")
                    EndTime = datetime.strptime(EndTime[0: 19], "%Y-%m-%d %H:%M:%S")

                    data_record["ColorNo"] = data_record["ColorNo"].strip()     # 去掉两边空格（款号）

                    # 获取订单号
                    data_record["SeqCode"] = data_record["SeqCode"].strip()     # 去掉两边空格（订单号）
                    order_number_obj = self.env["sale_pro.sale_pro"].sudo().search([("order_number", "=", data_record["SeqCode"])])

                    # 查询尺码
                    data_record["SizeName"] = data_record["SizeName"].strip()     # 去掉两边空格
                    fsn_size_obj = self.env["fsn_size"].sudo().search([("name", "=", data_record["SizeName"])])

                    suspension_system_summary_objs = self.env["suspension_system_summary"].sudo().search([
                        ("dDate", "=", data_record.get("dDate", None)),     # 日期
                        ("date_host", "=", EndTime.hour + 1),   # 时间
                        ("group", "=", check_position_settings_obj.id),     # 组别
                        ("MONo", "=", data_record["ColorNo"]),      # 款号
                        ("order_number_show", "=", data_record["SeqCode"]),     # 订单号
                        ("product_size", "=", fsn_size_obj.id),     # 尺码
                    ])

                    if suspension_system_summary_objs:
                        pass
                    else:
                        # 获取款号
                        ib_detail_ids = self.env["ib.detail"].sudo().search([
                            ("style_number", "=", data_record["ColorNo"])
                        ])

                        # 如果查询到款号信息
                        if ib_detail_ids:
                            suspension_system_summary_objs = self.env["suspension_system_summary"].sudo().create({
                                "dDate": data_record.get("dDate", None),
                                "date_host": EndTime.hour + 1,
                                "group": check_position_settings_obj.id,
                                "order_number": order_number_obj.id,
                                "order_number_show": data_record["SeqCode"],
                                "style_number": ib_detail_ids.id,
                                "MONo": data_record["ColorNo"],
                                "product_size": fsn_size_obj.id,
                            })
                        else:
                            suspension_system_summary_objs = self.env["suspension_system_summary"].sudo().create({
                                "dDate": data_record.get("dDate", None),
                                "date_host": EndTime.hour + 1,
                                "group": check_position_settings_obj.id,
                                "order_number": order_number_obj.id,
                                "order_number_show": data_record["SeqCode"],
                                # "style_number": ib_detail_ids.id,
                                "MONo": data_record["ColorNo"],
                                "product_size": fsn_size_obj.id,
                            })

                        suspension_system_summary_objs.sudo().write({
                            "people_number": suspension_system_summary_objs.set_people_number()     # 获取人数
                        })

                    suspension_system_summary_objs.sudo().write({
                        "total_quantity": suspension_system_summary_objs.total_quantity + data_record["Qty"],
                    })



    def send_hourly_suspension_system_summary_to_enterprise_weixin(self, message_group="测试群"):
        # now = datetime.now() + timedelta(hours=-1)
        # now = datetime(2021,12,1, 13,23)
        now = datetime.now() + timedelta(hours=8)  # !!!
        # now = datetime.now()

        print(now)
        # 区间:
        # start_hour, end_hour = (now.hour, (now.hour+1)%24)
        start_hour, end_hour = ((now.hour-1)%24, now.hour)
        data = self.env["suspension_system_summary"].sudo().search([
            ('dDate', '=', now.date()),
            ('date_host', '=', end_hour)
        ], order='group')

        # print(type(data), len(data), bool(data))  # <class 'odoo.api.suspension_system_summary'> 0 False
        if not data:
            return

        def format(d, sum, difference_sum, output_value_sum):
            return (f'>**组别：{d.group.group}**\n'
                    f'>款号：{d.MONo}\n'
                    f'>当天{end_hour}点之前总产量：{sum}件\n'
                    f'>与昨天{end_hour}点之前总产量差值：{difference_sum}件\n'
                    f'>当天{end_hour}点之前总组产值：{output_value_sum}\n'
                    f'>{start_hour}时至{end_hour}时产量：{d.total_quantity}件\n'
                    f'>与昨天{start_hour}时至{end_hour}时产量差值：{d.on_the_day_difference}件\n'
                    f'>{start_hour}时至{end_hour}时时产值：{d.production_value}\n'
                    )

        markdown = f'#### 吊挂组产量汇总（{now.year}年{now.month}月{now.day}日 {start_hour}时至{end_hour}时）\n'
        # markdown += '>\n'.join(format(d) for d in data)

        tem_markdown = ""
        for d in data:
            sum_objs = self.env["suspension_system_summary"].sudo().search([
                ('dDate', '=', now.date()),
                ('date_host', '<=', end_hour),
                ('group', '=', d.group.id),
                ('MONo', '=', d.MONo),
            ])
            sum = 0     # 总件数
            difference_sum = 0      # 差值总数
            output_value_sum = 0    # 产值总数
            for sum_obj in sum_objs:
                sum = sum + sum_obj.total_quantity
                difference_sum = difference_sum + sum_obj.on_the_day_difference
                output_value_sum = output_value_sum + sum_obj.production_value

            tem_markdown += ''.join(format(d, sum, difference_sum, output_value_sum))

        markdown += '>\n' + tem_markdown

        if message_group == "管理群":
        # weixin_utils.send_markdown_to_enterprise_weixin(markdown, to_party=weixin_utils.HEAD_DEPT)  # 总部
        # weixin_utils.send_markdown_to_enterprise_weixin(markdown, to_party=weixin_utils.DEV_DEPT)  # 开发部门
            weixin_utils.send_app_group_info_markdown_weixin(markdown, chatid=weixin_utils.ADMIN_GROUP)   # 管理群
        elif message_group == "测试群":
            weixin_utils.send_app_group_info_markdown_weixin(markdown, chatid=weixin_utils.DEVELOPMENT_AND_TEST)   # 开发测试群
