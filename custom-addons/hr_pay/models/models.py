from datetime import datetime, timedelta
import time

from odoo import models, fields, api
from odoo.exceptions import ValidationError


def which_week(date):
    year_count = date.isocalendar()[0]
    week_count = date.isocalendar()[1]
    return week_count, year_count


class every_detail(models.Model):
    _name = 'every.detail'
    _description = '请假表'
    _rec_name = 'leave_officer'
    _order = "date desc"

    date = fields.Datetime(string='开始日期', required=True)
    end_date = fields.Datetime(string='结束日期', required=True)
    department_id = fields.Char(string='部门', related='leave_officer.department_id.complete_name')
    leave_officer = fields.Many2one('hr.employee', string='请假人员', required=True)
    reason_for_leave = fields.Char(string='请假事由(旧，等删)')
    reason_for_leave2 = fields.Selection([
        ('事假', '事假'),
        ('病假', '病假'),
    ], string='请假事由', required=True)
    days = fields.Float(string='请假时间（小时/h)', required=True)
    fsn_days = fields.Float(string='请假天数')
    are_there_any_leave_slips = fields.Boolean('有无请假条')
    comment = fields.Char('备注')



    # 刷新员工请假状态
    def refresh_emp_status(self):

        emp_objs = self.env['hr.employee'].sudo().search([("is_delete", "=", False)])

        now_time = fields.Datetime.now()
        
        for emp_obj in emp_objs:

            if emp_obj.status == "正常":

                every_detail_objs = self.env['every.detail'].sudo().search([('leave_officer', '=', emp_obj.id), ('date', '<=', now_time), ('end_date', '>=', now_time)])
                if every_detail_objs:
                    if all(i.are_there_any_leave_slips for i in every_detail_objs):
                        emp_obj.status = "请假"
                    else:
                        emp_obj.status = "旷工"

            else:

                if not self.env['every.detail'].sudo().search([('leave_officer', '=', emp_obj.id), ('date', '>=', now_time), ('end_date', '>=', now_time)]):
                    emp_obj.status = "正常"




    @api.constrains('date', 'end_date', 'leave_officer')
    def _check_date(self):
        if self.date > self.end_date:
            raise ValidationError("开始时间不能大于结束时间！")

        data = self.sudo().search([
                    ('leave_officer', '=', self.leave_officer.id),
                    '|',
                        '&',
                            ('date', '>=', self.date),
                            ('date', '<' , self.end_date),
                        '&',
                            ('end_date', '>', self.date),
                            ('end_date', '<=', self.end_date),
                ])
        if len(data) > 1:
            raise ValidationError("同一时间段同一个人不能有两个请假条！")

        def processing_time(date):
            t = str(date).split('-')
            t2 = str(t[0]) + '-' + str(t[1])
            return t2

        begin_date = processing_time(self.date)
        end_date_year = processing_time(self.end_date)
        if begin_date != end_date_year:
            raise ValidationError('不能跨月请假，请分开请假！')


    def binding_every_totle_record(self):
        for record in self:
            if record.date or record.end_date:
                every_totle_objs = self.env['every.totle'].sudo().search([("date", ">=", record.date), ("date", "<=", record.end_date)])
                every_totle_objs.binding_leave_record()


    @api.model
    def create(self, vals):

        instance = super(every_detail, self).create(vals)
        
        instance.binding_every_totle_record()

        return instance


    def write(self, vals):

        res = super(every_detail, self).write(vals)

        self.binding_every_totle_record()

        return res



    def unlink(self):

        res = super(every_detail, self).unlink()

        return res





