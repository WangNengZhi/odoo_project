from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OutboundPrice(models.Model):
    _name = 'outbound_price'
    _description = 'FSN外发价格'
    _rec_name = 'style_number'
    _order = "date desc"


    date = fields.Date(string='申请日期', required=True)
    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    process_name = fields.Char(string="工序名称")
    ie_working_hours = fields.Float(string="IE工时", digits=(16, 5))
    ie_working_price = fields.Float(string="IE工价", digits=(16, 5))
    outbound_price = fields.Float(string="外发单价")
    apply_price = fields.Float(string="申请价格")
    actual_number = fields.Integer(string="实做件数")
    total_amount = fields.Float(string="总金额", compute="set_total_amount", store=True)
    @api.depends("apply_price", "actual_number")
    def set_total_amount(self):
        for record in self:
            # 总金额 = 申请价格 * 实做件数
            record.total_amount = record.apply_price * record.actual_number

    
    outsource_plant_id = fields.Many2one("outsource_plant", string="外发加工厂", required=True)
    nuclear_price_people = fields.Many2one('hr.employee', string='核价人', required=True)
    applicant_people = fields.Many2one('hr.employee', string='申请人', required=True)

    state = fields.Selection([('草稿', '草稿'), ('等待厂长审批', '等待厂长审批'), ('等待总经理审批', '等待总经理审批'), ('审批通过', '审批通过')], string="状态", default="草稿")

    # 确认弹窗
    def confirmation_button(self):

        action = {

            'name': "确认执行此操作吗",
            'view_mode': 'form',
            'res_model': 'outbound_price',
            'view_id': self.env.ref('fsn_outsource.outbound_price_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': dict(self._context),

        }

        return action


    # 状态改变
    def state_changes(self):
        button_type = self._context.get("button_type")

        if button_type == "state_changes1":
            if self.state == "草稿":
                self.state = "等待厂长审批"
            else:
                raise ValidationError(f"单据状态异常！")
        elif button_type == "state_changes2":
            if self.state == "等待厂长审批":
                self.state = "等待总经理审批"
            else:
                raise ValidationError(f"单据状态异常！")
        elif button_type == "state_changes3":
            if self.state == "等待总经理审批":
                self.state = "审批通过"
        else:
            raise ValidationError(f"单据状态异常！")

    # 状态回退
    def state_back(self):

        button_type = self._context.get("button_type")

        if button_type == "state_back1":
            if self.state == "等待厂长审批":
                self.state = "草稿"
            else:
                raise ValidationError(f"单据状态异常！")
        elif button_type == "state_back2":
            if self.state == "等待总经理审批":
                self.state = "等待厂长审批"
            else:
                raise ValidationError(f"单据状态异常！")
        elif button_type == "state_back3":
            if self.state == "审批通过":
                self.state = "等待总经理审批"
        else:
            raise ValidationError(f"单据状态异常！")



    def write(self, vals):

        if self.state != "草稿":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"审批过程中的单据, 不可修改！。")


        return super(OutboundPrice, self).write(vals)



    def unlink(self):

        for record in self:
            if record.state != "草稿":

                raise ValidationError(f"审批过程中的单据, 不可删除！。")

        return super(OutboundPrice, self).unlink()