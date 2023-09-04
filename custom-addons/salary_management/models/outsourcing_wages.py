
import datetime
import calendar
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import itertools


def get_month_range(year, month):
    first_day = datetime.date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    last_day = datetime.date(year, month, last_day)
    return first_day, last_day


class OutsourcingWagesWizard(models.TransientModel):
    _name = 'outsourcing_wages_wizard'
    _description = '外包员工月工资计算向导'
    # _order = 'id asc'


    year_month = fields.Char(string="月份")
    start_date = fields.Date(string="开始日期", required=True)
    end_date = fields.Date(string="结束日期", required=True)
    employee_id = fields.Many2one('hr.employee', string='员工')
    contract = fields.Selection([('外包(计时)', '外包(计时)'), ('外包(计件)', '外包(计件)')], string='工种', required=True)
    


    def calculation_outsourcing_wages(self):

        if self.contract == "外包(计时)":
            raise ValidationError(f"此功能暂时无法使用！")
            # self.env['outsourcing_wages'].sudo().outsourcing_wages_per_work_time(self.start_date, self.end_date)

        elif self.contract == "外包(计件)":
            self.env['outsourcing_wages'].sudo().outsourcing_wages_for_work_done(self.start_date, self.end_date, self.employee_id)


        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




class AdvanceOfWages(models.Model):
    """ 继承预支工资记录"""
    _inherit = 'advance_of_wages'


    outsourcing_wages_ids = fields.Many2one("outsourcing_wages", string="外包员工月工资", ondelete='cascade')
    total_wages = fields.Float(string='应付工资', related='outsourcing_wages_ids.total_wages')