# 员工每日出勤统计表
class every_totle(models.Model):
    _name = 'every.totle'
    _description = '员工每日出勤统计表'
    _rec_name = 'date'
    _order = "date desc"

    every_detail_ids = fields.Many2many("every.detail", string="请假表")
    date = fields.Date(string='日期')

    all_emp_ids = fields.Many2many("hr.employee", string="全部员工")
    number_of_attendees = fields.Integer(string='应出勤人数', compute="set_number_of_attendees", store=True)
    @api.depends("all_emp_ids", "all_emp_ids.entry_time", "all_emp_ids.is_delete_date", "all_emp_ids.is_delete")
    def set_number_of_attendees(self):
        for record in self:
            if record.all_emp_ids:
                record.number_of_attendees = len(record.all_emp_ids.filtered(lambda x: x.entry_time and x.entry_time <= record.date and (not x.is_delete or x.is_delete_date > record.date)))
            
    number_of_resignations = fields.Integer(string='辞职人数', compute="set_number_of_resignations", store=True)
    @api.depends("all_emp_ids", "all_emp_ids.is_delete_date")
    def set_number_of_resignations(self):
        for record in self:
            if record.all_emp_ids:
                record.number_of_resignations = len(record.all_emp_ids.filtered(lambda x: x.is_delete_date == record.date))
    
    actual_attendance = fields.Integer(string='实出勤人数', compute="set_actual_attendance", store=True)
    # 设置实出勤人数
    @api.depends("number_of_attendees", "number_of_workers", "number_of_leave")
    def set_actual_attendance(self):
        for record in self:
            record.actual_attendance = record.number_of_attendees - (record.number_of_workers + record.number_of_leave)


    number_of_workers = fields.Integer(string='旷工人数', compute="set_number_of_workers", store=True)
    # 设置旷工人数
    @api.depends("every_detail_ids", "every_detail_ids.are_there_any_leave_slips")
    def set_number_of_workers(self):
        for record in self:
            record.number_of_workers = len([i for i in record.every_detail_ids if not i.are_there_any_leave_slips])



    number_of_leave = fields.Integer(string='请假人数', compute="set_number_of_leave", store=True)
    # 设置请假人数
    @api.depends("every_detail_ids", "every_detail_ids.are_there_any_leave_slips")
    def set_number_of_leave(self):
        for record in self:
            record.number_of_leave = len([i for i in record.every_detail_ids if i.are_there_any_leave_slips])


    def binding_leave_record(self):
        for record in self:
            every_detail_objs = self.env['every.detail'].sudo().search([("date", "<=", record.date), ("end_date", ">=", record.date)])
            record.every_detail_ids = [(6, 0, every_detail_objs.ids)]


    def refresh_every_totle(self, present_date):

        every_totle_obj = self.env['every.totle'].sudo().search([("date", "=", present_date)])

        # 获取全部员工
        all_emp_objs = self.env['hr.employee'].sudo().search([])

        if not every_totle_obj:
            every_totle_obj = self.env['every.totle'].sudo().create({"date": present_date})

        every_totle_obj.all_emp_ids = [(6, 0, all_emp_objs.ids)]
        
        every_totle_obj.binding_leave_record()














class online(models.Model):
    _name = 'online.attendance'
    _description = '工时考勤'
    _rec_name = 'name'
    _order = "date desc"

    date = fields.Date('日期')
    name = fields.Char('员工')
    whether_to_be_absent = fields.Boolean('是否缺勤')

    @api.model
    def kaoqin(self):
        # 遍历所有的用户啥职位 如果是未辞职的计件和临时工
        demo = self.env['hr.employee'].sudo().search([('is_delete', '=', False)])
        for i in demo:
            if i.is_it_a_temporary_worker == '正式工(计件工资)' or i.is_it_a_temporary_worker == '临时工':
                date = datetime.datetime.now() + datetime.timedelta(hours=8) - datetime.timedelta(days=2)
                name = i.name
                # 现场工序
                demo1 = self.env['on.work'].sudo().search([('date1', '=', date), ('employee.name', '=', name)])
                # 考勤表
                demo2 = self.env['every.detail'].sudo().search([('date', '=', date), ('display_name', '=', name)])
                if demo1 or demo2:
                    pass
                else:
                    self.env['online.attendance'].sudo().create({
                        'date': date,
                        'name': name,
                        'whether_to_be_absent': True
                    })



