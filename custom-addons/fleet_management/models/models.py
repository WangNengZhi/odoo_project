# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FleetManagement(models.Model):
    _name = 'fleet_management'
    _description = '车队管理'
    _rec_name = 'numerical_order'
    _order = "date desc"

    numerical_order = fields.Integer(string="序号", required=True)
    date = fields.Date(string="日期", required=True)

    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    style_number = fields.Many2one('ib.detail', string='款号')
    number = fields.Float(string="数量")
    type = fields.Selection([
        ("面料", "面料"),
        ("辅料", "辅料"),
        ("成衣", "成衣"),
        ("人及行李", "人及行李"),
        ("招聘", "招聘"),
    ], string="类型")



    cause = fields.Text(string="出车事由", required=True)



    user_people = fields.Char(string="使用人")
    user_people_id = fields.Many2one('hr.employee', string="使用人", required=True)


    out_of_time = fields.Datetime(string="出车时间", required=True)
    return_time = fields.Datetime(string="归还时间", required=True)

    departure_photos = fields.Image(string='启程照片', required=True)
    arrival_photo = fields.Image(string='到达照片', required=True)
    before_refueling = fields.Image(string='加油前照片', required=True)
    after_refueling = fields.Image(string='加油后照片', required=True)


    return_people = fields.Char(string="归还人")
    return_people_id = fields.Many2one('hr.employee', string="归还人", required=True)

    
    remark = fields.Char(string="备注")

    plan_mileage = fields.Float(string="计划里程")
    the_actual_mileage = fields.Float(string="实际里程", required=True)
    fuel_consumption = fields.Float(string="百公里油耗(升)", required=True)
    practical_gasoline = fields.Float(string="实际油耗(升)", compute="set_practical_gasoline", store=True)
    today_oil_price = fields.Float(string="今日油价(金额/升)", required=True)
    actual_costs = fields.Float(string="计算费用", compute="set_actual_costs", store=True)

    destination = fields.Char(string="目的地", required=True)
    # oil_cost = fields.Float(string="实际油耗", compute="set_oil_cost", store=True)

    practical_costs = fields.Float(string="实际费用", required=True)


    # 生成费用
    def create_team_cost(self):
        for record in self:
            team_cost_obj = self.env["team_cost"].sudo().search([("fleet_management_id", "=", record.id)])
            if team_cost_obj:
                team_cost_obj.sudo().set_fleet_management_info()
            else:
                self.env["team_cost"].sudo().create({
                    "fleet_management_id": record.id,
                })

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('操作成功！'),
                'message': f'序号{record.numerical_order}操作成功！',
                'sticky': False,
                'type': 'success'
            },
        }
        return notification



    @api.constrains('numerical_order', 'today_oil_price')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('numerical_order', '=', record.numerical_order)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在序号为：{record.numerical_order}的记录了！")
            if record.today_oil_price == 0:
                raise ValidationError(f"今日油价不可为0！")


    # 计算实际油耗
    @api.depends('the_actual_mileage', 'fuel_consumption')
    def set_practical_gasoline(self):
        for record in self:
            # 实际油耗 = 实际里程 * （百公里油耗 / 100）
            record.practical_gasoline = record.the_actual_mileage * (record.fuel_consumption / 100)

    # 计算实际费用
    @api.depends('practical_gasoline', 'today_oil_price')
    def set_actual_costs(self):
        for record in self:
            # 实际费用 = 今日油价 * 实际油耗
            record.actual_costs = record.today_oil_price * record.practical_gasoline