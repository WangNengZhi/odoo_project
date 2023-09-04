import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils import weixin_utils
import requests
import json





class Channel(models.Model):
    _inherit = 'mail.channel'
    
    def send_fsn_dv_attendance_channel_messages(self, today):
        #发送研发信息到研发专用频道   
        first_day = datetime(today.year, today.month, 1)
        today_finish_jobs = self.env['development_tasks'].sudo().search([('end_time', '<=', today),('end_time', '>', first_day)])
        today_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', first_day)])
        message_strs = f"{today.date()},本月分配任务:增加新功能 {len(today_job_newdate)}项 修复BUG {len(today_job_BUG)}项 新增内容 {len(today_job_update)}项 修改内容 {len(today_job_change)}项<br/>"
        today_finish_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', first_day)])
        message_strs += f"本月研发完成任务:增加新功能 {len(today_finish_job_newdate)}项 修复BUG {len(today_finish_job_BUG)}项 新增内容 {len(today_finish_job_update)}项 修改内容 {len(today_finish_job_change)}项<br/>"
        today_doing_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('state', '=', '进行中')])
        today_doing_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('state', '=', '进行中')])
        today_doing_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('state', '=', '进行中')])
        today_doing_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('state', '=', '进行中')])
        message_strs += f"本月进行中任务:增加新功能 {len(today_doing_job_newdate)}项 修复BUG {len(today_doing_job_BUG)}项 新增内容 {len(today_doing_job_update)}项 修改内容 {len(today_doing_job_change)}项<br/>"
        #doing_dv_jobs =  self.env['development_tasks'].sudo().search([('state', '=', '进行中')])
        #message_strs += f"已完成任务:<br/>"
        #for today_finish_job in today_finish_jobs:
            #message_strs += f"  " + f"任务标题:{today_finish_job.task_title};  任务类型:{today_finish_job.task_type}<br/>"
        #message_strs += f"进行中任务:<br/>"
        #for doing_dv_job in doing_dv_jobs:
            #message_strs += f"  " + f"任务标题:{doing_dv_job.task_title};  任务类型:{doing_dv_job.task_type}<br/>"
        dv_peoples = self.env['development_tasks'].sudo().search([])
        dv_people = dv_peoples.mapped('developer_personnel.name')
        dv_job = self.env['hr.employee'].sudo().search([('is_delete', '!=',True), ('name', '=', dv_people)])
        dv_names = dv_job.mapped('name')
        for dv_name in dv_names:
            message_strs += f"开发人员:{dv_name}<br/>"
            name_today_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>',first_day)])
            name_today_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', first_day)])
            name_today_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', first_day)])
            name_today_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', first_day)])
            message_strs += f"分配任务:增加新功能 {len(name_today_job_newdate)}项 修复BUG {len(name_today_job_BUG)}项 新增内容 {len(name_today_job_update)}项 修改内容 {len(name_today_job_change)}项<br/>"
            name_today_finish_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>',first_day)])
            name_today_finish_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', first_day)])
            name_today_finish_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', first_day)])
            name_today_finish_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', first_day)])
            message_strs += f"完成研发任务:增加新功能 {len(name_today_finish_job_newdate)}项 修复BUG {len(name_today_finish_job_BUG)}项 新增内容 {len(name_today_finish_job_update)}项 修改内容 {len(name_today_finish_job_change)}项<br/>"
            name_today_doing_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('state', '=', '进行中')])
            name_today_doing_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('state', '=', '进行中')])
            name_today_doing_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('state', '=', '进行中')])
            name_today_doing_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('state', '=', '进行中')])
            message_strs += f"进行中任务:增加新功能 {len(name_today_doing_job_newdate)}项 修复BUG {len(name_today_doing_job_BUG)}项 新增内容 {len(name_today_doing_job_update)}项 修改内容 {len(name_today_doing_job_change)}项<br/>"
            name_doing_dv_jobs = self.env['development_tasks'].search([('developer_personnel.name', '=',dv_name ),('state', '=', '进行中')])
            message_strs += f"进行中任务:<br/>"   
            for name_doing_dv_job in name_doing_dv_jobs:
                message_strs += f"  " + f"任务标题:{name_doing_dv_job.task_title};  任务类型:{name_doing_dv_job.task_type}<br/>"
            message_strs += f"已完成任务:<br/>"
            new_dv_jobs = self.env['development_tasks'].search([('developer_personnel.name', '=',dv_name ),('end_time', '<=', today),('end_time', '>', today - timedelta(days=2))])
            for new_dv_job in new_dv_jobs:
                message_strs += f"  " + f"任务标题:{new_dv_job.task_title};  任务类型:{new_dv_job.task_type}<br/>"
        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].sudo().search([('id', '=', 4)])
        channel.sudo().message_post(body=message_strs, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
    
    """ def send_fsn_dv_kpi_channel_messages(self, today):
        #发送月研发信息到研发专用频道
        message_strs = f"{today.date()}，研发任务月完成量！<br/>"    
        dvs = self.env['development_tasks'].sudo().search([])
        dv_names = dvs.mapped('developer_personnel.name')
        for dv_name in dv_names:
            bug_finish_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '=', '已升级'), ('task_type', '=', 'BUG修复'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            new_finish_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '=', '已升级'), ('task_type', '=', '增加内容'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            dv_finish_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '=', '已升级'), ('task_type', '=', '新功能'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            change_finish_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '=', '已升级'), ('task_type', '=', '内容修改'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            no_finish_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '!=', '已升级'), ('state', '!=', '已作废'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            give_up_job = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ), ('state', '=', '已作废'),('create_date', '<=', today.date()), ('create_date', '>', today.date() - relativedelta(months=1))])
            data = {
                "开发人员":dv_name,
                "BUG修复数":len(bug_finish_job),
                "增加内容数":len(new_finish_job),
                "增加功能数":len(dv_finish_job),
                "内容修改数":len(change_finish_job),
                "未完成数":len(no_finish_job),
                "作废项目数":len(give_up_job)
            } 
            message_strs += f"开发人员:{dv_name}<br/> BUG修复数:{len(bug_finish_job)}<br/> 增加内容数:{len(new_finish_job)}<br/> 增加功能数:{len(dv_finish_job)}<br/> 内容修改数:{len(change_finish_job)}<br/>  未完成数:{len(no_finish_job)}<br/> 作废项目数:{len(give_up_job)}<br/>"
        #dv_start_times1 = self.env['development_tasks'].mapped('start_time')
        # 发送人
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        # 发送频道
        channel = self.env["mail.channel"].sudo().search([('id', '=', 4)])
        channel.sudo().message_post(body=message_strs, author_id=odoobot_id, message_type="notification", subtype_xmlid="mail.mt_comment")
        return channel
     """
    
    def send_devlopment_wx_messages(self, today):
        ''' 发送研发信息到研发群'''
        first_day = datetime(today.year, today.month, 1)
        today_finish_jobs = self.env['development_tasks'].sudo().search([('end_time', '<=', today),('end_time', '>', first_day)])
        today_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', first_day)])
        today_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', first_day)])
        messages = f"{today.date()},本月分配任务:增加新功能 {len(today_job_newdate)}项 修复BUG {len(today_job_BUG)}项 新增内容 {len(today_job_update)}项 修改内容 {len(today_job_change)}项 \n"
        today_finish_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', first_day)])
        today_finish_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', first_day)])
        messages += f"本月研发完成任务:增加新功能 {len(today_finish_job_newdate)}项 修复BUG {len(today_finish_job_BUG)}项 新增内容 {len(today_finish_job_update)}项 修改内容 {len(today_finish_job_change)}项 \n"
        today_doing_job_newdate = self.env['development_tasks'].sudo().search([('task_type', '=', '新功能'),('state', '=', '进行中')])
        today_doing_job_BUG = self.env['development_tasks'].sudo().search([('task_type', '=', 'BUG修复'),('state', '=', '进行中')])
        today_doing_job_update = self.env['development_tasks'].sudo().search([('task_type', '=', '增加内容'),('state', '=', '进行中')])
        today_doing_job_change = self.env['development_tasks'].sudo().search([('task_type', '=', '内容修改'),('state', '=', '进行中')])
        messages += f"本月进行中任务:增加新功能 {len(today_doing_job_newdate)}项 修复BUG {len(today_doing_job_BUG)}项 新增内容 {len(today_doing_job_update)}项 修改内容 {len(today_doing_job_change)}项 \n"
        #doing_dv_jobs =  self.env['development_tasks'].sudo().search([('state', '=', '进行中')])
        #message_strs += f"已完成任务:<br/>"
        #for today_finish_job in today_finish_jobs:
            #message_strs += f"  " + f"任务标题:{today_finish_job.task_title};  任务类型:{today_finish_job.task_type}<br/>"
        #message_strs += f"进行中任务:<br/>"
        #for doing_dv_job in doing_dv_jobs:
            #message_strs += f"  " + f"任务标题:{doing_dv_job.task_title};  任务类型:{doing_dv_job.task_type}<br/>"
        dv_peoples = self.env['development_tasks'].sudo().search([])
        dv_people = dv_peoples.mapped('developer_personnel.name')
        dv_job = self.env['hr.employee'].sudo().search([('is_delete', '!=',True), ('name', '=', dv_people)])
        dv_names = dv_job.mapped('name')
        for dv_name in dv_names:
            messages += f"开发人员:{dv_name} \n"
            name_today_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('create_date', '<=', today),('create_date', '>',first_day)])
            name_today_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('create_date', '<=', today),('create_date', '>', first_day)])
            name_today_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('create_date', '<=', today),('create_date', '>', first_day)])
            name_today_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('create_date', '<=', today),('create_date', '>', first_day)])
            messages += f"分配任务:增加新功能 {len(name_today_job_newdate)}项 修复BUG {len(name_today_job_BUG)}项 新增内容 {len(name_today_job_update)}项 修改内容 {len(name_today_job_change)}项 \n"
            name_today_finish_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('end_time', '<=', today),('end_time', '>',first_day)])
            name_today_finish_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('end_time', '<=', today),('end_time', '>', first_day)])
            name_today_finish_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('end_time', '<=', today),('end_time', '>', first_day)])
            name_today_finish_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('end_time', '<=', today),('end_time', '>', first_day)])
            messages += f"完成研发任务:增加新功能 {len(name_today_finish_job_newdate)}项 修复BUG {len(name_today_finish_job_BUG)}项 新增内容 {len(name_today_finish_job_update)}项 修改内容 {len(name_today_finish_job_change)}项 \n"
            name_today_doing_job_newdate = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '新功能'),('state', '=', '进行中')])
            name_today_doing_job_BUG = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', 'BUG修复'),('state', '=', '进行中')])
            name_today_doing_job_update = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '增加内容'),('state', '=', '进行中')])
            name_today_doing_job_change = self.env['development_tasks'].sudo().search([('developer_personnel.name', '=',dv_name ),('task_type', '=', '内容修改'),('state', '=', '进行中')])
            messages += f"进行中任务:增加新功能 {len(name_today_doing_job_newdate)}项 修复BUG {len(name_today_doing_job_BUG)}项 新增内容 {len(name_today_doing_job_update)}项 修改内容 {len(name_today_doing_job_change)}项 \n"
            name_doing_dv_jobs = self.env['development_tasks'].search([('developer_personnel.name', '=',dv_name ),('state', '=', '进行中')])
            messages += f"进行中任务:\n"
            for name_doing_dv_job in name_doing_dv_jobs:
                messages += f"  " + f"任务标题:{name_doing_dv_job.task_title};  任务类型:{name_doing_dv_job.task_type} \n"
            messages += f"已完成任务:\n"
            new_dv_jobs = self.env['development_tasks'].search([('developer_personnel.name', '=',dv_name ),('end_time', '<=', today),('end_time', '>', today - timedelta(days=2))])
            for new_dv_job in new_dv_jobs:
                messages += f"  " + f"任务标题:{new_dv_job.task_title};  任务类型:{new_dv_job.task_type} \n"


        weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.DEVELOPMENT_GROUP)
        #weixin_utils.send_app_group_info_markdown_weixin(messages, chatid=weixin_utils.DEVELOPMENT_AND_TEST)