from odoo import models, fields, api


class ProductionPreparationLineSample(models.Model):
    _name = "production_preparation_line_sample"
    _description = '产前准备明细样本'
    _order = 'sequence'


    group_type = fields.Selection([('1_3pgcxx', '3P过程信息'),
                                    ('2_swqr', '实物确认'),
                                    ('3_pxqzb', '培训前准备'),
                                    ('4_sbpx', '首包培训'),
                                    ('5_dhkkqzb', '大货开款前准备'),
                                    ('6_xczk', '现场转款'),
                                    ], string="组别")
    before_go_online = fields.Selection([('1_four_day', '四天'),
                                        ('2_three_day', '三天'),
                                        ('3_two_day', '两天'),
                                        ('4_punish', '当天'),
                                        ], string="新款上线前")
    content = fields.Char(string="内容")
    department_ids = fields.Many2many("hr.department", string="部门")
    sequence = fields.Integer(string="序号")