class group_attendance(models.Model):
    _name = 'group.attendance'
    _description = '组上考勤'
    _rec_name = 'staff'
    _order = "date desc"

    date = fields.Date('日期')
    group = fields.Char('组别')
    staff = fields.Many2one('hr.employee', string='员工')
    group_leader = fields.Many2one('hr.employee', string='组长')


class attendance_days_statistics_day(models.Model):
    _name = 'attendance.days.statistics.day'
    _description = '出勤天数统计表(精确到天)'

    date = fields.Date('日期')
    week = fields.Char('周')
    name = fields.Char('姓名')
    actual_attendance = fields.Integer('实出勤天数')
    number_of_workers = fields.Integer('旷工天数')
    number_of_leave = fields.Integer('请假天数')
    days_out = fields.Integer('外出天数')
    # comment = fields.Text(string='备注，防止薪酬管理没有数据，导致这边无法插入数据')
    @api.model
    def create(self, val):
        demo = self.env['attendance.days.statistics.day'].sudo().search([('date', '=', val['date']), ('name', '=', val['name'])])
        if demo:
            demo.sudo().unlink()

        # #  处理薪酬管理的数据       todo
        # #     处理时间成1990-10
        # date3 = val['date']
        # date4 = date3.split('-')[0]
        # date5 = date3.split('-')[1]
        # date_totle = date4 + '-' + date5

        return super(attendance_days_statistics_day, self).create(val)

    @api.model
    def attendance_days(self):
        """    这个是所有工种的情况  """
        #     不考虑日期元素
        demo_employee = self.env['hr.employee'].sudo().search([])
        #     前两天的，以防工时工序没有数据
        date_object = datetime.datetime.now() + datetime.timedelta(hours=8) - datetime.timedelta(days=2)
        # week      todo
        week_count, year = which_week(date_object)
        week_count = '%s-%s' % (date_object.year, week_count)

        for record in demo_employee:
            if record.is_it_a_temporary_worker == '正式工(计件工资)' or record.is_it_a_temporary_worker == '临时工':
                #       组上和工时
                demo_gongshi = self.env['on.work'].sudo().search([('employee', '=', record.name), ('date1', '=', date_object)])
                demo_zushang = self.env['group.attendance'].sudo().search([('staff', '=', record.name), ('date', '=', date_object)])
                #       本表数据
                demo_jingquetian = self.env['attendance.days.statistics.day'].sudo().search([('date', '=', date_object)])
                if len(demo_gongshi) and len(demo_zushang) == False:
                    # 组上      工时有   正常考勤 +1        第一种可能
                    # every.detail   请假表
                    demo_every_detail = self.env['every.detail'].sudo().search([('leave_officer', '=', record.name)])
                    #  外出单
                    demo_leave_form = self.env['leave.form'].sudo().search([('name', '=', record.name)])
                    # demo_actual_attendance = self.env['attendance.days.statistics.table'].sudo().search([('name', '=', record.name), ('date', '=', date_object)])
                    if len(demo_every_detail):
                        for every_detail_record in demo_every_detail:
                            date_begin = every_detail_record.date
                            dete_end = every_detail_record.end_date
                            if dete_end:
                                if date_begin < date_object < dete_end:
                                    status = every_detail_record.are_there_any_leave_slips
                                    if status:
                                        # 请假  +1
                                        self.env['attendance.days.statistics.day'].sudo().create({
                                            'date': date_object,
                                            'week': week_count,
                                            'name': record.name,
                                            'number_of_leave': 1,
                                            'number_of_workers': 0,
                                            'days_out': 0,
                                            'actual_attendance': 0,
                                        })
                                    else:
                                        #  旷工  +1
                                        self.env['attendance.days.statistics.day'].sudo().create({
                                            'date': date_object,
                                            'week': week_count,
                                            'name': record.name,
                                            'number_of_leave': 0,
                                            'number_of_workers': 1,
                                            'days_out': 0,
                                            'actual_attendance': 0,
                                        })
                    elif len(demo_leave_form):
                        #        外出+1
                        for leave_form_record in demo_leave_form:
                            date_begin = leave_form_record.time_out
                            dete_end = leave_form_record.time_end
                            if date_begin < date_object < dete_end:
                                #  外出+1
                                self.env['attendance.days.statistics.day'].sudo().create({
                                    'date': date_object,
                                    'week': week_count,
                                    'name': record.name,
                                    'number_of_leave': 0,
                                    'number_of_workers': 0,
                                    'days_out': 1,
                                    'actual_attendance': 0,
                                })
                    else:
                        self.env['attendance.days.statistics.day'].sudo().create({
                            'date': date_object,
                            'week': week_count,
                            'name': record.name,
                            'number_of_leave': 0,
                            'number_of_workers': 0,
                            'days_out': 0,
                            'actual_attendance': 1,
                        })
                else:
                    # 组上      工时有   正常考勤 +1        第2种可能

                    demo_every_detail = self.env['every.detail'].sudo().search([('leave_officer', '=', record.name)])
                    #  外出单
                    demo_leave_form = self.env['leave.form'].sudo().search([('name', '=', record.name)])
                    # demo_actual_attendance = self.env['attendance.days.statistics.table'].sudo().search([('name', '=', record.name), ('date', '=', date_object)])
                    if len(demo_every_detail):
                        for every_detail_record in demo_every_detail:
                            date_begin = every_detail_record.date
                            dete_end = every_detail_record.end_date
                            if dete_end:
                                if date_begin < date_object < dete_end:
                                    status = every_detail_record.are_there_any_leave_slips
                                    if status:
                                        # 请假  +1
                                        self.env['attendance.days.statistics.day'].sudo().create({
                                            'date': date_object,
                                            'week': week_count,
                                            'name': record.name,
                                            'number_of_leave': 1,
                                            'number_of_workers': 0,
                                            'days_out': 0,
                                            'actual_attendance': 0,
                                        })
                                    else:
                                        #  旷工  +1
                                        self.env['attendance.days.statistics.day'].sudo().create({
                                            'date': date_object,
                                            'week': week_count,
                                            'name': record.name,
                                            'number_of_leave': 0,
                                            'number_of_workers': 1,
                                            'days_out': 0,
                                            'actual_attendance': 0,
                                        })
                    elif len(demo_leave_form):
                        #        外出+1
                        for leave_form_record in demo_leave_form:
                            date_begin = leave_form_record.time_out
                            dete_end = leave_form_record.time_end
                            if date_begin < date_object < dete_end:
                                #  外出+1
                                self.env['attendance.days.statistics.day'].sudo().create({
                                    'date': date_object,
                                    'week': week_count,
                                    'name': record.name,
                                    'number_of_leave': 0,
                                    'number_of_workers': 0,
                                    'days_out': 1,
                                    'actual_attendance': 0,
                                })
                    else:
                        self.env['attendance.days.statistics.day'].sudo().create({
                            'date': date_object,
                            'week': week_count,
                            'name': record.name,
                            'number_of_leave': 0,
                            'number_of_workers': 1,
                            'days_out': 0,
                            'actual_attendance': 0,
                        })

            else:
            #   打卡机的数据
                self.env['punch.in.record'].sudo().search([('date', '=', date_object), ('name', '=', self.name)])
                #      姓名和日期去查打卡机的数据
                demo_daka = self.env['punch.in.record'].sudo().search([('employee', '=', record.name), ('date', '=', date_object)])
                #      判断打卡机的记录是不是存在，如果不存在的话，就看一下请假单和外出单，没有的话就是旷工，存在的话，就算实出勤

                # every.detail   请假表
                demo_every_detail = self.env['every.detail'].sudo().search([('leave_officer', '=', record.name)])
                #  外出单
                demo_leave_form = self.env['leave.form'].sudo().search([('name', '=', record.name)])
                if demo_daka != "--:-- --:--" and demo_daka:
                    self.env['attendance.days.statistics.day'].sudo().create({
                        'date': date_object,
                        'week': week_count,
                        'name': record.name,
                        'number_of_leave': 0,
                        'number_of_workers': 0,
                        'days_out': 0,
                        'actual_attendance': 1,
                    })
                else:
                    if demo_every_detail:
                        self.env['attendance.days.statistics.day'].sudo().create({
                            'date': date_object,
                            'week': week_count,
                            'name': record.name,
                            'number_of_leave': 1,
                            'number_of_workers': 0,
                            'days_out': 0,
                            'actual_attendance': 0,
                        })
                    elif demo_leave_form:
                        self.env['attendance.days.statistics.day'].sudo().create({
                            'date': date_object,
                            'week': week_count,
                            'name': record.name,
                            'number_of_leave': 0,
                            'number_of_workers': 0,
                            'days_out': 1,
                            'actual_attendance': 0,
                        })
                    else:
                        self.env['attendance.days.statistics.day'].sudo().create({
                            'date': date_object,
                            'week': week_count,
                            'name': record.name,
                            'number_of_leave': 0,
                            'number_of_workers': 1,
                            'days_out': 0,
                            'actual_attendance': 0,
                        })



