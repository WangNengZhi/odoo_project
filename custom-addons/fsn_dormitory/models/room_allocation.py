from odoo import api, fields, models
from odoo.exceptions import ValidationError




class RoomConfig(models.Model):
    """ 继承房间配置"""
    _inherit = 'room_config'

    room_allocation_ids = fields.One2many("room_allocation", "room_config_id", string="宿舍分配")





class RoomAllocation(models.Model):
    _name = 'room_allocation'
    _description = '宿舍分配'
    # _rec_name = 'room_serial_number'

    room_config_id = fields.Many2one("room_config", string="房间号", required=True, ondelete='restrict')


    dormitory_park_id = fields.Many2one("dormitory_park", string="园区", related="room_config_id.dormitory_park_id", store=True)
    dormitory_building_number_id = fields.Many2one("dormitory_building_number", string="楼号", related="room_config_id.dormitory_building_number_id", store=True)

    bed_no = fields.Char(string="床号", required=True)

    employee_id = fields.Many2one("hr.employee", string="员工")
    work_type = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生', '实习生'),
        ('外包(计时)', '外包(计时)'),
        ('外包(计件)', '外包(计件)')], related='employee_id.is_it_a_temporary_worker', store=True)
    job_id = fields.Many2one("hr.job", string="岗位", related='employee_id.job_id', store=True)


    stay_datetime = fields.Datetime(string="入住时间")
    check_out_datetime = fields.Datetime(string="退宿时间")
    is_the_key = fields.Boolean(string="是否有钥匙")

    # 检查数据唯一性
    @api.constrains('dormitory_building_number_id', 'bed_no','employee_id', 'room_config_id')
    def _check_unique(self):

        demo0 = self.env[self._name].sudo().search([
            ('bed_no', '=', self.bed_no),
            ('room_config_id', "=", self.room_config_id.id),
            ('dormitory_building_number_id', '=', self.dormitory_building_number_id.id),
        ])

        if len(demo0) > 2:
            raise ValidationError(f"一张床不可以睡超过两个人哦~！")
        
        demo1 = self.env[self._name].sudo().search([
            ('employee_id', '=', self.employee_id.id),
        ])
        if len(demo1) > 1:
            raise ValidationError(f"同一个员工不可住在多个床位！")

        if self.room_config_id:
            if (self.room_config_id.bed_number * 2) < len(self.room_config_id.room_allocation_ids):
                raise ValidationError(f"该房间床位数量超过上限！")

