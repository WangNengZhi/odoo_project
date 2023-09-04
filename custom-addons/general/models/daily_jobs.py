from datetime import datetime
from inspect import Traceback
from odoo import models
from utils import weixin_utils
import itertools
import traceback


def send_worst_workers_of_day_to_enterprise_weixin(date, data):
    if not data:
        return
    
    stats = {}
    # group, repair_rate, comment
    for d in data:
        if d.group not in stats:
            stats[d.group] = []
        stats[d.group].append(d)
            
    s = ''
    for group, recs in stats.items():
        maxi = max(d.repair_rate for d in recs)  # 组内最高的返修率
        if maxi == 0.0:
            continue
        workers = [d.comment.strip() for d in recs if d.repair_rate==maxi and d.comment and d.comment.strip()]  # d.comment may be bool
        if workers:
            s += f'{group}组：'
            if len(workers) == 1:
                s += workers[0]                    
            else:
                fst, *others = workers
                s += '、'.join(others) + '和' + fst
            s += '\n'

    if not s:
        return

    text = f'各组生产质量最差（中查返修率最高）员工统计（{date.year}年{date.month}月{date.day}日）：\n\n{s}'
    # print('*'*80, text)
    
    # weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.DEVELOPMENT_AND_TEST)
    weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.ADMIN_GROUP)


class DailyJobs(models.Model):
    _inherit = 'invest.invest'  # 中查


    def send_daily_report_of_worst_workers_to_enterprise_weixin(self):
        ''' 发送各组当日中查返修率最高的员工到企业微信 '''
        latest = self.env['sent_messages'].sudo().search([
                    ('msg_type','=','enterprise_weixin'),
                    ('msg_category','=','worst_workers_of_day')], 
                    order='msg_summary desc')  # !
        if not latest:
            return

        # print('*'*80, latest[0].msg_summary)
        latest = datetime(* map(int, latest[0].msg_summary.split('-')))

        data = self.sudo().search([('date','>',latest)], order='date')
        # print(len(data))
        
        for date, it in itertools.groupby(data, key=lambda x:x.date):
            # print(date, it)
            try:
                send_worst_workers_of_day_to_enterprise_weixin(date, list(it))
            except:
                traceback.print_exc()
                break  # !!
            else:
                record = dict(
                    msg_type = 'enterprise_weixin',
                    msg_category = 'worst_workers_of_day',
                    msg_summary = f'{date.year}-{date.month:02d}-{date.day:02d}',
                    send_time = datetime.now()
                )
                self.env['sent_messages'].create(record)