class attendance_days_statistics_table(models.Model):
    _name = 'attendance.days.statistics.table'
    _description = '出勤天数统计表'

    date = fields.Char('日期(周)')
    name = fields.Char('姓名')
    actual_attendance = fields.Integer('实出勤天数')
    number_of_workers = fields.Integer('旷工天数')
    number_of_leave = fields.Integer('请假天数')
    days_out = fields.Integer('外出天数')



    def test(self):
        date_object = datetime.datetime.now() + datetime.timedelta(hours=8)
        #  year
        # week
        week_count, year = which_week(date_object)
        #                todo
        old_week_count = week_count - 1
        old_week_count = str(year) + '-' + str(old_week_count)
        demo_old_attend = self.env['attendance.days.statistics.day'].sudo().search([('week', '=', old_week_count)])
        #      哪些员工
        record_employee_list = []
        for record_employee in demo_old_attend:
            record_employee_list.append(record_employee.name)
        #      去重员工
        for record_set_employee in set(record_employee_list):
            demo_zhu_attend = self.env['attendance.days.statistics.table'].sudo().search([('date', '=', old_week_count), ('name', '=', record_set_employee)])
            if demo_zhu_attend:
                demo_set_status_list = self.env['attendance.days.statistics.day'].sudo().search(
                    [('week', '=', old_week_count), ('name', '=', record_set_employee)])
                actual_attendance_list = []
                number_of_workers_list = []
                number_of_leave_list = []
                days_out_list = []
                for demo_set_status in demo_set_status_list:
                    actual_attendance_list.append(demo_set_status.actual_attendance)
                    number_of_workers_list.append(demo_set_status.number_of_workers)
                    number_of_leave_list.append(demo_set_status.number_of_leave)
                    days_out_list.append(demo_set_status.days_out)
                demo_zhu_attend.sudo().write({
                    'date': old_week_count,
                    'name': record_set_employee,
                    'actual_attendance': sum(actual_attendance_list),
                    'number_of_workers': sum(number_of_workers_list),
                    'number_of_leave': sum(number_of_leave_list),
                    'days_out': sum(days_out_list)
                })
            else:
                demo_set_status_list = self.env['attendance.days.statistics.day'].sudo().search([('week', '=', old_week_count), ('name', '=', record_set_employee)])
                actual_attendance_list = []
                number_of_workers_list = []
                number_of_leave_list = []
                days_out_list = []
                for demo_set_status in demo_set_status_list:
                    actual_attendance_list.append(demo_set_status.actual_attendance)
                    number_of_workers_list.append(demo_set_status.number_of_workers)
                    number_of_leave_list.append(demo_set_status.number_of_leave)
                    days_out_list.append(demo_set_status.days_out)
                self.env['attendance.days.statistics.table'].sudo().create({
                    'date': old_week_count,
                    'name': record_set_employee,
                    'actual_attendance': sum(actual_attendance_list),
                    'number_of_workers': sum(number_of_workers_list),
                    'number_of_leave': sum(number_of_leave_list),
                    'days_out': sum(days_out_list)
                })

