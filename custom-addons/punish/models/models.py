# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RewardPunishRecord(models.Model):
    _name = 'reward_punish_record'
    _description = '绩效考核记录单'
    _rec_name = 'emp_id'
    _order = "declare_time desc"
    _inherit = ['mail.thread']

    emp_id = fields.Many2one('hr.employee', string="员工", track_visibility='onchange')
    declare_time = fields.Date(string="申报时间", required=True, track_visibility='onchange')
    department2 = fields.Char(string="部门", related='emp_id.department_id.complete_name', track_visibility='onchange', store=True)
    record_type = fields.Selection([('reward', '奖励'),('punish', '绩效扣除'),('compensation', '赔偿')], string="申报类别", required=True, track_visibility='onchange')
    punish_type = fields.Selection([
        ("制度", "制度"),
        ("绩效", "绩效"),
        ("流程规范", "流程规范"),
        ("员工手册", "员工手册"),
        ("赔偿", "赔偿"),
        ], string="类型", required=True)
    kpi_deduct_marks = fields.Float(string="KPI扣分", track_visibility='onchange')
    money_amount = fields.Float(string="金额", track_visibility='onchange')
    record_matter = fields.Text(string="事项", track_visibility='onchange')
    propose_department = fields.Many2one('hr.department', string="提出部门", track_visibility='onchange')
    is_factory_manager_approval = fields.Boolean(string="厂长审批", track_visibility='onchange')
    is_general_manager_approval = fields.Boolean(string="总经理审批", track_visibility='onchange')
    matter_type = fields.Selection([('3p','3p'), ('qulity_control','品控'), ('production','生产'), ('warehouse','仓库')], string='事项类别')

    registrar_id = fields.Many2one("hr.employee", string="登记人", track_visibility='onchange', default=lambda self: self.env['hr.employee'].search([("name", "=", "沈欣1")]).id)
    state = fields.Selection([('草稿', '草稿'), ('等待厂长审批', '等待厂长审批'), ('等待总经理审批', '等待总经理审批'), ('审批通过', '审批通过')], string="状态", default="草稿", track_visibility='onchange')
    
    
    is_automatic = fields.Boolean(string="是否自动生成", default=False)
    event_date = fields.Date(string="事件日期")
    event_type = fields.Char(string="事件类型")

    # 状态改变
    def state_changes(self):
        button_type = self._context.get("type")

        for record in self:

            if button_type == "confirm":
                if record.state == "草稿":
                    record.state = "等待厂长审批"
                else:
                    raise ValidationError(f"单据状态异常！")
            elif button_type == "phase1":
                if record.state == "等待厂长审批":
                    record.state = "等待总经理审批"
                else:
                    raise ValidationError(f"单据状态异常！")
            elif button_type == "phase2":
                if record.state == "等待总经理审批":
                    record.state = "审批通过"
                elif record.state == "等待厂长审批":
                    record.state = "审批通过"
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


    # 批量审批
    def batch_approval(self):
        for record in self:
            if record.state != "草稿":
                record.state = "审批通过"
            else:
                raise ValidationError(f"选中了草稿状态的记录，尚未提交，无需审批！")
                

    @api.model
    def create(self, vals):

        res = super(RewardPunishRecord, self).create(vals)

        if res.emp_id:
            res.propose_department = res.emp_id.department_id.parent_id.id
        
        res.state = "等待厂长审批"

        return res



    def write(self, vals):

        if self.state != "草稿":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                
                raise ValidationError(f"审批过程中的单据, 不可修改！。")


        return super(RewardPunishRecord, self).write(vals)



    def unlink(self):

        for record in self:

            if record.state != "草稿":

                raise ValidationError(f"审批过程中的单据, 不可删除！。")
            
            if record.is_automatic:
                
                fsn_super_user_group = self.env.ref('fsn_base.fsn_super_user_group')
                # 判断是否是超级用户！
                if self.env.uid in fsn_super_user_group.users.ids or self.env.is_superuser():
                    pass
                else:
                    raise ValidationError(f"该单据为自动生成的单据，只有具有高级权限的用户可以删除！")


        return super(RewardPunishRecord, self).unlink()