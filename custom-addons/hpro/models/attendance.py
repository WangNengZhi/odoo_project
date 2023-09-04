import datetime
import time
#
from odoo import models, fields, api
from odoo.exceptions import ValidationError


#    统计表生成
class every_one_tongji(models.Model):

    _name = 'every.tongji'
    _description = '工种统计'
    date = fields.Date('日期')
    is_it_a_temporary_worker = fields.Selection([
        ('正式工(A级管理)', '正式工(A级管理)'),
        ('正式工(B级管理)', '正式工(B级管理)'),
        ('正式工(计件工资)', '正式工(计件工资)'),
        ('正式工(计时工资)', '正式工(计时工资)'),
        ('临时工', '临时工'),
        ('实习生', '实习生'),
        ('实习生(计件)', '实习生(计件)'),
        ('实习生(非计件)', '实习生(非计件)'),
        ('外包', '外包')
    ], string='工种')
    number = fields.Integer('人数')

    @api.model
    def create(self, val):
        demo = self.env['every.tongji'].sudo().search([('date', '=', val['date']), ('is_it_a_temporary_worker', '=', val['is_it_a_temporary_worker'])])
        if demo:
            demo.sudo().unlink()
        return super(every_one_tongji, self).create(val)


    def statistics(self):
        date = datetime.datetime.now() + datetime.timedelta(hours=8)
        demo = self.env['hr.employee'].sudo().search([('is_delete', '=', False)])
        #   未辞职的正式工    正式工(A级管理)
        wei_zheng1 = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', '=', '正式工(A级管理)')])
        #   未辞职的正式工     正式工(B级管理)
        wei_zheng2 = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', '=', '正式工(B级管理)')])
        #   未辞职的正式工      正式工(计件工资)
        wei_zheng3 = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', '=', '正式工(计件工资)')])

        #   未辞职的临时工
        wei_ling = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', '=', '临时工')])
        #   未辞职的实习生
        wei_shi = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', 'like', '实习生')])
        #   未辞职的外包
        wei_wai = self.env['hr.employee'].sudo().search(
            [('is_delete', '=', False), ('is_it_a_temporary_worker', 'like', '外包')])


        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '正式工(A级管理)',
            'number': len(wei_zheng1)
        })
        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '正式工(B级管理)',
            'number': len(wei_zheng2)
        })
        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '正式工(计件工资)',
            'number': len(wei_zheng3)
        })
        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '临时工',
            'number': len(wei_ling)
        })
        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '实习生',
            'number': len(wei_shi)
        })
        self.env['every.tongji'].sudo().create({
            'date': date,
            'is_it_a_temporary_worker': '外包',
            'number': len(wei_wai)
        })

