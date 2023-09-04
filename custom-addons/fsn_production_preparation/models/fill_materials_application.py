from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FillMaterialsApplication(models.Model):
    _name = 'fill_materials_application'
    _description = '补料申请表'
    _rec_name = 'style_number'
    _order = "application_date desc"


    application_date = fields.Date(string="申请日期", required=True)
    fsn_staff_team_id = fields.Many2one("fsn_staff_team", string="组别", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    style_number = fields.Many2one("ib.detail", string="款号", required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
            
    materials_name = fields.Char(string="材料名称", required=True)
    color = fields.Char(string="颜色")
    size = fields.Many2one("fsn_size", string="尺码")
    amount = fields.Integer(string="数量")
    unit = fields.Char(string="单位")
    lack_cause = fields.Char(string="缺少材料原因")
    comment = fields.Char(string="备注")
    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")


    department_id = fields.Many2one("hr.department", string="部门", required=True)
    employee_id = fields.Many2one('hr.employee', string="负责人", required=True)




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
            'res_model': 'fill_materials_application',
            'view_id': self.env.ref('fsn_production_preparation.popup_window_fill_materials_application_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action


    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            if self.state == "已审批":
                self.state = "待审批"


        elif button_type == "through":
            if self.state == "待审批":
                self.state = "已审批"




    def write(self, vals):

        if self.state != "待审批":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"审批通过的单据, 不可修改！。")


        return super(FillMaterialsApplication, self).write(vals)



    def unlink(self):

        for record in self:

            if record.state != "待审批":

                raise ValidationError(f"审批通过的的单据, 不可删除！。")

        return super(FillMaterialsApplication, self).unlink()