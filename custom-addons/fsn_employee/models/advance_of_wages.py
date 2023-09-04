from odoo.exceptions import ValidationError
from odoo import models, fields, api


class AdvanceOfWages(models.Model):
    _name = 'advance_of_wages'
    _description = '预支工资记录'
    _rec_name='employee_id'
    _order = "dDate desc"



    dDate = fields.Date(string="日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工', required=True)
    contract_attribute = fields.Char(string="合同属性", compute="set_contract_attribute", store=True)
    outsourcing_type = fields.Char(string="外包类型", compute="set_contract_attribute", store=True)
    @api.depends("employee_id")
    def set_contract_attribute(self):
        for record in self:
            record.contract_attribute = record.employee_id.contract_attributes
            record.outsourcing_type = record.employee_id.outsourcing_type
            
    working_state = fields.Boolean(related='employee_id.is_delete', string='是否离职')
    is_delete_date = fields.Date(related='employee_id.is_delete_date', string='离职时间')
    approve_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批'), ('未通过', '未通过')], string="审批状态", default="未审批", required=True)
    refused_note = fields.Char(string="备注")
    wages_type = fields.Selection([('借款', '借款'), ('薪酬', '薪酬'), ('补发', '补发'), ('奖金', '奖金')], string="预支类型", required=True)

    company_id = fields.Many2one('res.company')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    money = fields.Monetary(string="金额", currency_field='company_currency_id')




    # @api.depends('employee_id')
    # def set_company_id(self):
    #     for record in self:
    #         record.company_id = self.env.company.id

    # 设置审批状态
    def set_approve_state(self):

        for record in self:
            print(record)

    # 状态回退
    def state_back(self):

        for record in self:

            record.approve_state = "未审批"


    def test(self):
        print('---------------')
        print(self)

        print(self.mapped('money'))

        print(self.search_read([('money', '>=', 2000)], ["id", "employee_id"]))

        print(self.filtered(lambda x: x.working_state == False))


    def write(self, vals):

        for record in self:
            if record.approve_state == "已审批":
                if ("approve_state" in vals) and len(vals) == 1:
                    pass
                else:

                    raise ValidationError(f"已审批的记录, 不可编辑！")


        res = super(AdvanceOfWages, self).write(vals)

        return res


    def unlink(self):

        for record in self:
            if record.approve_state == "已审批":

                raise ValidationError(f"已审批的记录, 不可删除！")

        res = super(AdvanceOfWages, self).unlink()

        return res



class AdvanceOfWagesWizard(models.TransientModel):
    _name = 'advance_of_wages_wizard'
    _description = '预支工资审批向导'
    # _order = 'id asc'


    refused_note = fields.Char(string="备注")

    # 审批通过
    def action_audit_through(self):

        active_id = self.env.context.get('active_id')  # 获取记录id
        active_model = self.env.context.get('active_model') # 获取记录模型名称

        record_obj = self.env[active_model].sudo().browse(active_id)     # 获取记录对象

        record_obj.refused_note = False

        record_obj.approve_state = "已审批"




    # 审批拒绝
    def action_audit_refused(self):

        active_id = self.env.context.get('active_id')  # 获取记录id
        active_model = self.env.context.get('active_model') # 获取记录模型名称

        record_obj = self.env[active_model].sudo().browse(active_id)     # 获取记录对象

        record_obj.approve_state = "未通过"

        record_obj.refused_note = self.refused_note



