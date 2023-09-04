from odoo import models, fields, api
from odoo.exceptions import ValidationError

from . import mysql_operation
import datetime


class AutomaticCuttingBed(models.Model):
    _name = 'automatic_cutting_bed'
    _description = '自动裁床'
    _order = 'start_time desc'


    key_id = fields.Char(string="记录识别号")

    @api.constrains('key_id')
    def _check_uniqueness(self):

        demo = self.env[self._name].sudo().search([('key_id', '=', self.key_id)])
        if len(demo) > 1:
            raise ValidationError(f"{self.date}的记录已经存在了！不可重复创建。")

    date = fields.Date(string="日期")
    start_time = fields.Datetime(string='开始时间')
    end_time = fields.Datetime(string='结束时间')

    marker = fields.Char(string='版图名称')
    param_file = fields.Char(string="参数文件")
    order = fields.Char(string="订单")
    operator = fields.Char(string="操作员")


    cutdistance = fields.Float(string="裁割距离")
    posdistance = fields.Float(string="定位距离")
    pendistance = fields.Float(string="笔距离")
    contourdistance = fields.Float(string="轮廓线距离")
    markerlength = fields.Float(string="Ｘ轴（版长）")
    markerheight = fields.Float(string="Ｙ轴（幅宽）")

    cut_time = fields.Float(string='裁剪时间（分钟）')
    job_time = fields.Float(string='工作时间（分钟）')
    dryhaulcuttime = fields.Float(string="空裁时间")
    coutourtime = fields.Float(string="轮廓线时间")
    pentime = fields.Float(string="笔时间")
    dryhaulpentime = fields.Float(string="空笔时间")
    bitetime = fields.Float(string="过窗时间")
    secondarytime = fields.Float(string="二次时间")
    breaktime = fields.Float(string="休息时间")
    aborttime = fields.Float(string="终止时间")

    v = fields.Float(string='裁割速度')
    vmax = fields.Float(string='最大裁割速度')
    vmin = fields.Float(string='最小裁割速度')

    parameter1 = fields.Char(string="机器ID")
    parameter2 = fields.Float(string="笔（最大速度）")
    parameter3 = fields.Float(string="角度")
    parameter4 = fields.Float(string="弯曲")
    parameter5 = fields.Float(string="断开尺寸")
    parameter6 = fields.Float(string="工具")
    parameter7 = fields.Integer(string="最小磨刀")
    parameter8 = fields.Integer(string="最大磨刀")
    parameter9 = fields.Integer(string="有效裁割速度")
    parameter10 = fields.Integer(string="过裁量")


    ignoredpoints = fields.Integer(string="忽略点")
    points = fields.Integer(string="点")
    segs = fields.Integer(string="缺陷")
    ignoredsegs = fields.Integer(string="忽略缺陷")

    xzoom = fields.Float(string="X轴缩放比例")
    yzoom = fields.Float(string="Y轴缩放比例")

    sharpen = fields.Integer(string="磨刀")
    slit = fields.Integer(string="一字剪口")
    stitch = fields.Integer(string="缝制剪口")
    vnotch = fields.Integer(string="V字剪口")
    drill = fields.Integer(string="主钻")
    helprdrill = fields.Integer(string="轴钻")
    matchingpoint = fields.Integer(string="对条格点")
    tooledown = fields.Integer(string="工具下")
    labels = fields.Integer(string="贴标")
    sections = fields.Integer(string="窗数")
    layer = fields.Integer(string="层数")

    machineid = fields.Char(string="设备ID")




    def sync_data(self):

        # ip地址
        mysql_ip = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "IP")]).value
        # 端口号
        mysql_port = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "端口")]).value
        # 数据库账号
        mysql_db_account = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "数据库账号")]).value
        # 数据库密码
        mysql_db_password = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "数据库密码")]).value
        # 数据库名称
        mysql_db_name = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "数据库名")]).value
        # 数据库表名
        mysql_db_table_name = self.env["cutting_bed_connect_setting"].sudo().search([("key", "=", "数据库表名")]).value


        today_date = fields.Datetime.now().date()
        today_date_list = str(today_date)[2:].split("-")
        # 列表取反
        today_date_list = list(reversed(today_date_list))
        today_date = ".".join(today_date_list)


        sql = f'SELECT * FROM {mysql_db_table_name} WHERE DATE="{today_date}"'

        try:
            data = mysql_operation.select_db({
                "mysql_ip": mysql_ip,
                "mysql_port": int(mysql_port),
                "mysql_db_account": mysql_db_account,
                "mysql_db_password": mysql_db_password,
                "mysql_db_name": mysql_db_name,
                "mysql_db_table_name": mysql_db_table_name,
            }, sql)
        except Exception as err:
            pass
        else:
            # 如果查询到数据
            if data:
                for record in data:

                    # 开始时间
                    start_date_list = record["DATEOFSTART"].split(".")
                    start_date_list = list(reversed(start_date_list))
                    start_date_list[0] = start_date_list[0].strip()
                    start_date = "-".join(start_date_list)

                    start_time = f"20{start_date} {record['TIMEOFSTART'].strip()}"

                    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

                    # 结束时间
                    end_date_list = record["DATEOFEND"].split(".")
                    end_date_list = list(reversed(start_date_list))
                    end_date_list[0] = end_date_list[0].strip()
                    end_date = "-".join(start_date_list)

                    end_time = f"20{end_date} {record['TIMEOFEND'].strip()}"

                    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")


                    date = end_time.date()


                    exist = self.sudo().search([("key_id", "=", record["KeyID"])])

                    if not exist:

                        self.sudo().create({
                            "date": date,   # 日期
                            "key_id": record["KeyID"],  # 记录识别号
                            "start_time": start_time,   # 开始hi就
                            "end_time": end_time,   # 结束时间
                            "marker": record["MARKER"],     # 版图名称
                            "param_file": record["PARAMFILE"],  # 参数文件
                            "order": record["ORDER"],   # 订单
                            "operator": record["OPERATOR"],     # 操作员
                            "cutdistance": record["CUTDISTANCE"],   # 裁割距离
                            "posdistance": record["POSDISTANCE"],   # 定位距离
                            "pendistance": record["PENDISTANCE"],   # 笔距离
                            "contourdistance": record["CONTOURDISTANCE"],   # 轮廓线距离
                            "markerlength": record["MARKERLENGTH"],     # Ｘ轴（版长）
                            "markerheight": record["MARKERHEIGHT"],     # Ｙ轴（幅宽）

                            "job_time": record["JOBTIME"],  # 工作时间
                            "cut_time": record["CUTTIME"],   # 裁割时间
                            "dryhaulcuttime": record["DRYHAULCUTTIME"],     # 空裁时间
                            "coutourtime": record["CONTOURTIME"],   # 轮廓线时间
                            "pentime": record["PENTIME"],   # 笔时间
                            "dryhaulpentime": record["DRYHAULPENTIME"],     # 空笔时间
                            "bitetime": record["BITETIME"],     # 过窗时间
                            "secondarytime": record["SECONDARYTIME"],   # 二次时间
                            "breaktime": record["BREAKTIME"],   # 休息时间
                            "aborttime": record["ABORTTIME"],   # 终止时间

                            "v": record["V"],   # 裁割速度
                            "vmax": record["VMAX"],     # 最大裁割速度
                            "vmin": record["VMIN"],    # 最小裁割速度

                            "parameter1": record["PARAMETER1"],   #机器ID"
                            "parameter2": record["PARAMETER2"],   #笔（最大速度）")
                            "parameter3": record["PARAMETER3"],   #角度")
                            "parameter4": record["PARAMETER4"],   #弯曲")
                            "parameter5": record["PARAMETER5"],   #断开尺寸")
                            "parameter6": record["PARAMETER6"],   #工具")
                            "parameter7": record["PARAMETER7"],   #最小磨刀")
                            "parameter8": record["PARAMETER8"],   #最大磨刀")
                            "parameter9": record["PARAMETER9"],   #有效裁割速度")
                            "parameter10": record["PARAMETER10"],   #过裁量")

                            "ignoredpoints": record["IGNOREDPOINTS"],     # 忽略点
                            "points": record["POINTS"],     # 点
                            "segs": record["SEGS"],     # 缺陷
                            "ignoredsegs": record["IGNOREDSEGS"],      # 忽略缺陷

                            "xzoom": record["XZOOM"],   # X轴缩放比例
                            "yzoom": record["YZOOM"],   # Y轴缩放比例

                            "sharpen": record["SHARPEN"],   # 磨刀
                            "slit": record["SLIT"],     # 一字剪口
                            "stitch": record["STITCH"],     # 缝制剪口
                            "vnotch": record["VNOTCH"],    # V字剪口
                            "drill": record["DRILL"],   # 主钻
                            "helprdrill": record["HELPRDRILL"],     # 轴钻
                            "matchingpoint": record["MATCHINGPOINT"],   # 对条格点
                            "tooledown": record["TOOLDOWN"],    # 工具下
                            "labels": record["LABELS"],     # 贴标
                            "sections": record["SECTIONS"],     # 窗数
                            "layer": record["LAYER"],   # 层数

                            "machineid": record["MACHINEID"],  # 设备ID
                        })



