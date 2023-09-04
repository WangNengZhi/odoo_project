
from datetime import date
from math import e
import pypinyin
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

from odoo import models, fields, api

class work(models.Model):
    _inherit = "hr.employee"

    mobile_phone = fields.Char('电话')
    # comp = fields.Char('公司')
    department_id = fields.Many2one('hr.department', '一级部门',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True)

    second_dapartment = fields.Char('二级部门')
    department_position = fields.Char('岗位名称', required=True)
    rank = fields.Char('职级')
    entry_time = fields.Date('入职日期', required=True)
    turn_positive_time = fields.Date('转正时间')
    is_it_a_temporary_worker = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)'),
    ], string='工种', required=True)
    outsourcing_type = fields.Selection([
        ('长期', '长期'),
        ('短期', '短期'),
    ], string="外包性质")

    is_delete = fields.Boolean(string='是否已离职')
    is_handover = fields.Boolean(string="是否已交接")
    handover_id = fields.Many2one("hr.employee", string="交接人")
    is_delete_date = fields.Date(string='离职时间')

    contract_signing_date = fields.Date('合同签订日期')
    contract_expiration_time = fields.Date('合同到期时间')
    contract_attributes = fields.Char('合同属性', compute='contract')
    # stay1 = fields.Char('是否入驻公司宿舍(删)')
    account_nature = fields.Char('户口性质')
    id_card = fields.Char('身份证号', required=True)
    age = fields.Integer('年龄')
    pin2 = fields.Char('名字拼音')
    bank_account_id1 = fields.Char('银行卡号')

    account_bank1 = fields.Char('开户行')
    comment = fields.Char('备注')
    month_payment_social = fields.Date('社保起交月')
    social_payment_base = fields.Char('社保缴纳基数')
    month_provident_fund_start = fields.Date('公积金起交月')
    social_provident_base = fields.Char('公积金基数')
    provident_fund_customer_number = fields.Char('公积金客户号')
    whether_the_labor_contract = fields.Char('劳动合同是否已加盖公章')
    entry_reg_form = fields.Char('入职登记表')
    entry_notification_from = fields.Char('入职告知单')
    labor_contract = fields.Char('劳动合同')
    confidentiality_agreement = fields.Char('保密协议')
    integrity_agreement = fields.Char('廉洁协议')
    copy_of_id_card = fields.Char('身份证复印件')
    copy_of_academic_qualifications = fields.Char('学历复印件')
    res_certificate = fields.Char('离职证明')

    job_id = fields.Many2one('hr.job', '部门岗位', required=True,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    gender1 = fields.Selection([
        ('男', '男'),
        ('女', '女'),
        ('其他', '其他')
    ], string='性别', groups="hr.group_hr_user", tracking=True)

    marital11 = fields.Selection([
        ('已婚', '已婚'),
        ('未婚', '未婚'),
    ], string='婚姻', groups="hr.group_hr_user", tracking=True)

    status = fields.Selection([
        ('正常', '正常'),
        ('请假', '请假'),
        ('旷工', '旷工')
    ], string='状态', default='正常')

    # 只要填写身份证就会设置一个拼音

    birthday1 = fields.Date('年月日')
    year = fields.Char('年')
    month = fields.Char('月')
    day = fields.Char('日')

    nationality = fields.Char('民族')
    education1 = fields.Char('学历')
    major = fields.Char('专业')
    full_time = fields.Char('是否全日制')

    introducer = fields.Char('招聘来源/介绍人')
    recent_work_unit = fields.Char('近期工作单位')
    current_home_address = fields.Char('现居住地址')
    time_plan = fields.Selection([
        ('8:00 - 21:00, 单休', '8:00 - 21:00, 单休'),
        ('9:00 - 18:00, 单休', '9:00 - 18:00, 单休'),
        ('9:00 - 18:00, 大小休', '9:00 - 18:00, 大小休'),
        ('9:00 - 18:00, 双休', '9:00 - 18:00, 双休'),
        ('8:00 - 18:00, 单休', '8:00 - 18:00, 单休'),
        ('7:30 - 17:00, 单休', '7:30 - 17:00, 单休'),
        ('8:00 - 19:00, 单休', '8:00 - 19:00, 单休'),
    ], string='上下班时间', required=True)
    fixed_salary = fields.Float('薪资', groups='hpro.xinziboss2')
    # fixed_salary = fields.Float(string='薪资')
    stay2 = fields.Boolean(string='是否入驻公司宿舍')
    is_dormitory = fields.Selection([
        ('入住', '入住'),
        ('不入住', '不入住'),
    ], string='是否入住公司宿舍', required=True)
    stay2_money = fields.Float(string='宿舍押金')
    dormitory_subsidy = fields.Selection([
        ('有', '有'),
        ('没有', '没有'),
    ], string='是否有宿舍补贴', required=True)
    rice_tonic = fields.Selection([
        ('有', '有'),
        ('没有', '没有'),
    ], string='是否有饭补', required=True)
    is_attendance_bonus = fields.Selection([
        ('有', '有'),
        ('没有', '没有'),
    ], string="是否有全勤", required=True)

    # # 房租扣款
    # rent_deduction = fields.Float(string='房租扣款')
    # # 餐费扣款
    # meal_deduction = fields.Float(string='餐费扣款')
    # 是否交社保
    whether_to_pay_social_security = fields.Boolean(string='是否交社保')
    is_social_security = fields.Selection([
        ('交', '交'),
        ('不交', '不交'),
    ], string='是否交社保', required=True)

    is_introducer = fields.Selection([
        ("有", "有"),
        ("无", "无"),
    ], required=True)
    introducer = fields.Many2one("hr.employee", string="介绍人")



    # 当无介绍人时，则情况介绍人字段
    @api.onchange('is_introducer', 'introducer')
    def empty_introducer(self):
        if self.is_introducer != "有":
            self.introducer = False


    #  如果stay1等于flase的话，stay2清空
    @api.onchange('stay2')
    def stay_onchange(self):
        if self.is_dormitory == "入住":
            pass
        elif self.is_dormitory == "不入住":
            self.stay2_money = 0
    @api.depends('is_it_a_temporary_worker')
    #     '合同属性'和工种保持一致
    def contract(self):
        for i in self:
            i.contract_attributes = i.is_it_a_temporary_worker
    @api.onchange('birthday1')
    def chan(self):
        if self.birthday1:
            demo = str(self.birthday1).split('-')
            self.year = demo[0]
            self.month = demo[1]
            self.day = demo[2]

    # @api.onchange('id_card')
    def onname(self):
        id = self.display_name
        #得到拼音的方法
        def pinyin(word):
            s = ''
            for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
                s += ''.join(i)
            return s
        #传入的姓名的拼音
        s = pinyin(id)
        # n = len(s)
        # 数据库中的所有的拼音
        demo1 = self.env['hr.employee'].sudo().search([])
        d = []
        for i in demo1:
            for j in i:
               if  j.pin2 == False:
                  continue
               else:
                  d.append(j.pin2)
        print(d)
        #a是拼音，d是列表

        if s not in d:
            self.pin2 = s
        else:
            b = []
            if s in d:
                b.append(s)
                d.remove(s)
            for r in d:
                if r[0:len(s)] == s and int(r[len(s):len(s) + 1]):
                    b.append(r)
            n = len(b)
            s1 = s + str(n)
            self.pin2 = s1

    # @api.model
    # def create(self,val):
    #    id_card = self.env['hr.employee'].sudo().search([('id_card', '=', self.id_card)])
    #    if id_card:
    #        raise ValidationError('此人已经输入过了')
    #    else:
    #        return super(work, self).create(val)

    # @api.onchange('is_delete_date')
    # def onc_id_delete(self):
    #     if self.is_delete_date:
    #         self.is_delete = True
    #     else:
    #         self.is_delete = False
    @api.onchange('is_delete_date')
    def onc_id_delete(self):
        if self.is_delete_date:
            self.is_delete = True
        else:
            self.is_delete = False

    # @api.onchange('is_delete')
    # def onc_id_delete2(self):
    #     if self.is_delete:
    #         self.is_delete_date = datetime.now() + timedelta(hours=8)
    #     else:
    #         self.is_delete_date = False
    @api.onchange('is_delete')
    def onc_id_delete2(self):
        if self.is_delete and not self.is_delete_date:
            self.is_delete_date = fields.Date.today()

        if not self.is_delete:
            self.is_delete_date = False

    # 检测员工姓名不能重复！
    @api.constrains('name')
    def _check_something(self):
        # for record in self:
        demo = self.env['hr.employee'].sudo().search([('name', '=', self.name)])
        if len(demo) > 1:
            raise ValidationError("同一个人不能有多个记录")



    # 创建时设置人事奖励
    def set_personnel_award(self):

        personnel_award_objs = self.env["personnel_award"].sudo().search([
            ("emp_id", "=", self.id)
        ])
        if not personnel_award_objs:
            personnel_award_objs.sudo().create({"emp_id":self.id})


    @api.model
    def create(self, vals):

        res = super(work, self).create(vals)

        if res.is_introducer == "有":
            # 设置人事奖励
            res.set_personnel_award()

        return res

    # 修改时设置人事奖励
    def write_set_personnel_award(self):

        if self.is_introducer == "有":

            self.set_personnel_award()
        else:
            personnel_award_objs = self.env["personnel_award"].sudo().search([
                ("emp_id", "=", self.id)
            ])
            if personnel_award_objs:
                personnel_award_objs.sudo().unlink()


    def write(self, vals):

        res = super(work, self).write(vals)
        # 如果介绍人信息发生变化
        if "is_introducer" in vals:

            self.write_set_personnel_award()

        return res


    @api.onchange('is_delete_date')
    def _onchange_is_delete_date(self):
        """离职日期发生变化更新personnel_turnover的值"""
        for employee in self:
            if employee.is_delete and employee.department_id:
                is_delete_year = employee.is_delete_date.year
                is_delete_month = employee.is_delete_date.month
                is_delete_year_month = f"{is_delete_year}-{is_delete_month:02}"
                target_values = self.env['target_output_value'].search([
                    ('year_month', '=', is_delete_year_month),
                    ('department_id', '=', employee.department_id.id)
                ])
                for target_value in target_values:
                    target_value.personnel_turnover += 1
