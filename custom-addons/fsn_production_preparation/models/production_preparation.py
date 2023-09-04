from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleProLine(models.Model):
    _inherit = "sale_pro_line"


    
    def generate_production_preparation(self):
        for record in self:
            # self.env['production_preparation'].sudo().search([("sale_pro_line_id", "=", )])
            pass


    @api.model
    def create(self, vals):

        res = super(SaleProLine, self).create(vals)

        res.sudo().generate_production_preparation()

        return res



class ProductionPreparation(models.Model):
    _name = "production_preparation"
    _description = '产前准备'
    _rec_name = "order_number"
    _order = "date desc"



    sale_pro_line_id = fields.Many2one("sale_pro_line", string="订单明细")

    # 设置line_ids的默认值
    def _set_line_ids(self):
        sample_ids = self.env["production_preparation_line_sample"].search([])

        lines = []

        for sample_id in sample_ids:
            line = {
                "group_type": sample_id.group_type,      # 组别
                "before_go_online": sample_id.before_go_online,     # 新款上线前
                "content": sample_id.content,   # 内容
                "department_ids": sample_id.department_ids,     # 部门
                "sequence": sample_id.sequence,     # 排序
            }
            lines.append((0, 0, line))

        return lines

    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
    client = fields.Char(related="order_number.name", string="客户（旧）", store=True)
    client_id = fields.Many2one("fsn_customer", string="客户", related="order_number.customer_id", store=True)
    group = fields.Char(string="组别(旧)")
    group_id = fields.Many2one("fsn_staff_team", string="组别", required=True)
    date = fields.Date(string="日期", required=True)
    up_wire_date = fields.Date(string="上线日期", required=True)
    finish_plan_date = fields.Date(string="计划完成日期", required=True)

    th_per_management_id = fields.Many2one("th_per_management", string="样衣记录")
    sample_image = fields.Binary(string="样衣")
    # 设置样衣
    @api.onchange('th_per_management_id', 'th_per_management_id.sample_image')
    def set_sample_image(self):
        for record in self:
            if record.th_per_management_id:
                record.sample_image = record.th_per_management_id.sample_image

    fsn_process_sheet_id = fields.Many2one("fsn_process_sheet", string="工艺单记录")
    process_sheet = fields.Many2many(
        'ir.attachment',					#关联附件模型
        relation='process_sheet_res_att_rel',		#关联表（字段与 ir.attachment 表的附件的关联表名）
        column1='process_sheet_id',					# first_attachment 的 id 列
        column2='att_id',					# ir.attachment 表的附件 id 列
        string="工艺单"
    )

    # 设置工艺单
    @api.onchange('fsn_process_sheet_id', 'fsn_process_sheet_id.process_sheet_attachment_ids')
    def set_process_sheet(self):
        for record in self:
            if record.fsn_process_sheet_id:
                record.process_sheet = record.fsn_process_sheet_id.process_sheet_attachment_ids

    device_list = fields.Many2many(
        'ir.attachment',
        relation='device_list_res_att_rel',
        column1='device_list_id',
        column2='att_id',
        string="设备清单"
    )
    check_cloth_report = fields.Many2many(
        'ir.attachment',
        relation='check_cloth_report_res_att_rel',
        column1='check_cloth_report_id',
        column2='att_id',
        string="验布报告"
    )
    production_decision = fields.Many2many(
        'ir.attachment',
        relation='production_decision_res_att_rel',
        column1='production_decision_id',
        column2='att_id',
        string="生产方案"
    )
    process_requirement = fields.Many2many(
        'ir.attachment',
        relation='process_requirement_res_att_rel',
        column1='process_requirement_id',
        column2='att_id',
        string="工艺要求"
    )
    shell_fabric_card = fields.Many2many(
        'ir.attachment',
        relation='shell_fabric_card_res_att_rel',
        column1='shell_fabric_card_id',
        column2='att_id',
        string="面辅料卡"
    )
    line_ids = fields.One2many("production_preparation_line", "production_preparation_id", string="产前准备明细", default=_set_line_ids)


    @api.constrains('order_number', 'style_number')
    def _check_uniq(self):

        demo = self.env[self._name].sudo().search([('order_number', '=', self.order_number.id), ('style_number', '=', self.style_number.id)])
        if len(demo) > 1:
            raise ValidationError(f"相同订单号相同款号的记录已经存在了！不可重复创建。")



    # 设置款号件数汇总数据处的计划完成日期
    def set_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id),    # 款号
            ("order_number", "=", self.order_number.id)   # 订单号
        ])
        if style_number_summary_objs:
            style_number_summary_objs.sudo()._set_finish_plan_date()
        else:
            new_obj = style_number_summary_objs.sudo().create({
                "style_number": self.style_number.id,
                "order_number": self.order_number.id
            })
            new_obj.sudo()._set_finish_plan_date()


    # 删除时，清空款号件数汇总的计划完成日期字段
    def reduce_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id)
        ])
        style_number_summary_objs.sudo().write({
            "finish_plan_date": False
        })




    def write(self, vals):

        for record in self:

            res = super(ProductionPreparation, self).write(vals)


            record.set_style_number_summary()

        return res

 
    # 设置样衣记录
    def set_th_per_management_id(self):
        # self.env['th_per_management'].sudo().search([("")])
        pass

    @api.model
    def create(self, vals):

        res = super(ProductionPreparation, self).create(vals)

        res.set_style_number_summary()

        return res


    def unlink(self):

        for record in self:

            record.reduce_style_number_summary()

        record = super(ProductionPreparation, self).unlink()

        return record





class ProductionPreparationLine(models.Model):
    _name = "production_preparation_line"
    _description = '产前准备明细'
    _order = "sequence"


    group_type = fields.Selection([('1_3pgcxx', '3P过程信息'),
                                    ('2_swqr', '实物确认'),
                                    ('3_pxqzb', '培训前准备'),
                                    ('4_sbpx', '首包培训'),
                                    ('5_dhkkqzb', '大货开款前准备'),
                                    ('6_xczk', '现场转款'),
                                    ], string="组别")
    before_go_online = fields.Selection([('1_four_day', '四天'),
                                        ('2_three_day', '三天'),
                                        ('3_two_day', '两天'),
                                        ('4_punish', '当天'),
                                        ], string="新款上线前")
    production_preparation_id = fields.Many2one("production_preparation")
    content = fields.Char(string="内容")
    department_ids = fields.Many2many("hr.department", string="部门")
    sequence = fields.Integer(string="排序")
    person_in_charge = fields.Many2one("hr.employee", string="负责人")
    completion_date = fields.Date(string="完成日期")
    is_confirm = fields.Boolean(string="确认")

