from odoo.exceptions import ValidationError
from odoo import models, fields, api


class InheritPayroll3(models.Model):
    _inherit = "payroll3"


    # 对比检测工资条的实发工资
    def detection_real_hair(self):
        text = ""
        for record in self:
            
            payroll1_obj = self.env["payroll1"].sudo().search([
                ("date", "=", record.month),
                ("name", "=", record.name.id),
            ])


            if record.should_wage2 != payroll1_obj.salary_payable3:
                text = text + f"月份：{record.month}，员工: {record.name.name}\n"
            
        if text:
            raise ValidationError(f"{text}以上员工“应发”存在异常！")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('检测通过！'),
                    'message': '没有发现任何异常！',
                    'sticky': False,
                    'type': 'success'
                },
            }

    def jianchayingfa2(self):

        text = ""
        for record in self:
            
            payroll1_obj = self.env["payroll1"].sudo().search([
                ("date", "=", record.month),
                ("name", "=", record.name.id),
            ])

            print(payroll1_obj.name.name)

            if record.should_wage1 != payroll1_obj.salary_payable2:
                text = text + f"月份：{record.month}，员工: {record.name.name}\n"
            
        if text:
            raise ValidationError(f"{text}以上员工“应发”存在异常！")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('检测通过！'),
                    'message': '没有发现任何异常！',
                    'sticky': False,
                    'type': 'success'
                },
            }
