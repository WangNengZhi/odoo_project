from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PlanningSlot(models.Model):
    """ 继承计划"""
    _inherit = 'planning.slot'

    # 同步创建裁床产量记录
    def create_cutting_bed_production(self):
        cutting_bed_production_obj = self.env["cutting_bed_production"].sudo().search([("planning_slot_id", "=", self.id)])
        if cutting_bed_production_obj:
            if self.department_id != "裁床" or self.staff_group != "裁床":
                cutting_bed_production_obj.sudo().unlink()
        else:
            if self.department_id == "裁床" and self.staff_group == "裁床":
                cutting_bed_production_obj = self.env["cutting_bed_production"].sudo().search([
                    ("date", "=", self.dDate),
                    ("order_number", "=", self.order_number.id),
                    ("style_number", "=", self.style_number.id),
                    ("product_size", "=", self.product_size.id),
                ])
                if cutting_bed_production_obj:
                    cutting_bed_production_obj.planning_slot_id = self.id
                else:
                    self.env["cutting_bed_production"].sudo().create({
                        "planning_slot_id": self.id,
                    })


    @api.model
    def create(self, vals):

        res = super(PlanningSlot, self).create(vals)

        res.sudo().create_cutting_bed_production()

        return res



    def write(self, vals):

        res = super(PlanningSlot, self).write(vals)

        if "lock_state" in vals and len(vals) == 1:
            pass
        else:
            self.sudo().create_cutting_bed_production()

        return res


class CuttingBedProduction(models.Model):
    _name = 'cutting_bed_production'
    _description = '裁床产量'
    _rec_name = 'style_number'
    _order = "date desc"

    planning_slot_id = fields.Many2one("planning.slot", string="计划", ondelete="cascade")
    date = fields.Date(string="日期", compute="set_record_info", store=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', compute="set_record_info", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', compute="set_record_info", store=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        

        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
        
    product_size = fields.Many2one("fsn_size", string="尺码", compute="set_record_info", store=True)
    plan_productionp = fields.Float(string='计划产量', compute="set_record_info", store=True)
    plan_output_value = fields.Float(string="计划产值", compute="set_plan_output_value", store=True)
    @api.depends('plan_productionp', 'order_number', "order_number.order_price")
    def set_plan_output_value(self):
        for record in self:
            record.plan_output_value = float(record.order_number.order_price) * record.plan_productionp

    complete_productionp = fields.Float(string='完成产量')
    plan_complete_productionp = fields.Float(string="完成产值", compute="set_plan_complete_productionp", store=True)
    @api.depends('complete_productionp', 'order_number', "order_number.order_price")
    def set_plan_complete_productionp(self):
        for record in self:
            record.plan_complete_productionp = float(record.order_number.order_price) * record.complete_productionp

    @api.constrains('date', 'order_number', 'style_number', 'product_size')
    def _check_uniqueness(self):
        for record in self:
            demo = self.env[self._name].sudo().search([
                ('date', '=', record.date),
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("product_size", "=", record.product_size.id),
            ])
            if len(demo) > 1:
                raise ValidationError(f"{record.date}-{record.order_number.order_number}-{record.style_number.style_number}-{record.product_size.name}的记录已经存在了！不可重复创建。")



    @api.depends('planning_slot_id', 'planning_slot_id.dDate', 'planning_slot_id.order_number', 'planning_slot_id.style_number', 'planning_slot_id.product_size', 'planning_slot_id.plan_number')
    def set_record_info(self):
        for record in self:
            if record.planning_slot_id:
                record.date = record.planning_slot_id.dDate
                record.order_number = record.planning_slot_id.order_number.id
                record.style_number = record.planning_slot_id.style_number.id
                record.product_size = record.planning_slot_id.product_size.id
                record.plan_productionp = record.planning_slot_id.plan_number


    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")

    def set_lock_state(self):
        ''' 设置审批状态'''

        for record in self:
            lock_state = self.env.context.get("lock_state")
            if lock_state == "已审批":
                record.sudo().lock_state = "已审批"
            elif lock_state == "未审批":
                record.sudo().lock_state = "未审批"

    # 设置裁床产值
    def set_cutting_bed(self):
        hr_employee_objs = self.env['hr.employee'].sudo().search([("department_id.name", "=", "裁床部"), ("is_delete", "=", False)])
        num_people = len(hr_employee_objs)
        for record in self:

            cutting_bed_obj = self.env["cutting_bed"].sudo().search([
                ("date", "=", record.date),
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("product_size", "=", record.product_size.id),
            ])
            if not cutting_bed_obj:

                for hr_employee_obj in hr_employee_objs:
                    if self.env['every.detail'].sudo().search([("leave_officer", "=", hr_employee_obj.id), ("date", "<=", record.date), ("end_date", ">=", record.date)]):
                        num_people -= 1

                cutting_bed_obj = self.env["cutting_bed"].sudo().create({
                    "date": record.date,
                    "order_number": record.order_number.id,
                    "style_number": record.style_number.id,
                    "product_size": record.product_size.id,
                    "num_people": num_people,
                })

            cutting_bed_obj.cutting_bed_production_id = record.id


    @api.model
    def create(self, vals):

        res = super(CuttingBedProduction, self).create(vals)

        res.sudo().set_cutting_bed()

        return res



    def check_lock_state(self):
        ''' 检查审批状态'''
        if self.lock_state == "已审批":
            raise ValidationError(f"记录已审批，不可对其进行操作！")


    def write(self, vals):
        for record in self:
            if "lock_state" not in vals:
                record.check_lock_state()
        res = super(CuttingBedProduction, self).write(vals)
        return res


    def unlink(self):
        for record in self:
            if record.planning_slot_id and not self.user_has_groups("fsn_base.fsn_super_user_group"):
                raise ValidationError("该记录不可删除，如果有必要请联系管理员！")
            record.check_lock_state()
        res = super(CuttingBedProduction, self).unlink()
        return res
    




