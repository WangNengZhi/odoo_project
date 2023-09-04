from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta


class WarehouseOut(models.Model):
    _name = 'warehouse_out'
    _description = '出库产值'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one("sale_pro.sale_pro", string="销售订单", required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    number = fields.Integer('件数')
    week = fields.Char(string="周")
    num_people = fields.Integer('人数', required=True)
    pro_value = fields.Float(string="出库产值", compute="set_pro_value", store=True)
    is_inferior = fields.Selection([('合格', '合格'),('次品', '次品')],string="合格/次品", required=True)
    warehouse_out_week_id = fields.Many2one("warehouse_out_week", string="出库产值(周)")


    @api.constrains('date', "style_number", 'is_inferior')
    def _check_unique(self):
        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ("style_number", "=", self.style_number.id),
            ("is_inferior", "=", self.is_inferior),
            ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在日期为：{self.date}款号为：{self.style_number.style_number}的{self.is_inferior}后道产值记录了！")


    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)


    @api.model
    def create(self, vals):
        if vals["num_people"] <= 0:
            raise ValidationError(f"人数必须大于0！")

        datetime_obj = datetime.strptime(vals['date'], "%Y-%m-%d")
        year = datetime_obj.year
        week = datetime_obj.isocalendar()
        vals["week"] = f"{year}年第{week[1]}周"


        instance = super(WarehouseOut, self).create(vals)

        # 查询出库产值（周）表中有没有该组的记录
        warehouse_out_week_obj = self.env["warehouse_out_week"].sudo().search([("week", "=", vals["week"])])

        if warehouse_out_week_obj:
            instance.warehouse_out_week_id = warehouse_out_week_obj.id

            instance.warehouse_out_week_id.set_data()

        else:

            if instance.is_inferior == "合格":

                new_warehouse_out_week_obj = self.env["warehouse_out_week"].sudo().create({
                    "week": vals["week"],   # 周

                })
                instance.warehouse_out_week_id = new_warehouse_out_week_obj.id


        instance.warehouse_out_week_id.set_data()

        return instance





    def unlink(self):

        tem_obj = self.warehouse_out_week_id

        instance = super(WarehouseOut, self).unlink()

        tem_obj.set_data()

        return instance


class WarehouseOutWeek(models.Model):
    _name = 'warehouse_out_week'
    _description = '出库产值(周)'
    _order = "week desc"


    week = fields.Char('周')
    style_number = fields.Char('款号')
    number = fields.Integer('件数')
    pro_value = fields.Float('产值')
    num_people = fields.Integer('人数')


    def set_data(self):

        objs = self.env["warehouse_out"].sudo().search([
            ("week", "=", self.week)
        ])

        if objs:

            tem_str = ""
            tem_number = 0
            tem_num_people = 0
            tem_pro_value = 0

            for obj in objs:
                tem_str = tem_str + obj.style_number.style_number + ","
                tem_number = tem_number + obj.number
                tem_num_people = tem_num_people + obj.pro_value
                tem_pro_value = tem_pro_value + obj.pro_value

            self.style_number = tem_str[0: -2]     # 款号
            self.number = tem_number    # 件数
            self.num_people = tem_num_people / len(objs)    # 人数
            self.pro_value = tem_pro_value      # 产值

        else:

            self.sudo().unlink()