class no_attendance(models.Model):
    
    _name = 'no_attendance_record'
    _description = '每日缺勤统计表'
    _order = 'date desc'

    date = fields.Date(string='日期')
    employee = fields.Many2one('hr.employee', string='员工')
    department_id = fields.Many2one('hr.department', string='部门', related='employee.department_id', store=True)
    check_sign_time = fields.Char(string='出勤时间')
    


    def get_no_attendance(self, today):
        names = self.env['hr.employee'].sudo().search([('is_delete', '=', False)])
        for name in names :
            no_attend_name = self.env['punch.in.record'].sudo().search([('employee.name', '=', name.name), ('date', '=', today - timedelta(days=1))])
            if not no_attend_name:
                data = {
                'date': today - timedelta(days=1),
                'employee': name.id,
                'check_sign_time' : '无',
                
                }
                #print(data)
                self.sudo().create(data)
            else:
                real_time_list = no_attend_name.check_sign.split(' ')
                if real_time_list[0] == "--:--" and not real_time_list[1] == "--:--":
                    data1 = {
                        'date': today - timedelta(days=1),
                        'employee': name.id,
                        'check_sign_time' : '无' + ' ' + ';' + real_time_list[1],
                
                        }
                    #print(data1)
                    self.sudo().create(data1)
                elif real_time_list[0] != "--:--" and  real_time_list[1] == "--:--":
                    data2 = {
                        'date': today - timedelta(days=1),
                        'employee': name.id,
                        'check_sign_time' : real_time_list[0]  + ';' + ' ' + '无',
                
                        }
                    #print(data1)
                    self.sudo().create(data2)

                


