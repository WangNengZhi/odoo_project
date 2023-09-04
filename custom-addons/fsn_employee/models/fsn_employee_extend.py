from odoo import models, fields, api
from datetime import datetime, timedelta
import collections
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    staff_level = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('实习', '实习'),
    ], string='员工等级', required=True)

    delete_confirm_date = fields.Date('离职人事核定日期', compute="is_delete_changed", store=True)

    is_inductrial_injury_insurance = fields.Selection([
        ('交', '交'),
        ('不交', '不交'),
    ], string="是否交工伤险", required=True)


    @api.depends('is_delete')
    def is_delete_changed(self):
        for record in self:
            if record.is_delete:
                record.delete_confirm_date = datetime.now().date()
            else:
                record.delete_confirm_date = None


    disability_certificate = fields.Many2many(
        'ir.attachment',
        relation='disability_certificate_res_att_rel',
        column1='disability_certificate_id',
        column2='att_id',
        string="残疾证明"
    )


    academic_certificate = fields.Many2many(
        'ir.attachment',
        relation='academic_certificate_res_att_rel',
        column1='academic_certificate_id',
        column2='att_id',
        string="学历证书"
    )
    @api.constrains('department_id', 'academic_certificate')
    def _check_academic_certificate(self):

        for record in self:
            print(record.department_id.name, len(record.academic_certificate))
            if record.department_id.name in {"人事行政部", "开发部", "财务部"} and len(record.academic_certificate) == 0:

                raise ValidationError(f"{self.name},人事行政部,开发部,财务部,的员工必须上传学历证明！")

    employee_handbook = fields.Selection([('已签', '已签'), ('未签', '未签')], string='员工手册', required=True)
    performance_appraisal = fields.Selection([('已签', '已签'), ('未签', '未签')], string='绩效考核', required=True)
    compensation_system = fields.Selection([('已签', '已签'), ('未签', '未签')], string='薪酬制度', required=True)
    job_responsibility = fields.Selection([('已签', '已签'), ('未签', '未签')], string='岗位职责', required=True)
    attendance_system = fields.Selection([('已签', '已签'), ('未签', '未签')], string='考勤制度', required=True)
    dormitory_management = fields.Selection([('已签', '已签'), ('未签', '未签')], string='宿舍管理制度', required=True)
    confidentiality_agreement = fields.Selection([('已签', '已签'), ('未签', '未签')], string='保密协议', required=True)
    other_agreement = fields.Selection([('已签', '已签'), ('未签', '未签')], string='其他', required=True)

    enterprise_wechat_account = fields.Char(string="企业微信账号")



    # 生成员工编号
    def generate_random_barcode(self):
        for record in self:

            hr_employee_objs = self.env["hr.employee"].sudo().search([
                ("barcode", "!=", False)
            ])

            tem_barcode_list = []
            for hr_employee_obj in hr_employee_objs:

                tem_barcode_list.append(int(hr_employee_obj.barcode))

            if tem_barcode_list:
                tem_barcode = str(max(tem_barcode_list) + 1)

                if len(tem_barcode) == 1:
                    tem_barcode = f"00000{tem_barcode}"
                elif len(tem_barcode) == 2:
                    tem_barcode = f"0000{tem_barcode}"
                elif len(tem_barcode) == 3:
                    tem_barcode = f"000{tem_barcode}"
                elif len(tem_barcode) == 4:
                    tem_barcode = f"00{tem_barcode}"
                elif len(tem_barcode) == 5:
                    tem_barcode = f"0{tem_barcode}"
                elif len(tem_barcode) == 6:
                    tem_barcode = tem_barcode

                record.barcode = tem_barcode

            else:
                record.barcode = "000001"

            # tem_barcode = max((int(e.barcode) for e in hr_employee_objs), default=0) + 1
            # record.barcode = '%06d' % tem_barcode


    def get_employees_enrolled(self, date):
        ''' 获取指定日入职或在该日之前入职但在该日录入的员工的列表 '''
        begin_time = datetime(date.year, date.month, date.day)
        end_time = begin_time + timedelta(days=1)
        return list(self.env["hr.employee"].sudo().search([
                '|', ("entry_time", "=", date),
                     '&', ("entry_time", "<", date),
                          '&', ('create_date','>=',begin_time), ('create_date','<',end_time)
            ]))

    def get_employees_left(self, date):
        ''' 获取指定日离职或人事在该日核定为已离职的员工的列表 '''
        return list(self.env["hr.employee"].sudo().search([
                '|', ("is_delete_date", "=", date),
                     '&', ('is_delete_date','<',date), ('delete_confirm_date','=', date)
            ]))

    def get_employees_current(self):
        ''' 获取（此刻）在职的员工的列表 '''
        return list(self.env["hr.employee"].sudo().search([
                ("is_delete", "=", False)  # 入职日可能是今天之后
            ], order="department_id"))

    def get_departments(self, company_id=1):
        """" 获取全部部门 """
        return list(self.env["hr.department"].sudo().search([
                '&', ('company_id','=',company_id),
                     '!', ('name','like','(作废)')]))
        # return list(self.env["hr.department"].sudo().search([
        #           ('company_id','=',company_id),
        #           ('parent_id','=', 53)]))  # 53：总经办

    def get_department_hierarchy(self):
        ''' 获取部门的层次结构 '''
        depts = self.get_departments()  # 获取部门列表
        stats = {}  # parent_id 父部门 id -> 直属子部门
        for dept in depts:
            pnt_id = dept.parent_id.id if dept.parent_id else None
            # print(repr(dept.parent_id), repr(pnt_id))  # hr.department() None; hr.department(9,) 9
            if pnt_id not in stats:
                stats[pnt_id] = []
            stats[pnt_id].append(dept)
        return stats

    def get_dept_employees_mapping(self):
        ''' 获取“部门 -> 直属员工列表”的词典 '''
        current = self.get_employees_current()  # 获取在职员工

        emps = {}
        for emp in current:
            dept_id = emp.department_id.id
            if dept_id not in emps:
                emps[dept_id] = []
            emps[dept_id].append(emp)

        return emps

    def generate_stats_of_posts(self):
        ''' 生成公司各部门岗位人数的报告 '''
        def format(depts, emps, pnt_id, level=0):
            def format_employees(emps):

                if not emps:
                    return ''

                # stats = collections.Counter(emp.job_id.name for emp in emps)  # 不对, job 34 在 hr_job 中是“车位”
                stats = collections.Counter(emp.job_id.name for emp in emps)  # job 34 是“人事招聘专员”

                # (job_name, n), *others = stats.items()
                stats = sorted(stats.items())
                job_name, n = stats.pop()
                others = stats
                s = ''

                if others:
                    s += '、'.join(f'{n}个{job_name}' for job_name, n in others)
                    s += '和'
                s += f'{n}个{job_name}'

                return s

            if pnt_id not in depts:
                return
            for dept in depts[pnt_id]:
                s = format_employees(emps.get(dept.id, []))
                yield f"{'  '*level}{dept.name}：{s}\n"
                # print(f"{'  '*level}{dept.name}：{s or '0职工'}")
                yield from format(depts, emps, dept.id, level+1)


        depts = self.get_department_hierarchy()

        emps = self.get_dept_employees_mapping()

        return ''.join(format(depts, emps, pnt_id=53, level=0))  # 53：总经办



