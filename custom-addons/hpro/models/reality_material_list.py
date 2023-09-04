# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class RealityMaterialList(models.Model):
    _name = 'reality_material_list'
    _description = '实际用料表'
    _rec_name = 'name'
    

    name = fields.Char(related='order_number.name', string='客户')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    size = fields.Char(string='尺码', required=True)

    # 面料
    picture = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)



    # 里料
    picture1 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment1 = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width1 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces1 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece1 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)



    # 胆布
    picture2 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment2 = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width2 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces2 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece2 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)



    # 棉
    picture3 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment3 = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width3 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces3 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece3 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)


    # 粘衬
    picture4 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment4 = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width4 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces4 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece4 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)


    # 配料1
    picture5 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment5 = fields.Char('备注', compute="_set_fabric_messages", store=True)

    float_door_width5 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces5 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece5 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)



    # 配料2
    picture6 = fields.Image(string='图片', compute="_set_fabric_messages", store=True)
    comment6 = fields.Char('备注', compute="_set_fabric_messages", store=True)


    float_door_width6 = fields.Float(string="门幅(CM)", compute="_set_fabric_messages", store=True)
    float_number_of_pieces6 = fields.Float(string="片数", compute="_set_fabric_messages", store=True)
    float_single_piece6 = fields.Float(string="单件(CM)", compute="_set_fabric_messages", store=True)


    @api.constrains('style_number')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ("style_number", "=", self.style_number.id),
            ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在款号为：{self.style_number.style_number}的记录了！")


    @api.depends('style_number')
    def _set_fabric_messages(self):
        for obj in self:
            
            mater_maters_objs = self.env["mater.maters"].sudo().search([("style_number", "=", obj.style_number.id)])

            obj.write({
                "picture": mater_maters_objs.picture,
                "float_door_width": obj.style_number.s_totle * mater_maters_objs.float_door_width,
                "float_number_of_pieces": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces,
                "float_single_piece": obj.style_number.s_totle * mater_maters_objs.float_single_piece,
                "comment": mater_maters_objs.comment,

                "picture1": mater_maters_objs.picture1,
                "float_door_width1": obj.style_number.s_totle * mater_maters_objs.float_door_width1,
                "float_number_of_pieces1": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces1,
                "float_single_piece1": obj.style_number.s_totle * mater_maters_objs.float_single_piece1,
                "comment1": mater_maters_objs.comment1,

                "picture2": mater_maters_objs.picture2,
                "float_door_width2": obj.style_number.s_totle * mater_maters_objs.float_door_width2,
                "float_number_of_pieces2": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces2,
                "float_single_piece2": obj.style_number.s_totle * mater_maters_objs.float_single_piece2,
                "comment2": mater_maters_objs.comment2,

                "picture3": mater_maters_objs.picture3,
                "float_door_width3": obj.style_number.s_totle * mater_maters_objs.float_door_width3,
                "float_number_of_pieces3": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces3,
                "float_single_piece3": obj.style_number.s_totle * mater_maters_objs.float_single_piece3,
                "comment3": mater_maters_objs.comment3,

                "picture4": mater_maters_objs.picture4,
                "float_door_width4": obj.style_number.s_totle * mater_maters_objs.float_door_width4,
                "float_number_of_pieces4": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces4,
                "float_single_piece4": obj.style_number.s_totle * mater_maters_objs.float_single_piece4,
                "comment4": mater_maters_objs.comment4,

                "picture5": mater_maters_objs.picture5,
                "float_door_width5": obj.style_number.s_totle * mater_maters_objs.float_door_width5,
                "float_number_of_pieces5": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces5,
                "float_single_piece5": obj.style_number.s_totle * mater_maters_objs.float_single_piece5,
                "comment5": mater_maters_objs.comment5,

                "picture6": mater_maters_objs.picture6,
                "float_door_width6": obj.style_number.s_totle * mater_maters_objs.float_door_width6,
                "float_number_of_pieces6": obj.style_number.s_totle * mater_maters_objs.float_number_of_pieces6,
                "float_single_piece6": obj.style_number.s_totle * mater_maters_objs.float_single_piece6,
                "comment6": mater_maters_objs.comment6,
            })


