from odoo.exceptions import ValidationError
from odoo import models, fields, api

import datetime
import time

from utils import weixin_approval_utils


class InvestInvest(models.Model):
    '''继承中查'''
    _inherit = "invest.invest"

    group_secondary_repair_number = fields.Integer(string="小组二次返修数")
    group_secondary_check_number = fields.Integer(string="小组二次返修查货数")
    group_secondary_delivery_number = fields.Integer(string="小组二次返修交货数")
    problem_points_number = fields.Integer(string="问题点数")

    sp_no = fields.Char(string="审批编号")


    def workwx_auto_sync_info(self, now_time):
        ''' 同步企业微信审批任务'''

        now_time += datetime.timedelta(hours=8)
        old_time = now_time - datetime.timedelta(days=5)

        now_time_stamp = int(time.mktime(now_time.timetuple()))
        old_time_stamp = int(time.mktime(old_time.timetuple()))


        print(now_time, old_time)
        print(now_time_stamp, old_time_stamp)
        approval_number_info = weixin_approval_utils.get_approval_number_info(old_time_stamp, now_time_stamp, weixin_approval_utils.INVEST_SP_TEMPLATE_ID, weixin_approval_utils.HAVE_PASSED)
        for sp_no in approval_number_info:

            if self.env['fsn_work_wx_approval_record'].sudo().search([("sp_no", "=", sp_no), ("template_id", "=", weixin_approval_utils.INVEST_SP_TEMPLATE_ID)]):
                ''' 如果已经同步过了该审批记录，则不再同步'''
                continue

            detail_info = weixin_approval_utils.get_approval_details_info(sp_no)

            for field_info in detail_info['apply_data']['contents']:

                if field_info['title'][0]['text'] == "交货日期":

                    s_timestamp = int(field_info['value']['date']['s_timestamp']) + 28800
                    s_timestamp = time.localtime(s_timestamp)
                    sp_date = time.strftime("%Y-%m-%d", s_timestamp)
                    print(sp_date)

                if field_info['title'][0]['text'] == "中查姓名":
                    invest_id = int(field_info['value']['selector']['options'][0]['key'])
                    invest_obj = self.env['hr.employee'].sudo().browse(invest_id)
                    print(invest_obj.name)

                if field_info['title'][0]['text'] == "组别":
                    group_id = int(field_info['value']['selector']['options'][0]['key'])
                    fsn_staff_team_obj = self.env['fsn_staff_team'].sudo().browse(group_id)
                    print(fsn_staff_team_obj.name)

                if field_info['title'][0]['text'] == "订单号":
                    order_number_id = int(field_info['value']['selector']['options'][0]['key'])
                    print(order_number_id)

                if field_info['title'][0]['text'] == "款号":
                    style_number_id = int(field_info['value']['selector']['options'][0]['key'])
                    print(style_number_id)

                if field_info['title'][0]['text'] == "大货查货数":
                    check_the_quantity = int(field_info['value']['new_number'])

                if field_info['title'][0]['text'] == "大货返修数":
                    repairs_number = int(field_info['value']['new_number'])

                if field_info['title'][0]['text'] == "大货交货数":
                    quantity_of_delivery = int(field_info['value']['new_number'])

                if field_info['title'][0]['text'] == "二次返修查货数":
                    group_secondary_check_number = int(field_info['value']['new_number'])

                if field_info['title'][0]['text'] == "二次返修数":
                    group_secondary_repair_number = int(field_info['value']['new_number'])

                if field_info['title'][0]['text'] == "二次返修交货数":
                    group_secondary_delivery_number = int(field_info['value']['new_number'])

                line_list = []
                if field_info['title'][0]['text'] == "明细":
                   
                   for line_info in field_info['value']['children']:
                        for line_field_info in line_info['list']:

                            if line_field_info['title'][0]['text'] == "问题点":
                                problems = line_field_info['value']['text']

                            if line_field_info['title'][0]['text'] == "问题点数":
                                problem_points_number = line_field_info['value']['new_number']

                            if line_field_info['title'][0]['text'] == "返修类型":
                                repair_type = line_field_info['value']['selector']['options'][0]['value'][0]['text']

                            if line_field_info['title'][0]['text'] == "车位姓名":
                                emp_obj = self.env['hr.employee'].sudo().browse(int(line_field_info['value']['selector']['options'][0]['key']))
                                print(emp_obj.name)


                        line_list.append({
                            "problems": problems,
                            "problem_points_number": int(problem_points_number),
                            "repair_type": repair_type,
                            "comment": emp_obj.name,
                        })

            for index, line in enumerate(line_list):

                if index:
                    self.env['invest.invest'].sudo().create({
                        "date": sp_date,    # 日期
                        "group": fsn_staff_team_obj.name,   # 组别
                        "invest": invest_obj.name,  # 中查
                        "order_number": order_number_id,    # 订单
                        "style_number": style_number_id,    # 款号
                        "check_the_quantity": 0,   # 大货查货数
                        "repairs_number": 0,   # 大货返修数
                        "quantity_of_delivery": 0,   # 大货交货数
                        "group_secondary_check_number": 0,   # 二次查货数
                        "group_secondary_repair_number": 0,     # 二次返修数
                        "group_secondary_delivery_number": 0,     # 二次交货数
                        "problems": line['problems'],   # 问题点
                        "problem_points_number": line['problem_points_number'],     # 问题点数
                        "repair_type": line['repair_type'],     # 返修类型
                        "comment":line['comment'],    # 车位姓名
                        "sp_no": sp_no,
                    })
                else:
                    self.env['invest.invest'].sudo().create({
                        "date": sp_date,    # 日期
                        "group": fsn_staff_team_obj.name,   # 组别
                        "invest": invest_obj.name,  # 中查
                        "order_number": order_number_id,    # 订单
                        "style_number": style_number_id,    # 款号
                        "check_the_quantity": check_the_quantity,   # 大货查货数
                        "repairs_number": repairs_number,   # 大货返修数
                        "quantity_of_delivery": quantity_of_delivery,   # 大货交货数
                        "group_secondary_check_number": group_secondary_check_number,   # 二次查货数
                        "group_secondary_repair_number": group_secondary_repair_number,     # 二次返修数
                        "group_secondary_delivery_number": group_secondary_delivery_number,     # 二次交货数
                        "problems": line['problems'],   # 问题点
                        "problem_points_number": line['problem_points_number'],     # 问题点数
                        "repair_type": line['repair_type'],     # 返修类型
                        "comment":line['comment'],    # 车位姓名
                        "sp_no": sp_no,
                    })


            self.env['fsn_work_wx_approval_record'].sudo().create({
                "sp_no": detail_info['sp_no'],
                "sp_name": detail_info['sp_name'],
                "template_id": detail_info['template_id'],
                "apply_time": detail_info['apply_time'],
                "sp_status": str(detail_info['sp_status'])
            })



    def set_day_qing_day_bi(self):
        for record in self:
            
            day_qing_day_bi_objs = self.env["day_qing_day_bi"].sudo().search([
                ("date", "=", record.date),
                ("group", "=", record.group),
                ("style_number", "=", record.style_number.id),
            ])
            if day_qing_day_bi_objs:
                for day_qing_day_bi_obj in day_qing_day_bi_objs:
                    day_qing_day_bi_obj.invest_invest_ids = [(4, record.id)]
            else:
                day_qing_day_bi_obj = self.env["day_qing_day_bi"].sudo().create({
                    "date": record.date,
                    "group": record.group,
                    "style_number": record.style_number.id
                })
                day_qing_day_bi_obj.invest_invest_ids = [(4, record.id)]

    @api.model
    def create(self, vals):

        res = super(InvestInvest, self).create(vals)

        res.set_day_qing_day_bi()

        return res