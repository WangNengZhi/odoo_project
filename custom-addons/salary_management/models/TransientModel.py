from odoo.exceptions import ValidationError
from odoo import models, fields, api
import datetime
import calendar


class NumberSettingsWizard(models.TransientModel):
    _name = 'number_settings_wizard'
    _description = '数量设置向导'
    # _order = 'id asc'

    number = fields.Float(string="数量")



    def action_number(self):

        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        for active_id in active_ids:
            active_model_obj = self.env[active_model].sudo().browse(active_id)

            date = active_model_obj.date
            date = date.split('-')
            year = int(date[0])
            month = int(date[1])

            first_day = datetime.date(year,month,1)

            # 应出勤增加或减少天数
            active_model_obj.should_attend = active_model_obj.should_attend + self.number

            # 如果入职时间 >= 本月第一天 实际出勤天数则不增加或减少, 否则实际出勤天数跟随应出勤天数增加或减少
            if active_model_obj.name.entry_time >= first_day:

                # 但是如果实出勤天数 > 应出勤天数,则实出勤天数 = 应出勤天数
                if active_model_obj.clock_in_time > active_model_obj.should_attend:
                    active_model_obj.clock_in_time = active_model_obj.should_attend

            else:

                active_model_obj.clock_in_time = active_model_obj.clock_in_time + self.number



class TimeHorizonWizard(models.TransientModel):
    _name = 'time_horizon_wizard'
    _description = '正常薪资设置'
    # _order = 'id asc'

    start_time = fields.Date(string="开始时间")
    end_time = fields.Date(string="结束时间")

    calculation = fields.Selection([('按月计算','按月计算'), ('按天计算','按天计算')], string='计算方式')


    def action_time_horizon(self):

        if (self.start_time and not self.end_time) or (not self.start_time and self.end_time):
            raise ValidationError(f"不能只填开始时间或只填写结束时间!")

        else:

            active_ids = self.env.context.get('active_ids')
            active_model = self.env.context.get('active_model')

            for active_id in active_ids:
                active_model_obj = self.env[active_model].sudo().browse(active_id)

                active_model_obj.current_salary_refresh(self.start_time, self.end_time, self.calculation)

