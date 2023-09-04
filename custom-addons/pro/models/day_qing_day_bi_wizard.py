from odoo import models, fields, api
from datetime import timedelta

class DayQingDaybiwizard(models.TransientModel):
    _name = 'day_qing_day_bi_wizard'
    _description = '日清日毕向导'



    refresh_mode = fields.Selection([('指定日期', '指定日期'), ('指定范围', '指定范围')], string='刷新方式', required=True)
    refresh_date = fields.Date(string="刷新日期")
    refresh_start_date = fields.Date(string="开始日期")
    refresh_end_date = fields.Date(string="结束日期")


    # 获取两个日期间的所有日期 
    def getEveryDay(self, begin_date, end_date): 
        date_list = [] 
        while begin_date <= end_date: 
            date_list.append(begin_date) 
            begin_date += timedelta(days=1) 
        return date_list


    def day_qing_day_bi_refresh(self):

        if self.refresh_mode == "指定日期":

            self.env['day_qing_day_bi'].sudo().manual_refresh(self.refresh_date)
        
        elif self.refresh_mode == "指定范围":
            
            for day_ in self.getEveryDay(self.refresh_start_date, self.refresh_end_date):

                self.env['day_qing_day_bi'].sudo().manual_refresh(day_)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




    # 审批通过
    def action_audit_through(self):

        active_id = self.env.context.get('active_id')  # 获取记录id
        active_model = self.env.context.get('active_model') # 获取记录模型名称

        record_obj = self.env[active_model].sudo().browse(active_id)     # 获取记录对象

        record_obj.refused_note = False

        record_obj.approve_state = "已审批"




    # 审批拒绝
    def action_audit_refused(self):

        active_id = self.env.context.get('active_id')  # 获取记录id
        active_model = self.env.context.get('active_model') # 获取记录模型名称

        record_obj = self.env[active_model].sudo().browse(active_id)     # 获取记录对象

        record_obj.approve_state = "未通过"

        record_obj.refused_note = self.refused_note