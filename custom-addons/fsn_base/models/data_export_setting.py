from odoo import api, fields, models
from odoo.exceptions import ValidationError

class DataExportSetting(models.Model):
    _name = 'data_export_setting'
    _description = 'FSN数据导出权限设置'
    _rec_name = 'name'
    _order = "create_date desc"


    def set_res_group_id(self):
        return self.env.ref('base.group_allow_export').id

    name = fields.Char(string="名称", required=True)
    model_id = fields.Many2one('ir.model', string='模型', required=True, ondelete='cascade')
    users = fields.Many2many('res.users', string="员工")

    res_group_id = fields.Many2one("res.groups", string="组别", compute="set_res_group_id_users", store=True, default=set_res_group_id)



    # 检查数据唯一性
    @api.constrains('model_id')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('model_id', '=', self.model_id.id)
        ])

        if len(demo) > 1:
            raise ValidationError("已经存在该模型的导出权限设置记录了！")




    @api.depends('users')
    def set_res_group_id_users(self):
        for record in self:

            for user in record.users:

                record.res_group_id.users = [(4, user.id)]