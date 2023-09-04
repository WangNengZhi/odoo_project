from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DevelopmentTasks(models.Model):

    _name = "development_tasks"
    _description = '开发任务'
    _rec_name = 'task_title'
    _order = "create_date desc"


    task_title = fields.Char(string="任务标题", required=True)
    task_description = fields.Text(string="任务描述")
    start_time = fields.Datetime(string="开始时间")
    end_time = fields.Datetime(string="结束时间")
    task_type = fields.Selection([
        ('增加内容', '增加内容'),
        ('新功能', '新功能'),
        ('BUG修复', 'BUG修复'),
        ('内容修改', '内容修改'),
        ], string="任务类型", required=True)
    developer_personnel = fields.Many2one('hr.employee', string="开发人员", required=True)
    state = fields.Selection([
        ('未开始', '未开始'),
        ('进行中', '进行中'),
        ('已完成', '已完成'),
        ('已升级', '已升级'),
        ('已作废', '已作废'),
        ], string="状态", default="未开始", required=True)
    note = fields.Text(string="备注")
    design = fields.Text(string="设计")


    attachment_number = fields.Integer(string="附件数量", compute='_compute_attachment_number')
    attachment_ids = fields.Many2many(   
        'ir.attachment',					#关联附件模型
        relation='development_tasks_att_rel',		#关联表（字段与 ir.attachment 表的附件的关联表名）
        column1='development_tasks_id',					# first_attachment 的 id 列
        column2='att_id',					# ir.attachment 表的附件 id 列
        string="附件"
    )


    def _compute_attachment_number(self):
        domain = [('res_model', '=', 'development_tasks'), ('res_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)


    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'development_tasks'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'development_tasks', 'default_res_id': self.id}
        return res


    # 开始按钮
    def set_ongoing(self):
        for record in self:

            if record.state == "未开始":
                record.write({
                    "state": "进行中",
                    "start_time": fields.datetime.now()
                })
            else:
                raise ValidationError(f"发生异常，请联系管理员！")
    

    # 完成按钮
    def set_complete(self):
        for record in self:

            if record.state == "进行中":
                record.write({"state": "已完成",})
            else:
                raise ValidationError(f"发生异常，请联系管理员！")


    # 升级按钮
    def set_upgrade(self):
        for record in self:

            if record.state == "已完成" and record.design:
                record.write({
                    "state": "已升级",
                    "end_time": fields.datetime.now()
                })
            else:
                raise ValidationError(f"请填写设计文本！")
    

    # 作废按钮
    def set_invalid(self):
        for record in self:
            record.write({"state": "已作废",})
    

