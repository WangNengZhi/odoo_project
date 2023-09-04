from datetime import datetime, date, time, timedelta
from odoo import api, fields, models
from utils import weixin_utils
from odoo.exceptions import ValidationError


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'
    _order = "start_datetime desc"


    dDate = fields.Date(string="日期", required=True)
    staff_group = fields.Char(string="员工小组", required=True)
    number_people = fields.Float(string="人数")

    department_id = fields.Selection([
        ('车间', '车间'),
        ('裁床', '裁床'),
        ('后道', '后道'),
    ], string='部门', required=True)

    group_leader = fields.Many2one("hr.employee", string="组长", required=True)
    plan_number = fields.Integer(string="计划数量")
    plan_output_value = fields.Float(string="计划产值", compute="set_plan_output_value", store=True)
    actual_number = fields.Integer(string="实际数量")
    progress_bar = fields.Float(string="进度", compute="get_progress_bar", store=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    product_size = fields.Many2one("fsn_size", string="尺码", required=True)
    plan_type = fields.Selection([
        ('生产', '生产'),
        ('返修', '返修'),
    ], string='计划类别', required=True)
    repair_source = fields.Selection([
        ('客户返修', '客户返修'),
        ('后道返修', '后道返修'),
        ('组上组检返修', '组上组检返修'),
    ], string="返修来源")

    plan_stage = fields.Selection([
        ('开款第一天', '开款第一天'),
        ('开款第二天', '开款第二天'),
        ('正常', '正常'),
    ], string="计划阶段", required=True)




    target_avg_production_value = fields.Integer(string="目标人均产值", required=True)
    unproduced_number = fields.Integer(string="剩余未生产数量", compute="set_unproduced_number", store=True)
    priority = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ], string='优先级', required=True, default="2")


    start_datetime = fields.Datetime(
        "Start Date", store=True, required=True,
        copy=True)
    end_datetime = fields.Datetime(
        "End Date", store=True, required=True,
        copy=True)

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
            raise ValidationError(f"该日计划已审批，不可对其进行操作！")
        
        

    @api.constrains('dDate', 'department_id', 'staff_group', 'style_number', 'product_size')
    def _check_uniqueness(self):

        demo = self.env[self._name].sudo().search([
            ('dDate', '=', self.dDate),     # 日期
            ("department_id", "=", self.department_id),     # 部门
            ("staff_group", "=", self.staff_group),     # 员工小组
            ("style_number", "=", self.style_number.id),    # 款号
            ("product_size", "=", self.product_size.id),    # 尺码
        ])
        if len(demo) > 1:
            raise ValidationError(f"{self.dDate}-{self.department_id}-{self.staff_group}-{self.style_number.style_number}-{self.product_size.name}的记录已经存在了！不可重复创建。")


    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}


    def set_time_range(self):
        for record in self:

            if record.dDate:
                # 日期
                dDate = record.dDate
                # 开始时间
                start_datetime = datetime.combine(dDate, time()) - timedelta(hours=8)
                # 结束时间
                end_datetime = datetime.combine(start_datetime, datetime.max.time()) + timedelta(hours=16)

                record.start_datetime = start_datetime

                record.end_datetime = end_datetime


    @api.depends('order_number', 'order_number.order_price', 'plan_number')
    def set_plan_output_value(self):
        """ 设置计划产值"""
        for record in self:

            record.plan_output_value = record.plan_number * float(record.order_number.order_price)




    @api.depends('plan_number', 'actual_number')
    def get_progress_bar(self):
        ''' 设置进度条'''
        for record in self:

            tem_dict = {"obj_ids": [], "plan_number": 0, "actual_number": 0}

            planning_slot_objs_list = self.env["planning.slot"].sudo().search_read(
                [('dDate', '=', record.dDate), ('staff_group', '=', record.staff_group)],
                ["plan_number", "actual_number"]
            )

            for planning_slot_obj in planning_slot_objs_list:
                tem_dict["plan_number"] = tem_dict["plan_number"] + planning_slot_obj["plan_number"]
                tem_dict["actual_number"] = tem_dict["actual_number"] + planning_slot_obj["actual_number"]
                tem_dict["obj_ids"].append(planning_slot_obj["id"])


            objs = self.browse(tem_dict["obj_ids"])
            for obj in objs:
                obj.progress_bar = (tem_dict["actual_number"] / tem_dict["plan_number"]) * 100




    def set_data(self):
        ''' 设置实际数量'''
        for record in self:
            date = record.start_datetime.date()
            pro_pro_objs = self.env["pro.pro"].sudo().search([
                ("date", "=", date),
                ("style_number", "=", record.style_number.id),
                '|', ("group", "=", record.staff_group[0:1]), ("group", "=", record.staff_group)
            ])
            tem_actual_number = 0
            for pro_pro_obj in pro_pro_objs:
                tem_actual_number = tem_actual_number + pro_pro_obj.number

            record.actual_number = tem_actual_number


    @api.depends('style_number', 'actual_number')
    def set_unproduced_number(self):
        ''' 设置剩余未生产数量'''
        for record in self:

            planning_slot_objs = self.env["planning.slot"].sudo().search([
                ("style_number", "=", record.style_number.id),
                ("dDate", "<=", record.dDate)
            ])

            tem_actual_number = 0
            for planning_slot_objs in planning_slot_objs:
                tem_actual_number = tem_actual_number + planning_slot_objs.actual_number

            record.unproduced_number = record.style_number.s_totle - tem_actual_number


    @api.model
    def create(self, vals):

        rec = super(PlanningSlot, self).create(vals)

        # 设置开始时间和结束时间
        rec.set_time_range()
        return rec


    def write(self, vals):

        if "lock_state" not in vals:

            self.check_lock_state()


        res = super(PlanningSlot, self).write(vals)

        # 设置开始时间和结束时间
        if "dDate" in vals:
            self.set_time_range()

        return res


    def unlink(self):
        for record in self:
            record.check_lock_state()

        res = super(PlanningSlot, self).unlink()

        return res
    
    def fsn_anomaly_detection(self):
        exception_message = ""
        for record in self:

            schedule_production_obj = self.env['schedule_production'].sudo().search([
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("size", "=", record.product_size.id)
            ])



            if not schedule_production_obj:

                exception_message += f"订单号:{record.order_number.order_number}，款号:{record.style_number.style_number}，尺码:{record.product_size.name}，存在异常！\n"
                    
        raise ValidationError(exception_message)



    def send_daily_production_plan_to_enterprise_weixin(self):
        ''' 发送各组当天的生产计划到企业微信 '''
        now = datetime.now()
        data = self.sudo().search([
            ('start_datetime', '<=', now),
            # (now, '<=', 'end_datetime')  # Wrong !
            ('end_datetime', '>=', now)])

        if not data:
            return

        def format(d):
            return f'{d.staff_group}计划生产{d.plan_number}件{d.style_number.style_number}款式。'

        text = f'本日（{now.date()}）计划生产数量：\n\n'
        text += '\n'.join(format(d) for d in data)

        # print(text)
        # weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.DEVELOPMENT_AND_TEST)
        weixin_utils.send_app_group_info_text_weixin(text, weixin_utils.ADMIN_GROUP)




