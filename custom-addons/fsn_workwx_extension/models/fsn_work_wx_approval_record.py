from odoo import models, fields, api


class FsnWorkWxApprovalRecord(models.Model):
    _name = 'fsn_work_wx_approval_record'
    _description = 'FSN企业微信审批记录'
    _rec_name = 'sp_no'
    _order = "sp_no"


    sp_no = fields.Char(string="审批编号")
    sp_name = fields.Char(string="审批名称")
    template_id = fields.Char(string="模板ID")
    apply_time = fields.Char(string="申请时间")
    sp_status = fields.Selection([
        ('1', '审批中'),
        ('2', '已通过'),
        ('3', '已驳回'),
        ('4', '已撤销'),
        ('6', '通过后撤销'),
        ('7', '已删除'),
        ('10', '已支付'),
    ], string="审批状态")