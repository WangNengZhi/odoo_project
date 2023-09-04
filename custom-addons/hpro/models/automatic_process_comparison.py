from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AutomaticProcessComparison(models.Model):
    _name = 'automatic_process_comparison'
    _description = '自动工序对比'
    _rec_name = 'employee_id'
    _order = "date desc"

    date = fields.Date(string='日期')
    employee_id = fields.Many2one("hr.employee", string="员工id")
    work_type = fields.Char(string="工种", compute="set_work_type", store=True)
    departure_date = fields.Date(string="离职日期", compute="set_work_type", store=True)
    group = fields.Many2one('check_position_settings', string='组别')
    style_number_id = fields.Many2one('ib.detail', string='款号id')
    process_id = fields.Many2one('work.work', string="工序id（自动）")
    process_describe = fields.Char(string="工序描述（自动）", related="process_id.process_abbreviation", store=True)
    process_level = fields.Char(string="工序等级（自动）", related="process_id.process_level", store=True)
    process_time = fields.Float(string="标准时间（自动）", related="process_id.standard_time", store=True)
    process_price = fields.Float(string="工序价格（自动）", related="process_id.standard_price", store=True)
    number = fields.Float(string="件数（自动）", compute="set_automatic_process_info", store=True)


    on_work_process_id = fields.Integer(string="工序号（手动）", compute="set_manual_process_info", store=True)
    on_work_process_describe = fields.Char(string="工序描述（手动）", compute="set_manual_process_info", store=True)
    on_work_process_level = fields.Char(string="工序等级（手动）", compute="set_manual_process_info", store=True)
    on_work_process_time = fields.Float(string="标准时间（手动）", compute="set_manual_process_info", store=True)
    on_work_process_price = fields.Float(string="工序价格（手动）", compute="set_manual_process_info", store=True)
    on_work_number = fields.Float(string="件数（手动）", compute="set_manual_process_info", store=True)


    automatic_process_id = fields.Many2one("automatic_scene_process", string="自动工序id")

    manual_process_id = fields.Many2one("on.work", string="手动工序id")


    # 设置自动工序信息
    @api.depends('automatic_process_id')
    def set_automatic_process_info(self):
        for record in self:

            record.number = record.automatic_process_id.number

    # 设置手动工序信息
    @api.depends('manual_process_id')
    def set_manual_process_info(self):
        for record in self:

            record.on_work_process_id = record.manual_process_id.employee_id    # 工序号

            record.on_work_process_describe = record.manual_process_id.process_abbreviation     # 工序描述

            record.on_work_process_level = record.manual_process_id.process_level   # 工序等级

            record.on_work_process_time = record.manual_process_id.standard_time    # 工序标准时间

            record.on_work_process_price = record.manual_process_id.standard_price      # 工序价格

            record.on_work_number = record.manual_process_id.over_number    # 件数




    # 设置工种，在职状态
    @api.depends('employee_id')
    def set_work_type(self):
        for record in self:
            record.work_type = record.employee_id.is_it_a_temporary_worker

            record.departure_date = record.employee_id.is_delete_date





class OnWork(models.Model):
    """ 继承现场工序"""
    _inherit = 'on.work'


    # 设置工序对比
    def set_process_comparison(self):

        CN_NUM = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            }

        # 查询组别
        check_position_settings_obj = self.env["check_position_settings"].sudo().search([
            # ("group", "=", CN_NUM.get(self.group, self.group))
            ("group", "=", CN_NUM.get(self.group, None))
        ])

        if check_position_settings_obj:

            # 查询工序号
            work_work_obj = self.env["work.work"].sudo().search([
                ("employee_id", "=", str(self.employee_id)),
                ("order_number", "=", self.order_number.id)
            ])

            automatic_process_comparison_objs = self.env["automatic_process_comparison"].sudo().search([
                ("date", "=", self.date1),  # 日期
                ("employee_id", "=", self.employee.id),     # 员工
                ("group", "=", check_position_settings_obj.id),     # 组别
                ("style_number_id", "=", self.order_number.id),     # 款号
                ("process_id", "=", work_work_obj.id)   # 工序号
            ])

            if automatic_process_comparison_objs:
                automatic_process_comparison_objs.manual_process_id = self.id
            else:

                automatic_process_comparison_objs.sudo().create({
                    "date": self.date1,      # 日期
                    "employee_id": self.employee.id,     # 员工
                    "group": check_position_settings_obj.id,    # 组别
                    "style_number_id": self.order_number.id,     # 款号
                    "process_id": work_work_obj.id,     # 工序号
                    "manual_process_id": self.id
                })




    @api.model
    def create(self, vals):


        instance = super(OnWork, self).create(vals)

        # 设置工序对比
        instance.sudo().set_process_comparison()

        return instance



class AutomaticSceneProcess(models.Model):
    """ 继承自动现场工序"""
    _inherit = "automatic_scene_process"


    # 设置工序对比
    def set_process_comparison(self):


        automatic_process_comparison_objs = self.env["automatic_process_comparison"].sudo().search([
            ("date", "=", self.date),
            ("employee_id", "=", self.employee_id.id),
            ("group", "=", self.group.id),
            ("style_number_id", "=", self.style_number_id.id),
            ("process_id", "=", self.process_id.id)
        ])
        if automatic_process_comparison_objs:
            automatic_process_comparison_objs.automatic_process_id = self.id
        else:

            automatic_process_comparison_objs.sudo().create({
                "date": self.date,
                "employee_id": self.employee_id.id,
                "group": self.group.id,
                "style_number_id": self.style_number_id.id,
                "process_id": self.process_id.id,
                "automatic_process_id": self.id
            })




    @api.model
    def create(self, vals):


        instance = super(AutomaticSceneProcess, self).create(vals)

        # 设置工序对比
        instance.sudo().set_process_comparison()

        return instance