class OutsourcingWages(models.Model):
    _name = 'outsourcing_wages'
    _description = '外包员工月工资'
    _rec_name = "employee"


    
    employee = fields.Many2one('hr.employee', string='外包员工')
    id_card = fields.Char(string="身份证号", compute="set_id_card", store=True)
    @api.depends('employee')
    def set_id_card(self):
        for rec in self:
            rec.id_card = rec.employee.id_card  # 身份证号


    contract = fields.Selection([
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], string='工种', compute="set_contract", store=True)
    @api.depends('employee')
    def set_contract(self):
        for rec in self:
            rec.contract = rec.employee.is_it_a_temporary_worker  # 合同/工种

    outsourcing_type = fields.Selection([
        ('长期', '长期'),
        ('短期', '短期'),
    ], string="外包性质", compute="set_outsourcing_type", store=True)
    @api.depends('employee')
    def set_outsourcing_type(self):
        for record in self:
            record.outsourcing_type = record.employee.outsourcing_type


    fixed_salary = fields.Float(string='单位薪资', compute='set_fixed_salary', store=True)

    year = fields.Integer(string='年')
    month = fields.Integer(string='月')
    year_month = fields.Char(string='月份', compute="generate_year_month", store=True)
    start_date = fields.Date(string="开始日期", required=True)
    end_date = fields.Date(string="结束日期", required=True)


    deduct_money = fields.Float(string="扣款")

    month_workpiece_ratio = fields.Float(string="月平均效率(%)")

    total_wages = fields.Float(string='应付工资', compute="set_total_wages", store=True)

    work_hours = fields.Float(string='总工时')

    work_done = fields.Integer(string='总件数', compute="set_total_wages", store=True)

    work_done_details = fields.One2many("outsourcing_wages_line", "outsourcing_wages_id", string="外包(计件)数量明细")

    # 计算应付工资
    @api.depends('fixed_salary', 'work_hours', 'work_done', "deduct_money", "work_done_details", "work_done_details.number", "work_done_details.salary")
    def set_total_wages(self):
        for rec in self:
            if rec.contract == "外包(计时)":

                rec.total_wages = (rec.fixed_salary * rec.work_hours) - rec.deduct_money
            elif rec.contract == "外包(计件)":

                rec.work_done = sum(rec.work_done_details.mapped("number"))

                rec.total_wages = sum(rec.work_done_details.mapped("salary")) - rec.deduct_money
            

            rec.create_advance_of_wages()


    def create_advance_of_wages(self):
        ''' 同步创建预支工资记录'''
        for record in self:
            advance_of_wages_obj = self.env['advance_of_wages'].sudo().search([("outsourcing_wages_ids", "=", record.id)])
            if not advance_of_wages_obj:
                advance_of_wages_obj = self.env['advance_of_wages'].sudo().create({
                    "dDate": fields.Date.today(),
                    "employee_id": record.employee.id,
                    "wages_type": "薪酬",
                    "money": record.total_wages,
                    "outsourcing_wages_ids": record.id
                })

            advance_of_wages_obj.money = record.total_wages



    @api.depends('year', 'month')
    def generate_year_month(self):
        for rec in self:
            rec.year_month = f'{rec.year}-{rec.month:02d}'





    @api.depends('employee')
    def set_fixed_salary(self):
        for rec in self:
            if rec.employee.is_it_a_temporary_worker == "外包(计时)":

                rec.fixed_salary = rec.employee.fixed_salary / 11.5
            elif rec.employee.is_it_a_temporary_worker == "外包(计件)":

                tem_fixed_salary = 0

                for line_obj in rec.employee.epiboly_contract_line_ids:
                    tem_fixed_salary = tem_fixed_salary + line_obj.processing_cost

                rec.fixed_salary = tem_fixed_salary

            # else:

            #     rec.fixed_salary = rec.employee.fixed_salary  #


    def get_outsourcing_workers(self, year, month, contract):
        ''' 获取指定月在职的外包员工 '''
        first_day, last_day = get_month_range(year, month)
        return self.env["hr.employee"].sudo().search([
                    ('is_it_a_temporary_worker', '=', contract),
                    ('entry_time', '<=', last_day),
                    '|', ('is_delete','=',False),
                         ('is_delete_date', '>=', first_day),
                ])


    def outsourcing_wages_per_work_time(self, year, month):
        ''' 计算指定月份的外包计时员工的工资 '''
        # print('*'*40, 'outsourcing_wages_per_work_time')

        first_day, last_day = get_month_range(year, month)

        emps = self.get_outsourcing_workers(year, month, '外包(计时)')
        emp_stats = {e.id : 0 for e in emps}

        redo = self.env['repair_clock_in_line'].sudo().search([  # 补卡申请单
                            ('line_date', '>=', first_day),
                            ('line_date', '<=', last_day),
                        ], order='employee_id, line_date')  # !
        redo_set = {(x.employee_id.id, x.line_date, x.repair_clock_type) for x in redo}
        # print(redo_set)

        working_days = self.env['punch.in.record'].sudo().search([  # 打卡机记录
                            ('date', '>=', first_day),
                            ('date', '<=', last_day),
                        ])

        for d in working_days:
            emp_id = d.employee.id
            if emp_id not in emp_stats:
                continue

            first_punch, last_punch = d.check_sign.split()
            # print((first_punch, last_punch))

            if first_punch == '--:--':
                if (emp_id, d.date, '上班卡') not in redo_set:
                    continue
                first_punch = '08:00'
            elif last_punch == '--:--':
                if (emp_id, d.date, '下班卡') not in redo_set:
                    continue
                last_punch = '21:00'

            if first_punch < '08:00':
                first_punch = '08:00'

            begin_hour, begin_min = map(int, first_punch.split(':'))
            end_hour, end_min = map(int, last_punch.split(':'))
            # print((begin_hour, begin_min), (end_hour, end_min))

            hours = (60*end_hour+end_min - (60*begin_hour+begin_min)) / 60
            emp_stats[emp_id] += hours

        for i, x in enumerate(redo):
            if not i:
                continue
            # print('here!')
            emp_id = x.employee_id.id
            prev = redo[i-1]
            if (prev.employee_id.id, prev.line_date) == (emp_id, x.line_date):
                # print(x.employee_id.name, x.line_date)
                if emp_id in emp_stats:
                    emp_stats[emp_id] += 21 - 8

        # print('*'*40, emp_stats)

        for e in emps:
            work_hours = emp_stats[e.id]
            total_wages = work_hours * e.fixed_salary
            self.sudo().create(dict(
                employee = e.id,
                year = year,
                month = month,
                work_hours = work_hours,
                total_wages = total_wages
            ))


    def outsourcing_wages_for_work_done(self, first_day, last_day, emp):
        ''' 计算指定月份的外包计件员工的工资 '''

        outsourcing_wages_obj = self.sudo().create(dict(employee=emp.id, year=first_day.year, month=first_day.month, start_date=first_day, end_date=last_day))

        on_work_objs = self.env['on.work'].sudo().search([('date1', '>=', first_day), ('date1', '<=', last_day), ("employee", "=", emp.id)])


        if emp.outsourcing_type == "长期":

            on_work_objs = on_work_objs.sorted(key=lambda x: (x.process_abbreviation, x.order_number.id, x.employee_id), reverse=False)

            for (process_abbreviation, order_number_id, employee_id), objs in itertools.groupby(on_work_objs, key=lambda x: (x.process_abbreviation, x.order_number.id, x.employee_id)):

                objs = list(objs)

                epiboly_contract_line_obj = self.env['epiboly_contract_line'].sudo().search([("hr_employee_id", "=", emp.id), ("process_name", "=", process_abbreviation.strip())])
                
                if epiboly_contract_line_obj:
                    outsourcing_wages_obj.work_done_details.sudo().create({
                        "outsourcing_wages_id": outsourcing_wages_obj.id,
                        "process_name": process_abbreviation,
                        "style_number": order_number_id,  # 款号
                        "process_number": employee_id,     # 工序
                        "unit_price": epiboly_contract_line_obj.processing_cost,    # 工价
                        "number": sum(i.over_number for i in objs)  # 件数
                    })
                else:
                    raise ValidationError(f"员工{emp.name}的外包明细信息中没有查询到工序描述为:{process_abbreviation}的记录！")

        elif emp.outsourcing_type == "短期":
    
            on_work_objs = on_work_objs.sorted(key=lambda x: (x.order_number.id, x.employee_id), reverse=False)

            for (style_number_id, procedure_number), objs in itertools.groupby(on_work_objs, key=lambda x:(x.order_number.id, x.employee_id)):

                epiboly_contract_line_obj = emp.epiboly_contract_line_ids.sudo().search([
                    ("style_number", "=", style_number_id),
                    ("process_number", "=", procedure_number),
                    ("hr_employee_id", "=", emp.id)
                ])
                
                if epiboly_contract_line_obj:
                    outsourcing_wages_obj.work_done_details.sudo().create({
                        "outsourcing_wages_id": outsourcing_wages_obj.id,
                        "style_number": style_number_id,  # 款号
                        "process_number": procedure_number,     # 工序
                        "unit_price": epiboly_contract_line_obj.processing_cost,    # 工价
                        "number": sum(i.over_number for i in objs)  # 件数
                    })
                else:
                    raise ValidationError(f"员工{emp.name}的外包明细信息中没有查询到款号:{self.env['ib.detail'].sudo().browse(style_number_id).style_number}工序号：{procedure_number}的记录！")
        else:
            raise ValidationError(f"员工{emp.name}未设置外包类型！")






    # 计算月的第一天和最后一天
    def compute_start_and_end(self, date_year, date_month):

        last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
        start = datetime.date(date_year, date_month, 1)
        end = datetime.date(date_year, date_month, last_day)

        return {"start": start, "end": end}



    # 计算月平均效率
    def set_month_workpiece_ratio(self, first_day, last_day):

        eff_eff_objs = self.env["eff.eff"].sudo().search([
            ("date", ">=", first_day),
            ("date", "<=", last_day),
            ("employee", "=", self.employee.id)
        ])

        if eff_eff_objs:

            overall_efficiency = 0

            for eff_eff_obj in eff_eff_objs:
                overall_efficiency = overall_efficiency + eff_eff_obj.totle_eff

            month_workpiece_ratio = overall_efficiency / len(eff_eff_objs)

        else:

            month_workpiece_ratio = 0

        return month_workpiece_ratio


    # 计算扣款
    def set_deduct_money(self, first_day, last_day):

        if last_day:
            # 查询扣款
            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                ("declare_time", ">=", first_day),    # 申报时间大于等于当月第一天
                ("declare_time", "<=", last_day),      # 申报时间小于等于当月最后一天
                ("emp_id", "=", self.employee.id),   # 员工id
            ])
        else:
            # 查询扣款
            reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
                ("declare_time", ">=", first_day),    # 申报时间大于等于当月第一天
                ("emp_id", "=", self.employee.id),   # 员工id
            ])

        tem_deduct_money = 0
        for reward_punish_record_obj in reward_punish_record_objs:
            tem_deduct_money = tem_deduct_money + reward_punish_record_obj.money_amount

        return tem_deduct_money

    @api.model
    def create(self, vals):


        rec = super(OutsourcingWages, self).create(vals)

        # 获取当月第一天和最后一天
        this_month = rec.compute_start_and_end(rec.year, rec.month)

        # 判断离职时间是否为公司结算月份
        if rec.employee.is_delete_date and rec.employee.is_delete_date.year == rec.year and rec.employee.is_delete_date.month == rec.month:
            # 计算扣款
            rec.deduct_money = rec.set_deduct_money(this_month["start"], this_month["end"])
        else:
            # 计算扣款
            rec.deduct_money = rec.set_deduct_money(this_month["start"], False)

        # 计算效率
        rec.month_workpiece_ratio = rec.set_month_workpiece_ratio(this_month["start"], this_month["end"])



        return rec


    def unlink(self):
        for record in self:
            advance_of_wages_obj = self.env['advance_of_wages'].sudo().search([
                ("outsourcing_wages_ids", "=", record.id),
                ("approve_state", "=", "已审批"),
            ])
            if advance_of_wages_obj:
                raise ValidationError("存在已经审批的预支工资记录，不可删除!")
            
        res = super(OutsourcingWages, self).unlink()
        return res






