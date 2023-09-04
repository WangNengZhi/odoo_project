from datetime import datetime, timedelta

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class DevelopManage(models.Model):
    _name = 'develop_manage'
    _description = '开发管理'

    month = fields.Date(string="日期")
    emp = fields.Many2one('hr.department', string='部门')
    dv_name = fields.Many2one('hr.employee', string='开发人员')
    joined_date = fields.Date(string='入职日期')
    termination_date = fields.Date(string='离职日期')
    planned_new_job = fields.Integer(string='分配新功能数')
    planned_bug = fields.Integer(string='分配修复bug数')
    planned_new_data = fields.Integer(string='分配新内容数')
    planned_change_data = fields.Integer(string='分配更改内容数')
    finish_new_job = fields.Integer(string='完成新功能数')
    finish_bug = fields.Integer(string='完成修复bug数')
    finish_new_data = fields.Integer(string='完成新内容数')
    finish_change_data = fields.Integer(string='完成更改内容数')
    data_month = fields.Integer(string='日期月份')
    year = fields.Integer(string='日期年份')
    def get_develop_data(self, today):
        """获取开发数据"""
        month_start_data = datetime(today.year, today.month, 1)
        # 构建当前日期作为截止日期
        dv_employees =  self.env['development_tasks'].sudo().search([])
        dv_employees_names = dv_employees.mapped('developer_personnel.name')
        dv_names =  self.env['hr.employee'].sudo().search([('name', '=', dv_employees_names),('is_delete', '=', False)])
        for dv_name in dv_names:
            planned_new_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_bug = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_new_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_change_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            finish_new_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_bug = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_new_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_change_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            data = {
                'month':today,
                'dv_name':dv_name.id,
                'emp':dv_name.department_id.id,
                'joined_date':dv_name.entry_time,
                'termination_date':dv_name.is_delete_date,
                'planned_new_job':len(planned_new_job),
                'planned_bug':len(planned_bug),
                'planned_new_data':len(planned_new_data),
                'planned_change_data':len(planned_change_data),
                'finish_new_job':len(finish_new_job),
                'finish_bug':len(finish_bug),
                'finish_new_data':len(finish_new_data),
                'finish_change_data':len(finish_change_data),
                'data_month':today.month,
                'year':today.year,
            }
            self.sudo().create(data)
            #print(data)
        

    def update_develop_data(self,today):
        """更新开发数据"""
        month_start_data = datetime(today.year, today.month, 1)
        # 构建当前日期作为截止日期
        dv_employees =  self.env['development_tasks'].sudo().search([])
        dv_employees_names = dv_employees.mapped('developer_personnel.name')
        dv_names =  self.env['hr.employee'].sudo().search([('name', '=', dv_employees_names),('is_delete', '=', False)])
        for dv_name in dv_names:
            planned_new_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_bug = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_new_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            planned_change_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', month_start_data)])
            finish_new_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_bug = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_new_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            finish_change_data = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name.name ),('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', month_start_data)])
            data = {
                'month':today,
                'dv_name':dv_name.id,
                'emp':dv_name.department_id.id,
                'joined_date':dv_name.entry_time,
                'termination_date':dv_name.is_delete_date,
                'planned_new_job':len(planned_new_job),
                'planned_bug':len(planned_bug),
                'planned_new_data':len(planned_new_data),
                'planned_change_data':len(planned_change_data),
                'finish_new_job':len(finish_new_job),
                'finish_bug':len(finish_bug),
                'finish_new_data':len(finish_new_data),
                'finish_change_data':len(finish_change_data),
                'data_month':today.month,
                'year':today.year,
            }
            self.env['develop_manage'].sudo().search([('data_month', '=', today.month),('year', '=', today.year),  ('dv_name', '=', dv_name.id)]).write(data)
        