class punch_in_record(models.Model):
    _name = 'punch.in.record'
    _description = '打卡机记录'
    _order = 'date desc'

    date = fields.Date(string='日期')
    employee = fields.Many2one('hr.employee', string='员工')
    department_id = fields.Many2one('hr.department', string='部门', related='employee.department_id', store=True)
    job_id = fields.Many2one("hr.job", string="岗位", related='employee.job_id', store=True)

    check_sign = fields.Char(string='出勤时间')
    come_to_work_id = fields.Many2one('come.to.work', string='迟到早退的刷新id')



    @api.constrains('date', "employee")
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([('date', '=', self.date), ("employee", "=", self.employee.id)])
        if len(demo) > 1:
            raise ValidationError(f"我是不是和你说过不让你多次点击!")


    # 迟到早退刷新
    def come_to_work_refresh(self):

        for record in self:

            # 获取部门id
            department_id = record.employee.department_id.id
            # 获取员工的休息类型(单休还是双休或者大小休息)
            # rest_type = self.employee.time_plan.split(' ')[-1]

            # ['07:45', '20:01']
            real_time_list = record.check_sign.split(' ')

            if real_time_list[0] == "--:--":
                go_to_work_time = False
            else:
                # 上班时间
                go_to_work_time = str(record.date) + " " + real_time_list[0] + ":00"
                go_to_work_time = datetime.datetime.strptime(go_to_work_time, "%Y-%m-%d %H:%M:%S")

            if real_time_list[1] == "--:--":
                time_from_work = False
            else:
                # 下班时间
                time_from_work = str(record.date) + " " + real_time_list[1] + ":00"
                time_from_work = datetime.datetime.strptime(time_from_work, "%Y-%m-%d %H:%M:%S")


            if record.employee.time_plan:


                # 查询日历有没有特殊的考勤数据
                custom_calendar_obj = self.env["custom.calendar"].sudo().search([
                    ("date", "=", record.date),
                ])

                if custom_calendar_obj:
                    # 查询日历明细记录
                    custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([
                        ("custom_calendar_id", "=", custom_calendar_obj.id),    # 日历id
                        ("department", "=", department_id)   # 部门id
                        ])


                    # 设置默认备注
                    comment = ""

                    # 如果有特殊的上班和下班时间
                    if custom_calendar_line_obj.down_time and custom_calendar_line_obj.up_time:
                        # 特殊考勤上班时间
                        special_go_to_work_time = custom_calendar_line_obj.up_time + datetime.timedelta(hours=8)
                        # 特殊考勤下班时间
                        special_time_from_work = custom_calendar_line_obj.down_time + datetime.timedelta(hours=8)

                        # 如果上班没打卡
                        if go_to_work_time == False:
                            comment = "上班没打卡"
                            late_time = 0
                        else:
                            if record.date == record.employee.entry_time:
                                comment = "入职第一天不计迟到时间！"
                                late_time = 0
                            else:
                                # 如果上班打卡时间 > 特殊考勤的上班时间r
                                if go_to_work_time > special_go_to_work_time:
                                    # 迟到时间(分钟) = (上班打卡时间 - 特殊考勤的上班时间)
                                    late_time = ((go_to_work_time - special_go_to_work_time).seconds) / 60
                                else:
                                    late_time = 0


                        # 如果下班没打卡
                        if time_from_work == False:
                            comment = "下班没打卡"
                            leave_early = 0
                        else:
                            # 如果下班打卡时间 < 特殊考勤的下班时间
                            if time_from_work < special_time_from_work:
                                # 早退时间(分钟) = (下班打卡时间 - 特殊考勤的上班时间)
                                leave_early = ((special_time_from_work - time_from_work).seconds) / 60
                            else:
                                leave_early = 0


                    # 如果特殊考勤没有当前日期的记录
                    else:
                        # 9:00 - 18:00, 单休
                        tem_str = record.employee.time_plan.split(',')[0]
                        tem_list = tem_str.split(' ')
                        # 正常上班时间
                        normal_go_to_work_time = str(record.date) + " " + tem_list[0] + ":00"
                        normal_go_to_work_time = datetime.datetime.strptime(normal_go_to_work_time, "%Y-%m-%d %H:%M:%S")
                        # 正常下班时间
                        normal_time_from_work = str(record.date) + " " + tem_list[-1] + ":00"
                        normal_time_from_work = datetime.datetime.strptime(normal_time_from_work, "%Y-%m-%d %H:%M:%S")

                        # 如果上班没打卡
                        if go_to_work_time == False:
                            comment = "上班没打卡"
                            late_time = 0
                        else:
                            if record.date == record.employee.entry_time:
                                comment = "入职第一天不计迟到时间！"
                                late_time = 0
                            else:
                                # 如果上班打卡时间 > 正常考勤的上班时间r
                                if go_to_work_time > normal_go_to_work_time:
                                    # 迟到时间(分钟) = (上班打卡时间 - 正常考勤的上班时间)
                                    late_time = ((go_to_work_time - normal_go_to_work_time).seconds) / 60
                                else:
                                    late_time = 0

                        # 如果下班没打卡
                        if time_from_work == False:
                            comment = "下班没打卡"
                            leave_early = 0
                        else:
                            # 如果下班打卡时间 < 正常考勤的下班时间
                            if time_from_work < normal_time_from_work:
                                # 早退时间(分钟) = (下班打卡时间 - 正常考勤的上班时间)
                                leave_early = ((normal_time_from_work - time_from_work).seconds) / 60
                            else:
                                leave_early = 0


                else:
                    # 9:00 - 18:00, 单休
                    tem_str = record.employee.time_plan.split(',')[0]
                    tem_list = tem_str.split(' ')
                    # 正常上班时间
                    normal_go_to_work_time = str(record.date) + " " + tem_list[0] + ":00"
                    normal_go_to_work_time = datetime.datetime.strptime(normal_go_to_work_time, "%Y-%m-%d %H:%M:%S")
                    # 正常下班时间
                    normal_time_from_work = str(record.date) + " " + tem_list[-1] + ":00"
                    normal_time_from_work = datetime.datetime.strptime(normal_time_from_work, "%Y-%m-%d %H:%M:%S")

                    # 如果上班没打卡
                    if go_to_work_time == False:
                        comment = "上班没打卡"
                        late_time = 0
                    else:
                        if record.date == record.employee.entry_time:
                            comment = "入职第一天不计迟到时间！"
                            late_time = 0
                        else:
                            # 如果上班打卡时间 > 正常考勤的上班时间r
                            if go_to_work_time > normal_go_to_work_time:
                                # 迟到时间(分钟) = (上班打卡时间 - 正常考勤的上班时间)
                                late_time = ((go_to_work_time - normal_go_to_work_time).seconds) / 60
                            else:
                                late_time = 0

                    # 如果下班没打卡
                    if time_from_work == False:
                        comment = "下班没打卡"
                        leave_early = 0
                    else:
                        # 如果下班打卡时间 < 正常考勤的下班时间
                        if time_from_work < normal_time_from_work:
                            # 早退时间(分钟) = (下班打卡时间 - 正常考勤的上班时间)
                            leave_early = ((normal_time_from_work - time_from_work).seconds) / 60
                        else:
                            leave_early = 0

                # 创建迟到早退记录
                self.env["come.to.work"].sudo().create({
                    "date": record.date,    # 日期
                    "name": record.employee.id,     # 员工
                    "minutes_late": late_time,      # 迟到分钟数
                    "total_time_early": leave_early,    # 早退分钟数
                    # "comment": comment,  # 备注
                })

            else:
                raise ValidationError('%s的上下班时间没有写' % record.employee.name)




    @api.constrains('date', 'employee')
    def _check_something(self):
        # for record in self:
        demo = self.env['punch.in.record'].sudo().search(
            [('date', '=', self.date), ('employee', '=', self.employee.id)])
        if len(demo) > 1:
            raise ValidationError("同一个人同一天不能有多个记录")




    # 创建考勤打卡记录
    def create_attendance_record(self):

        custom_calendar_obj = self.env["custom.calendar"].sudo().search([
            ("date", "=", self.date)
        ])
        if custom_calendar_obj:
            # 获取员工休息类型
            rest_type = self.employee.time_plan.split(' ')[-1]
            # 获取员工部门
            department_id = self.employee.department_id.id

            custom_calendar_line_obj = self.env["custom_calendar_line"].sudo().search([
                ("custom_calendar_id", "=", custom_calendar_obj.id),    # 日历id
                ("department", "=", department_id)   # 部门id
                ])

            if rest_type == "单休" and custom_calendar_line_obj.state == "休息":
                pass
            elif rest_type == "大小休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息"):
                pass
            elif rest_type == "双休" and (custom_calendar_line_obj.state == "休息" or custom_calendar_line_obj.state== "大小休休息" or custom_calendar_line_obj.state== "仅双休休息"):
                pass
            else:
                self.env["attendance_record"].sudo().create({
                    "date": self.date,
                    "employee": self.employee.id,
                    "check_sign": self.check_sign
                })

        else:
            self.env["attendance_record"].sudo().create({
                "date": self.date,
                "employee": self.employee.id,
                "check_sign": self.check_sign
            })

    @api.model
    def create(self, val):

        object = super(punch_in_record, self).create(val)

        # 创建考勤打卡记录
        object.create_attendance_record()

        return object


    def unlink(self):
        # 删除上下班的数据
        # id
        for record in self:
            id = record.come_to_work_id.id
            demo = self.env['come.to.work'].sudo().search([('id', '=', id)])
            demo.sudo().unlink()

            attendance_record_obj = self.env["attendance_record"].sudo().search([
                ("date", "=", record.date),
                ("employee", "=", record.employee.id)
            ])
            attendance_record_obj.sudo().unlink()

        return super(punch_in_record, self).unlink()



