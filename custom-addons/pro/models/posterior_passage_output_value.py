from odoo.exceptions import ValidationError
from odoo import models, fields, api


from datetime import datetime, timedelta
import time


class PosteriorPassageOutputValue(models.Model):
    _name = "posterior_passage_output_value"
    _description = '后道产值'
    _rec_name = "date"
    _order = "date desc"


    date = fields.Date('日期', required=True)
    week = fields.Char(string="周")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer('件数')
    num_people = fields.Integer('人数', required=True)
    # avg_value = fields.Float('人均产值', compute="_set_avg_value", store=True)
    pro_value = fields.Float('产值', compute="set_pro_value", store=True)
    posterior_passage_week_id = fields.Many2one('posterior_passage_output_value_week', string="后道产值(周)")
    is_inferior = fields.Selection([('合格', '合格'),('次品', '次品')],string="合格/次品", required=True)

    yesterday_pro_pro_number = fields.Integer(string="昨天产量", compute="set_yesterday_pro_pro_number", store=True)



    # 设置昨天产量
    @api.depends('date', "style_number")
    def set_yesterday_pro_pro_number(self):
        for record in self:
            if record.date and record.style_number:
                dDate = record.date - timedelta(days=1)

                pro_pro_objs = self.env["pro.pro"].sudo().search([
                    ("date", "=", dDate),
                    ("style_number", "=", record.style_number.id)
                ])
                # 临时昨天产量
                tem_yesterday_pro_pro_number = 0
                for pro_pro_obj in pro_pro_objs:
                    tem_yesterday_pro_pro_number = tem_yesterday_pro_pro_number + pro_pro_obj.number

                record.yesterday_pro_pro_number = tem_yesterday_pro_pro_number


    @api.constrains('date', "style_number", 'is_inferior')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ("style_number", "=", self.style_number.id),
            ("order_number", "=", self.order_number.id),
            ("is_inferior", "=", self.is_inferior),
            ("product_size", "=", self.product_size.id),
            ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在日期为：{self.date}款号为：{self.style_number.style_number}的{self.is_inferior}后道产值记录了！")


    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)


    # 设置后道进出明细
    def set_following_process_detail(self):
        following_process_detail_obj = self.env["following_process_detail"].sudo().search([
            ("dDate", "=", self.date)
        ])
        if following_process_detail_obj:
            following_process_detail_obj.set_following_process_enter()
        else:
            new_obj = following_process_detail_obj.create({
                "dDate": self.date
            })
            new_obj.set_following_process_enter()





    @api.model
    def create(self, vals):

        if vals["num_people"] <= 0:
            raise ValidationError(f"人数必须大于0！")


        datetime_obj = datetime.strptime(vals['date'], "%Y-%m-%d")
        year = datetime_obj.year
        week = datetime_obj.isocalendar()
        vals["week"] = f"{year}年第{week[1]}周"


        instance = super(PosteriorPassageOutputValue, self).create(vals)

        # 查询后道产值（周）表中有没有该组的记录
        posterior_passage_week_obj = self.env["posterior_passage_output_value_week"].sudo().search([("week", "=", vals["week"])])

        if posterior_passage_week_obj:
            # 计算人数
            posterior_passage_objs = self.env[self._name].sudo().search([("week", "=", vals["week"])])
            people_count = 0
            for posterior_passage_obj in posterior_passage_objs:
                people_count = people_count + posterior_passage_obj.num_people
            # 人数取平均值
            tem_num_people = int((people_count + vals["num_people"]) / (len(posterior_passage_objs) + 1))

            if instance.is_inferior == "合格":
                # 产值
                tem_pro_value = posterior_passage_week_obj.pro_value + abs(instance.pro_value)


                tem_style_number_list = posterior_passage_week_obj.style_number.split(",")
                tem_style_number_list.append(instance.style_number.style_number)      # 将款号添加到列表中
                tem_style_number_list = list(set(tem_style_number_list))    # 去重
                tem_style_number = ",".join(tem_style_number_list)


                posterior_passage_week_obj.sudo().write({
                    "style_number": tem_style_number,   # 款号
                    "number": posterior_passage_week_obj.number + vals["number"],   # 件数
                    "pro_value": tem_pro_value,     # 产值
                    "num_people": tem_num_people,   # 人数
                })

                instance.posterior_passage_week_id = posterior_passage_week_obj.id
        else:

            if instance.is_inferior == "合格":

                new_posterior_passage_week_obj = self.env["posterior_passage_output_value_week"].sudo().create({
                    "week": vals["week"],   # 周
                    "style_number": instance.style_number.style_number,    # 款号
                    "number": vals["number"],   # 件数
                    "pro_value": abs(instance.pro_value),     # 产值
                    "num_people": vals["num_people"],    # 人数
                })


                instance.posterior_passage_week_id = new_posterior_passage_week_obj.id

        # 设置后道进出明细
        instance.set_following_process_detail()

        return instance


    def unlink(self):

        for record in self:
            posterior_passage_objs = self.env[self._name].sudo().search([("week", "=", record["week"])])
            if len(posterior_passage_objs) == 1:
                record.posterior_passage_week_id.sudo().unlink()     # 删除组产值(周)
            else:

                # 计算删除后的人数
                tem_num_people_sum = 0
                for posterior_passage_obj in posterior_passage_objs:
                    tem_num_people_sum = tem_num_people_sum + posterior_passage_obj.num_people
                tem_num_people = (tem_num_people_sum - record.num_people) / (len(posterior_passage_objs) - 1)

                if record.is_inferior == "合格":
                    # 计算总产值 
                    tem_pro_value = record.posterior_passage_week_id.pro_value - abs(record.pro_value)
                # elif record.is_inferior == "次品":
                #     # 计算总产值 
                #     tem_pro_value = record.posterior_passage_week_id.pro_value + abs(record.pro_value)

                    # 查询相同款号的数量
                    style_number_obj = self.env["posterior_passage_output_value"].sudo().search([("style_number", "=", record.style_number.id), ("week", "=", record.week)])
                    
                    # 如果只有一个，则删除，否则则不删除
                    if len(style_number_obj) == 1:
                        tem_style_number_list = record.posterior_passage_week_id.style_number.split(",")
                        if record.style_number.style_number in tem_style_number_list:
                            tem_style_number_list.remove(record.style_number.style_number)
                        tem_style_number = ",".join(tem_style_number_list)
                    else:
                        tem_style_number = record.posterior_passage_week_id.style_number

                    record.posterior_passage_week_id.sudo().write({
                        "style_number": tem_style_number,   # 款号
                        "number": record.posterior_passage_week_id.number - record.number,    # 件数
                        "num_people": tem_num_people,  # 人数
                        "pro_value": tem_pro_value,   # 产值
                    })

            dDate = record.date     # 日期


            super(PosteriorPassageOutputValue, record).unlink()

            # 删除时，设置后道进出明细
            following_process_detail_obj = self.env["following_process_detail"].sudo().search([
                ("dDate", "=", dDate)
            ])
            if following_process_detail_obj:
                following_process_detail_obj.sudo().set_following_process_enter()
                

        res = super(PosteriorPassageOutputValue, self).unlink()

        return res



class PosteriorPassageOutputValueWeek(models.Model):
    _name = 'posterior_passage_output_value_week'
    _description = '后道产值(周)'
    _order = "week desc"

    week = fields.Char('周')
    style_number = fields.Char('款号')
    number = fields.Integer('件数')
    pro_value = fields.Float('产值')
    num_people = fields.Integer('人数')
    # avg_value = fields.Float('人均产值')   