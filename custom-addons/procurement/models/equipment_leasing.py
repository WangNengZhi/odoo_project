from odoo import models, fields, api
from odoo.exceptions import ValidationError




class EquipmentLeasing(models.Model):
    _name = 'equipment_leasing'
    _description = '物品租赁'
    _rec_name = 'device_name'
    _order = "start_date desc"


    date = fields.Date(string="申请日期", required=True)


    start_date = fields.Datetime(string="租赁开始时间", required=True)
    end_data = fields.Datetime(string="租赁结束时间", required=True)

    lease_duration = fields.Float(string="租赁时长", required=True)
    time_unit = fields.Selection([('秒','秒'), ('分钟','分钟'), ('小时','小时'), ('天','天'), ('星期','星期'), ('月','月'), ('年','年')], string="租赁时间单位", required=True)



    device_name = fields.Char(string="物品名称", required=True)
    unit = fields.Char(string="物品单位", required=True)
    specification = fields.Char(string="规格", required=True)


    amount = fields.Float(string="数量")
    unit_price = fields.Float(string="单价")
    money_sum = fields.Float(string="金额", compute="_set_money_sum", store=True)
    # 计算总价格
    @api.depends('lease_duration', 'amount', 'unit_price')
    def _set_money_sum(self):
        for record in self:

            record.money_sum = record.amount * record.unit_price * record.lease_duration



    apply_department = fields.Many2one("hr.department", string="租赁部门", required=True)
    firm_principal = fields.Many2one('hr.employee', string="租赁负责人", required=True)
    manager = fields.Many2one('hr.employee', string="主管/经理", required=True)


    approve_state = fields.Selection([('草稿', '草稿'), ('已审批', '已审批')], string="审批状态", default="草稿")


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
            'res_model': 'equipment_leasing',
            'view_id': self.env.ref('procurement.equipment_leasing_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action



    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.approve_state = "草稿"
        elif button_type == "through":
            self.approve_state = "已审批"