class OutsourcingWagesLine(models.Model):
    _name = 'outsourcing_wages_line'
    _description = '外包员工计件工资明细'


    outsourcing_wages_id = fields.Many2one("outsourcing_wages", ondelete="cascade")
    style_number = fields.Many2one('ib.detail', string='款号')
    process_number = fields.Char(string="工序号")
    process_name = fields.Char(string="工序描述")
    unit_price = fields.Float(string="工价")
    number = fields.Float(string="件数")
    salary = fields.Float(string="工资", compute="set_total_wages", store=True)

    application_price = fields.Float(string="申请价格", compute="set_application_info", store=True)
    application_number = fields.Float(string="申请件数", compute="set_application_info", store=True)
    @api.depends('outsourcing_wages_id.outsourcing_type', 'style_number', 'process_number', 'process_name')
    def set_application_info(self):
        for record in self:
            if record.outsourcing_wages_id.outsourcing_type == "长期":
                record.application_price = self.env['long_term_temp_rate'].sudo().search([("process_name", "=", record.process_name)]).processing_cost
                record.application_number = 0
            elif record.outsourcing_wages_id.outsourcing_type == "短期":
                temporary_workers_apply_obj = self.env["temporary_workers_apply"].sudo().search([
                    ("style_number", "=", record.style_number.id),
                    ("process_no", "=", record.process_number)
                ], limit=1)
                record.application_price = temporary_workers_apply_obj.apply_price
                record.application_number = temporary_workers_apply_obj.number
            else:
                record.application_price = 0
                record.application_number = 0
 



    # 计算工资
    @api.depends('style_number', 'unit_price', 'number')
    def set_total_wages(self):
        for rec in self:
            rec.salary = rec.unit_price * rec.number


