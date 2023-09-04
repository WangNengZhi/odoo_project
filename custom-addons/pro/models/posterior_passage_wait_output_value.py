from odoo.exceptions import ValidationError
from odoo import models, fields, api


class PosteriorPassageWaitOutputValue(models.Model):
    _name = "pp_wait_output_value"
    _description = '后道待检产值'
    _rec_name = "date"
    _order = "date desc"


    date = fields.Date(string='日期')
    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    number = fields.Integer(string='件数')
    num_people = fields.Integer(string='人数')
    pro_value = fields.Float('产值', compute="set_pro_value", store=True)



    # 设置产值
    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for record in self:


            record.pro_value = record.number * float(record.order_number.order_price)



    def set_date(self):
        for record in self:

            # 查询当日的总检的记录
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.date),
                ("item_no", "=", record.style_number.id),
                ("order_number_id", "=", self.order_number.id),
                ("general1", "!=", "蒋桃秀")
            ])

            tem_number = 0  # 件数
            tem_num_people_list = []    # 人员列表

            for general_general_obj in general_general_objs:
                # 件数求和
                tem_number = tem_number + general_general_obj.general_number

                # 判断人员列表中，是否已经有该员工，否则奖该员工添加到临时人员列表中
                if general_general_obj.general1 not in tem_num_people_list:
                    tem_num_people_list.append(general_general_obj.general1)

            record.number = tem_number
            record.num_people = len(tem_num_people_list)
