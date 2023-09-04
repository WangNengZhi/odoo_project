from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TemporaryWorkersApply(models.Model):
    _name = 'temporary_workers_apply'
    _description = '临时工申请'
    _rec_name = 'style_number'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    state = fields.Selection([('等待厂长审批', '等待厂长审批'), ('等待总经理审批', '等待总经理审批'), ('审批通过', '审批通过')], string="状态", default="等待厂长审批", track_visibility='onchange')
    


    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_id')
    def style_number_domain(self):
        self.style_number = False
        if self.order_id:
            
            return {'domain': {'style_number': [("id", "in", self.order_id.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
    style = fields.Char(string="款式")
    number = fields.Float(string="件数")
    process_no = fields.Many2one("work.work", string="工序号", required=True)
    process_no_name = fields.Char(string="工序号名称", related="process_no.employee_id", store=True)
    @api.onchange('style_number')
    def process_no_domain(self):
        self.process_no = False
        if self.style_number:
            return {'domain': {'process_no': [("id", "in", self.env['work.work'].search(["|", ("order_number", "=", self.style_number.id), ("employee_id", "=", "9999")]).ids)]}}
        else:
            return {'domain': {'process_no': []}}

    process_abbreviation = fields.Char(string='工序描述')
    standard_time = fields.Float(string='标准工时')
    standard_price = fields.Float(string='标准工价')
    @api.onchange('process_no')
    def set_process_info(self):
        for record in self:
            record.process_abbreviation = record.process_no.process_abbreviation
            record.standard_time = record.process_no.standard_time
            record.standard_price = record.process_no.standard_price


    apply_price = fields.Float(string="申请价格")

    price_per_person = fields.Float(string="总价格", compute="set_price_per_person", store=True)
    @api.depends("apply_price", "number")
    def set_price_per_person(self):
        for record in self:
            record.price_per_person = record.apply_price * record.number

    applications = fields.Integer(string="申请临时工人数")

    total_price = fields.Float(string="单人价格", compute="set_total_price", store=True)
    @api.depends("price_per_person", "applications")
    def set_total_price(self):
        for record in self:
            if record.applications:
                record.total_price = record.price_per_person / record.applications
            else:
                record.total_price = 0



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
            'res_model': 'temporary_workers_apply',
            'view_id': self.env.ref('fsn_employee.temporary_workers_apply_examine_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action


    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            if self.state == "等待总经理审批":
                self.state = "等待厂长审批"
            elif self.state == "审批通过":
                self.state = "等待厂长审批"
        elif button_type == "through":
            if self.state == "等待厂长审批":
                self.state = "等待总经理审批"
            elif self.state == "等待总经理审批":
                self.state = "审批通过"



    def write(self, vals):

        if self.state != "等待厂长审批":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"审批过程中的单据, 不可修改！。")


        return super(TemporaryWorkersApply, self).write(vals)



    def unlink(self):

        for record in self:

            if record.state != "等待厂长审批":

                raise ValidationError(f"审批过程中的单据, 不可删除！。")

        return super(TemporaryWorkersApply, self).unlink()


