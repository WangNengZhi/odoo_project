from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import calendar


class PersonnelAward(models.Model):
    _name = 'personnel_award'
    _description = '人事奖励记录'
    _rec_name = 'emp_id'
    _order = "entry_date desc"


    emp_id = fields.Many2one('hr.employee', string="员工", ondelete='cascade')
    job_id = fields.Many2one("hr.job", string="岗位", related="emp_id.job_id", store=True)
    entry_date = fields.Date(string="入职日期", related="emp_id.entry_time", store=True)

    resignation_date = fields.Date(string="离职日期", related="emp_id.is_delete_date", store=True)
    working_time = fields.Float(string="在职时长")
    lock_state = fields.Selection([('未审批', '未审批'), ('已审批', '已审批')], string="审批状态", default="未审批")
    introducer = fields.Many2one('hr.employee', string="介绍人", related="emp_id.introducer", store=True)
    satisfy_date = fields.Date(string="满在职30天日期", compute='set_satisfy_date', store=True)
    @api.depends('emp_id', 'emp_id.entry_time')
    def set_satisfy_date(self):
        for record in self:
            record.satisfy_date = record.emp_id.entry_time + timedelta(days=30)


    state = fields.Selection([('在职', '在职'), ('已离职', '已离职')], string="状态", default="在职", compute='set_resignation_state', store=True)

    during_month_award_money = fields.Float(string="当月奖励金额")
    during_month_count_month = fields.Char(string="当前月份")
    last_month_award_money = fields.Float(string="上月奖励金额")
    award_end_month = fields.Char(string="奖励截至月份")
    is_award = fields.Boolean(string="奖励已截至", default=False)

    def set_lock_state(self):
        ''' 设置审批状态'''

        for record in self:
            lock_state = self.env.context.get("lock_state")
            if lock_state == "已审批":
                record.sudo().lock_state = "已审批"
            elif lock_state == "未审批":
                record.sudo().lock_state = "未审批"

    personnel_award_line_ids = fields.One2many("personnel_award_line", "personnel_award_id", string="人事奖励明细", compute='set_personnel_award_line_ids', store=True)
    @api.depends('emp_id', 'entry_date', 'introducer')
    def set_personnel_award_line_ids(self):
        for record in self:
            record.personnel_award_line_ids.sudo().unlink()

            tem_year_month = {"year": record.satisfy_date.year, "month": record.satisfy_date.month}   # 临时月份

            count = 0

            while True:

                if record.introducer.department_id.name == "人事行政部":
                    if count >= 1:
                        break

                    # 查询是否已经存在该月份的记录了
                    obj = record.personnel_award_line_ids.sudo().search([
                        ("personnel_award_id", "=", record.id),
                        ("award_month", "=", f"{tem_year_month['year']}-{'%02d' % tem_year_month['month']}")
                    ])
                    if not obj:

                        record.personnel_award_line_ids.sudo().create({
                            "personnel_award_id": record.id,
                            "award_month": f"{tem_year_month['year']}-{'%02d' % tem_year_month['month']}"
                        })


                    count = count + 1
                    if tem_year_month["month"] == 12:
                        tem_year_month["year"] = tem_year_month["year"] + 1
                        tem_year_month["month"] = 1
                    else:
                        tem_year_month["month"] = tem_year_month["month"] + 1

                else:

                    if count >= 6:
                        break

                    obj = record.personnel_award_line_ids.sudo().search([
                        ("personnel_award_id", "=", record.id),
                        ("award_month", "=", f"{tem_year_month['year']}-{'%02d' % tem_year_month['month']}")
                    ])
                    if not obj:
                        record.personnel_award_line_ids.sudo().create({
                            "personnel_award_id": record.id,
                            "award_month": f"{tem_year_month['year']}-{'%02d' % tem_year_month['month']}"
                        })

                    count = count + 1
                    if tem_year_month["month"] == 12:
                        tem_year_month["year"] = tem_year_month["year"] + 1
                        tem_year_month["month"] = 1
                    else:
                        tem_year_month["month"] = tem_year_month["month"] + 1


    # 设置离职状态
    @api.depends('resignation_date')
    def set_resignation_state(self):
        for record in self:

            if record.resignation_date != False:
                record.state = "已离职"



    # 计算在职时长
    def action_get_working_time(self):

        # 查询离职日期为False的记录，并循环
        for record in self.search([("resignation_date", "=", False)]):

            # 判断是否有离职日期
            if record.emp_id.is_delete_date:
                resignation_date = record.emp_id.is_delete_date
                working_time = (resignation_date - record.entry_date).days

                record.sudo().write({
                    "resignation_date": resignation_date,
                    "working_time": working_time,
                })
            else:
                working_time = (fields.datetime.now().date() - record.entry_date).days

                record.sudo().write({
                    "working_time": working_time,
                })



    # 获取当月第一天和最后一天
    def set_begin_and_end(self, year, month):

        day = 1
        date_pinjie = year + '-' + month + '-' + str(day)

        #    这就是年月的算法，返回本月天数
        month_math = calendar.monthrange(int(year), int(month))[1]

        #  本月的最大时间
        date_end_of_the_month5 = year + '-' + str(month) + '-' + str(month_math)
        last_day = datetime.strptime(date_end_of_the_month5, '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)     # 当月最后一天

        first_day = datetime.strptime(date_pinjie, '%Y-%m-%d')      # 当月第一天

        return first_day, last_day



    # 计算奖励金额
    def action_calculate_award_money(self):

        for record in self.search([]):

            if record.introducer.department_id.name == "人事行政部":

                if record.working_time >= 30:

                    for personnel_award_line_obj in record.personnel_award_line_ids:
                        personnel_award_line_obj.award_money = 100

            else:

                for personnel_award_line_obj in record.personnel_award_line_ids:

                    year, month = personnel_award_line_obj.award_month.split('-')
                    first_day, last_day = self.set_begin_and_end(year, month)

                    # 查询计件工资
                    ji_jian_objs = self.env["dg_piece_rate"].sudo().search([
                        ("employee_id", "=", record.emp_id.id),
                        ("date", ">=", first_day),
                        ("date", "<=", last_day),
                    ])

                    personnel_award_line_obj.award_money = sum(i.cost for i in ji_jian_objs)




class PersonnelAwardLine(models.Model):
    _name = 'personnel_award_line'
    _description = '人事奖励明细'


    personnel_award_id = fields.Many2one("personnel_award", string="人事奖励", ondelete="cascade")
    award_month = fields.Char(string="奖励月份")
    award_money = fields.Float(string="奖励金额")

















