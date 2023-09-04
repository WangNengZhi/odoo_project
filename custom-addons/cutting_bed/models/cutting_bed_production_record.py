from datetime import date, datetime, timedelta
import logging
import requests
from odoo import models, fields

_logger = logging.getLogger(__name__)

class CuttingBedProductionRecord(models.Model):
    _name = 'cutting_bed_production_record'
    _description = '裁床生产数据'
    _order = 'update_time desc'

    dtype = fields.Char(string='裁床型号')
    dsn = fields.Char(string='裁床序列号')

    marker = fields.Char(string='版图名称')
    param_file = fields.Char(string='参数文件')
    cut_time = fields.Float(string='裁剪时间（分钟）')
    job_time = fields.Float(string='工作时间（分钟）')
    cut_distance = fields.Float(string='裁剪距离（米）')

    pos_distance = fields.Float(string='定位距离')
    dryhaul_cuttime = fields.Float(string='定位时间')
    bite_time = fields.Float(string='过窗时间')
    secondary_time = fields.Float(string='准备时间')
    break_time = fields.Float(string='暂停时间')

    update_time = fields.Datetime(string='更新时间')
    start_time = fields.Datetime(string='开始时间')
    end_time = fields.Datetime(string='结束时间')

    v = fields.Float(string='速度')
    vmax = fields.Float(string='最大速度')
    vmin = fields.Float(string='最小速度')

    sharpen = fields.Integer(string='磨刀数')
    slit = fields.Integer(string='I字剪口')
    vnotch = fields.Integer(string='V字剪口')
    drill = fields.Integer(string='主打孔钻数')
    helprdrill = fields.Integer(string='辅打孔钻数')
    sections = fields.Integer(string='窗口数')

    segs = fields.Integer(string='裁剪片数')


    def sync(self, date):
        _logger.info(f'sync cutting_bed_production_record of {date}')

        USER = 'hzjt'
        PASSWD = '123456'
        LOGIN_POST_URL = 'https://bullmer.online/Ajax/Ajax_Login.ashx'
        REPORT_POST_URL = 'https://bullmer.online/Ajax/Ajax_CutterStatistic.ashx'

        DTYPE = 'D800'
        DSN = '0095C6A0'
        MAPPING = {
                   'MARKER': ('marker', str),
                   'PARAMFILE': ('param_file', str),
                   'CUTTIME': ('cut_time', float),
                   'JOBTIME': ('job_time', float),
                   'CUTDISTANCE': ('cut_distance', float),
                   'POSDISTANCE': ('pos_distance', float),
                   'DRYHAULCUTTIME': ('dryhaul_cuttime', float),
                   'BITETIME': ('bite_time', float),
                   'SECONDARYTIME': ('secondary_time', float),
                   'BREAKTIME': ('break_time', float),
                   'V': ('v', float),
                   'VMAX': ('vmax', float),
                   'VMIN': ('vmin', float),
                   'SHARPEN': ('sharpen', int),
                   'SLIT': ('slit', int),
                   'VNOTCH': ('vnotch', int),
                   'DRILL': ('drill', int),
                   'HELPRDRILL': ('helprdrill', int),
                   'SECTIONS': ('sections', int),
                   'SEGS': ('segs', int),
                  }

        with requests.Session() as s:
            payload = dict(type = 'login', bmembername = USER, bpassword = PASSWD)
            resp = s.post(LOGIN_POST_URL, data=payload)
            # print(resp)

            start_date = end_date = f'{date.year}-{date.month:02d}-{date.day:02d}'
            # print(start_date, 'to', end_date)
            payload = dict( type = 'GetStatInfoSearch',
                            pageIndex = 1,
                            pageSize = 10,  # TOFIX
                            StatCType = 'D800',
                            StatSN = '0095C6A0',
                            StatType = 'CAD',
                            StatParam = 'POSDISTANCE,DRYHAULCUTTIME,BITETIME,SECONDARYTIME,BREAKTIME,TIME,TIMEOFSTART,TIMEOFEND,DATE,DATEOFSTART,DATEOFEND,V,VMAX,VMIN,SHARPEN,SLIT,VNOTCH,DRILL,HELPRDRILL,SECTIONS',
                            Start_Date = start_date,
                            End_Date = end_date,
                        )
            resp = s.post(REPORT_POST_URL, data=payload)  # data, NOT params
            resp = resp.json()

        # print(resp['recordTotal'])

        NAME, TYPE = 0, 1
        delta = timedelta(hours=-8)
        def get_datetime(date, time, delta=delta):
            hh, mm, ss = map(int, time.split(':'))
            dt = datetime(date.year, date.month, date.day, hh, mm, ss)
            return dt + delta

        n = resp['recordTotal']
        if n == 0:
            _logger.info(f'NO cutting_bed_production_record data of {date}.')
            return

        _logger.info(f'sync {n} cutting_bed_production_record data of {date}')

        for x in resp['Data']:
            d = {MAPPING[k][NAME]: MAPPING[k][TYPE](v) for k, v in x.items() if k in MAPPING}
            d['start_time'] = get_datetime(date, x['TIMEOFSTART'])
            d['end_time'] = get_datetime(date, x['TIMEOFEND'])
            update_time = get_datetime(date, x['TIME'])

            self.sudo().search([('dtype', '=', DTYPE),
                                ('dsn', '=', DSN),
                                ('update_time', '=', update_time)]).unlink()
            self.sudo().create(dict(d, dtype = DTYPE, dsn = DSN, update_time = update_time))

