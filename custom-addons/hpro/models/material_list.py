# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class material_list(models.Model):
    _name = 'mater.maters'
    _description = '单件用料表'
    _rec_name = 'name'

    name = fields.Char(related='order_number.name', string='客户')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    size = fields.Char(string='尺码', required=True)


    # 面料
    picture = fields.Image(string='图片')
    door_width = fields.Char('门幅(旧)')
    number_of_pieces = fields.Char('片数(旧)')
    single_piece = fields.Char('单件(旧)')
    comment = fields.Char('备注')

    float_door_width = fields.Float(string="门幅(CM)")
    float_number_of_pieces = fields.Float(string="片数")
    float_single_piece = fields.Float(string="单件(CM)")



    # 里料
    picture1 = fields.Image(string='图片')
    door_width1 = fields.Char('门幅(旧)')
    number_of_pieces1 = fields.Char('片数(旧)')
    single_piece1 = fields.Char('单件(旧)')
    comment1 = fields.Char('备注')

    float_door_width1 = fields.Float(string="门幅(CM)")
    float_number_of_pieces1 = fields.Float(string="片数")
    float_single_piece1 = fields.Float(string="单件(CM)")



    # 胆布
    picture2 = fields.Image(string='图片')
    door_width2 = fields.Char('门幅(旧)')
    number_of_pieces2 = fields.Char('片数(旧)')
    single_piece2 = fields.Char('单件(旧)')
    comment2 = fields.Char('备注')

    float_door_width2 = fields.Float(string="门幅(CM)")
    float_number_of_pieces2 = fields.Float(string="片数")
    float_single_piece2 = fields.Float(string="单件(CM)")



    # 棉
    picture3 = fields.Image(string='图片')
    door_width3 = fields.Char('门幅(旧)')
    number_of_pieces3 = fields.Char('片数(旧)')
    single_piece3 = fields.Char('单件(旧)')
    comment3 = fields.Char('备注')

    float_door_width3 = fields.Float(string="门幅(CM)")
    float_number_of_pieces3 = fields.Float(string="片数")
    float_single_piece3 = fields.Float(string="单件(CM)")


    # 粘衬
    picture4 = fields.Image(string='图片')
    door_width4 = fields.Char('门幅(旧)')
    number_of_pieces4 = fields.Char('片数(旧)')
    single_piece4 = fields.Char('单件(旧)')
    comment4 = fields.Char('备注')

    float_door_width4 = fields.Float(string="门幅(CM)")
    float_number_of_pieces4 = fields.Float(string="片数")
    float_single_piece4 = fields.Float(string="单件(CM)")


    # 配料1
    picture5 = fields.Image(string='图片')
    door_width5 = fields.Char('门幅(旧)')
    number_of_pieces5 = fields.Char('片数(旧)')
    single_piece5 = fields.Char('单件(旧)')
    comment5 = fields.Char('备注')

    float_door_width5 = fields.Float(string="门幅(CM)")
    float_number_of_pieces5 = fields.Float(string="片数")
    float_single_piece5 = fields.Float(string="单件(CM)")



    # 配料2
    picture6 = fields.Image(string='图片')
    door_width6 = fields.Char('门幅(旧)')
    number_of_pieces6 = fields.Char('片数(旧)')
    single_piece6 = fields.Char('单件(旧)')
    comment6 = fields.Char('备注')


    float_door_width6 = fields.Float(string="门幅(CM)")
    float_number_of_pieces6 = fields.Float(string="片数")
    float_single_piece6 = fields.Float(string="单件(CM)")


    @api.constrains('style_number')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ("style_number", "=", self.style_number.id),
            ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在款号为：{self.style_number.style_number}的记录了！")




class process_optimization(models.Model):
    _name = 'process.optimization'
    _description = '工艺优化方案'
    _rec_name = 'number_no'
    date = fields.Date('日期')
    group = fields.Char('组别')
    number_no = fields.Char('款号')
    optimize_process_and_process = fields.Char('优化工序及工艺')
    tools_and_equipment = fields.Char('工具及设备')
    is_it_optimized = fields.Char('是否已优化')
    working_hours_before = fields.Char('优化前工时')
    working_hours_after = fields.Char('优化后工时')
    efficiency_improvement = fields.Char('效率提升')
    person_in_charge = fields.Char('负责人')
    comment = fields.Char('备注')

