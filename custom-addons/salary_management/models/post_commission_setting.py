from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PostCommissionSetting(models.Model):
    _name = 'post_commission_setting'
    _description = 'FSN岗位提成设置'
    _rec_name = 'job_id'
    # _order = "date desc"


    job_id = fields.Many2one('hr.job', string='岗位', required=True)
    frequency_distribution = fields.Integer(string="发放频率（每几个月一次发放一次）")
    starting_month = fields.Char(string="启始月份", required=True)
    commission_type = fields.Selection([
        ('裁床产值','裁床产值'),
        ('后道产值','后道产值'),
        ('工厂','工厂'),
        ('外发','外发'),
        ('工厂和外发','工厂和外发'),
        ('外发(按订单属性)','外发(按订单属性)'),
    ], string='提成类型', required=True)
    commission_ratio = fields.Float(string="提成比例")

    post_commission_setting_line_ids = fields.One2many("post_commission_setting_line", "post_commission_setting_id", string="FSN岗位提成设置明细")

    @api.constrains('job_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('job_id', '=', record.job_id.id)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在该岗位的提成设置了！")



    
    def add_post_commission_setting_line_ids(self):
        ''' 添加提成明细'''
        for record in self:
            
            order_attribute_objs_ids = self.env['order_attribute'].sudo().search([]).ids

            lines = []

            for order_attribute_id in list(set(order_attribute_objs_ids) ^ set(record.post_commission_setting_line_ids.mapped("order_attribute_id").ids)):

                lines.append((0, 0, {"order_attribute_id": order_attribute_id}))
            
            record.post_commission_setting_line_ids = lines


class PostCommissionSettingLine(models.Model):
    _name = 'post_commission_setting_line'
    _description = 'FSN岗位提成设置明细'
    _rec_name = 'order_attribute_id'


    post_commission_setting_id = fields.Many2one("post_commission_setting", string="FSN岗位提成设置", ondelete="cascade")
    order_attribute_id = fields.Many2one("order_attribute", string="订单属性", required=True)
    commission_amount = fields.Float(string="提成金额")


    @api.constrains('job_id')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('order_attribute_id', '=', record.order_attribute_id.id)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在该订单属性的提成设置了！")


    