from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FoodBeverageCosts(models.Model):
    _name = 'food_beverage_costs'
    _description = '餐饮费用'



    date = fields.Date(string="日期", required=True)
    cause = fields.Char(string="事由", required=True)
    user_people_id = fields.Many2one('hr.employee', string="使用人", required=True)

    starting_point = fields.Char(string="起点", required=True)
    out_of_time = fields.Datetime(string="出发时间", required=True)
    destination = fields.Char(string="目的地", required=True)
    arrival_time = fields.Datetime(string="到达时间", required=True)

    costs = fields.Float(string="费用", required=True)

    remark = fields.Char(string="备注")
    state = fields.Selection([('草稿', '草稿'), ('确认', '确认')], string="状态", default="草稿")




    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"

        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'food_beverage_costs',
            'view_id': self.env.ref('fsn_travel.food_beverage_costs_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action



    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.state = "草稿"
        elif button_type == "through":
            self.state = "确认"



    def write(self, vals):

        if self.state == "确认":

            if "state" in vals and len(vals) == 1:
                pass
            else:

                raise ValidationError(f"已经审批通过的记录不可修改！")

        res = super(FoodBeverageCosts, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "确认":

                raise ValidationError(f"已经审批通过的记录不可删除！")


        res = super(FoodBeverageCosts, self).unlink()

        return res
