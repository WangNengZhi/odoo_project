# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.expense'

    fsn_department = fields.Many2one("hr.department", string="部门")
    category = fields.Char(string="类别")
    fsn_product = fields.Char(string="产品")
    cost_type_id = fields.Many2one("cost_type", string="成本类别")
    expense_type_id = fields.Many2one("expense_type", string="费用类别")


    @api.onchange('cost_type_id')
    def _onchange_expense_type_id(self):

        self.expense_type_id = False

        if self.cost_type_id:
            return {'domain': {'expense_type_id': [('cost_type_id', '=', self.cost_type_id.id), ('lock_state', '=', '已审批')]}}
        else:
            return {'domain': {'expense_type_id': []}}



    @api.model
    def get_empty_list_help(self, help):
        # 重写该方法，取消帮助信息提示
        pass

    # 重写该方法，注释掉了不填写产品弹出的错误提示。
    def _create_sheet_from_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        # if any(not expense.product_id for expense in self):
        #     raise UserError(_("You can not create report without product."))

        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        sheet = self.env['hr.expense.sheet'].create({
            'company_id': self.company_id.id,
            'employee_id': self[0].employee_id.id,
            'name': todo[0].name if len(todo) == 1 else '',
            'expense_line_ids': [(6, 0, todo.ids)]
        })
        return sheet


    # 设置盘点模块的成本数据
    def set_money_flow(self):

        date = str(self.date)
        date = date[0:7]

        money_flow_objs = self.env["money_flow"].sudo().search([
            ("month", "=", date)
        ])
        if money_flow_objs:
            # 运输费
            if self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_freight').id:
                money_flow_objs.sudo().set_transport_cost()
            # 办公费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_office').id:
                money_flow_objs.sudo().set_office_cost()
            # 生产成本费用
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_production_costs').id:
                money_flow_objs.sudo().set_production_cost()
            # 工资费用
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_wages').id:
                money_flow_objs.sudo().set_wages_cost()
            # 公积金及社保
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_social_security').id:
                money_flow_objs.sudo().set_social_security_cost()
            # 税费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_taxation').id:
                money_flow_objs.sudo().set_taxation_cost()
            # 加油费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_refueling_fee').id:
                money_flow_objs.sudo().set_refuelingr_cost()
            # 员工餐费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_meals').id:
                money_flow_objs.sudo().set_staff_meals_cost()
            # 厂房租金
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_plant_rent').id:
                money_flow_objs.sudo().set_plant_rent_cost()
            # 固定资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_fixed_assets').id:
                money_flow_objs.sudo().set_fixed_assets_cost()
            # 无形资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_intangible').id:
                money_flow_objs.sudo().set_intangible_assets()
            # 其他资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_other_expenses').id:
                money_flow_objs.sudo().set_other_cost()
        else:
            new_obj = money_flow_objs.sudo().create({
                "month": date,
            })
            # 运输费
            if self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_freight').id:
                new_obj.sudo().set_transport_cost()
            # 办公费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_office').id:
                new_obj.sudo().set_office_cost()
            # 生产成本费用
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_production_costs').id:
                new_obj.sudo().set_production_cost()
            # 工资费用
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_wages').id:
                new_obj.sudo().set_wages_cost()
            # 公积金及社保
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_social_security').id:
                new_obj.sudo().set_social_security_cost()
            # 税费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_taxation').id:
                new_obj.sudo().set_taxation_cost()
            # 加油费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_refueling_fee').id:
                new_obj.sudo().set_refuelingr_cost()
            # 员工餐费
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_meals').id:
                new_obj.sudo().set_staff_meals_cost()
            # 厂房租金
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_plant_rent').id:
                new_obj.sudo().set_plant_rent_cost()
            # 固定资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_fixed_assets').id:
                new_obj.sudo().set_fixed_assets_cost()
            # 无形资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_intangible').id:
                new_obj.sudo().set_intangible_assets()
            # 其他资产
            elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_other_expenses').id:
                new_obj.sudo().set_other_cost()


    # 减少成本模块的运营数据(删除时使用)
    def reduce_money_flow_data(self):

        date = str(self.date)
        date = date[0:7]

        money_flow_objs = self.env["money_flow"].sudo().search([
            ("month", "=", date)
        ])
        # 运输费
        if self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_freight').id:
            money_flow_objs.write({
                "transport_cost": money_flow_objs.transport_cost - self.total_amount
            })
        # 办公费
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_office').id:
            money_flow_objs.write({
                "office_cost": money_flow_objs.office_cost - self.total_amount
            })
        # 生产成本费用
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_production_costs').id:
            money_flow_objs.write({
                "production_cost": money_flow_objs.production_cost - self.total_amount
            })
        # 工资费用
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_wages').id:
            money_flow_objs.write({
                "wages_cost": money_flow_objs.wages_cost - self.total_amount
            })
        # 公积金及社保
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_social_security').id:
            money_flow_objs.write({
                "social_security_cost": money_flow_objs.social_security_cost - self.total_amount
            })
        # 税费
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_taxation').id:
            money_flow_objs.write({
                "taxation_cost": money_flow_objs.taxation_cost - self.total_amount
            })
        # 加油费
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_refueling_fee').id:
            money_flow_objs.write({
                "refuelingr_cost": money_flow_objs.refuelingr_cost - self.total_amount
            })
        # 员工餐费
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_meals').id:
            money_flow_objs.write({
                "staff_meals_cost": money_flow_objs.staff_meals_cost - self.total_amount
            })
        # 厂房租金
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_plant_rent').id:
            money_flow_objs.write({
                "plant_rent_cost": money_flow_objs.plant_rent_cost - self.total_amount
            })
        # 固定资产
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_fixed_assets').id:
            money_flow_objs.write({
                "fixed_assets_cost": money_flow_objs.fixed_assets_cost - self.total_amount
            })
        # 无形资产
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_intangible').id:
            money_flow_objs.write({
                "intangible_assets": money_flow_objs.intangible_assets - self.total_amount
            })
        # 其他资产
        elif self.cost_type_id.id == self.env.ref('fsn_expenses.cost_type_other_expenses').id:
            money_flow_objs.write({
                "other_cost": money_flow_objs.other_cost - self.total_amount
            })




    def write(self, vals):
        # 修改类型之前
        if 'cost_type_id' in vals or 'date' in vals:
            self.reduce_money_flow_data()

        res = super(HrEmployee, self).write(vals)

        # 修改类型之后
        if 'cost_type_id' in vals or 'date' in vals:
            self.sudo().set_money_flow()
        else:
            if 'quantity' in vals or 'unit_amount' in vals or 'tax_ids' in vals:
                # 修改同步成本数据
                self.sudo().set_money_flow()

        return res


    @api.model
    def create(self, vals):

        res = super(HrEmployee, self).create(vals)

        # 创建完成后同步成本数据
        res.sudo().set_money_flow()

        return res


    def unlink(self):
        for record in self:

            # 删除时同步盘点模块的成本数据
            record.reduce_money_flow_data()

        return super(HrEmployee, self).unlink()





class CostType(models.Model):
    _name = "cost_type"
    _description = '成本类别'

    name = fields.Char(string="成本类型名称", required=True)



class ExpenseType(models.Model):
    _name = "expense_type"
    _description = '费用类别'
    _order = "create_date desc"



    name = fields.Char(string="费用类型名称", required=True)
    cost_type_id = fields.Many2one("cost_type", string="成本类别id", required=True)
    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")

    def set_lock_state(self):
        ''' 设置审批状态'''

        for record in self:
            lock_state = self.env.context.get("lock_state")
            if lock_state == "已审批":
                record.sudo().lock_state = "已审批"
            elif lock_state == "未审批":
                record.sudo().lock_state = "未审批"



    def check_lock_state(self):
        ''' 检查审批状态'''
        if self.lock_state == "已审批":
            raise ValidationError(f"记录已审批，不可对其进行操作！")


    def write(self, vals):
        for record in self:
            if "lock_state" not in vals:
                record.check_lock_state()
        res = super(ExpenseType, self).write(vals)
        return res


    def unlink(self):
        for record in self:
            record.check_lock_state()
        res = super(ExpenseType, self).unlink()
        return res