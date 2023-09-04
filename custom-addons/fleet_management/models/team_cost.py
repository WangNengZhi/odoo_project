from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TeamCost(models.Model):
    _name = 'team_cost'
    _description = '车队费用'
    _rec_name = 'fleet_management_id'
    _order = "date desc"

    
    fleet_management_id = fields.Many2one("fleet_management", string="车队管理", ondelete='cascade')
    date = fields.Date(string="日期", compute="set_fleet_management_info", store=True)
    cause = fields.Char(string="出车事由", compute="set_fleet_management_info", store=True)
    user_people_id = fields.Many2one('hr.employee', string="使用人", compute="set_fleet_management_info", store=True)

    before_refueling = fields.Image(string='加油前照片', compute="set_fleet_management_info", store=True)
    after_refueling = fields.Image(string='加油后照片', compute="set_fleet_management_info", store=True)

    cost = fields.Float(string="费用", compute="set_fleet_management_info", store=True)
    # 设置车队费用信息
    @api.depends('fleet_management_id', 'fleet_management_id.date', 'fleet_management_id.cause',
                 'fleet_management_id.user_people_id', 'fleet_management_id.practical_costs',
                 'fleet_management_id.before_refueling', 'fleet_management_id.after_refueling')
    def set_fleet_management_info(self):
        for record in self:
            record.date = record.fleet_management_id.date
            record.cause = record.fleet_management_id.cause
            record.user_people_id = record.fleet_management_id.user_people_id.id
            record.cost = record.fleet_management_id.practical_costs
            record.before_refueling = record.fleet_management_id.before_refueling
            record.after_refueling = record.fleet_management_id.after_refueling


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
            'res_model': 'team_cost',
            'view_id': self.env.ref('fleet_management.team_cost_form').id,
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

        if self.state == "已出库":

            if "state" in vals and len(vals) == 1:
                pass
            else:

                raise ValidationError(f"已经审批通过的记录不可修改！")

        res = super(TeamCost, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "确认":

                raise ValidationError(f"已经审批通过的记录不可删除！")


        res = super(TeamCost, self).unlink()

        return res