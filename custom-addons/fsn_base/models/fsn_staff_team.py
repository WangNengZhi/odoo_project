from odoo import api, fields, models
from odoo.exceptions import ValidationError

class FsnStaffTeam(models.Model):
    _name = 'fsn_staff_team'
    _description = 'FSN_员工小组'
    _rec_name = 'name'
    _order = "sequence"


    name = fields.Char(string="小组名称", required=True)
    sequence = fields.Integer()
    type = fields.Selection([
        ('车间','车间'),
        ('后道','后道'),
        ('裁床','裁床'),
        ('外部','外部')
    ], string='类型', required=True)
    department_id = fields.Many2one("hr.department", string="部门")

    @api.constrains('name')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('name', '=', record.name)])
            if len(demo) > 1:
                raise ValidationError(f"小组名称重复！")
