from odoo import models, fields, api

class MianFuLiaoBuLiao(models.Model):
    _name = 'mian_fu_liao_bu_liao'
    _description = '面辅料补料单'
    _rec_name = 'datetime'
    _order = "datetime desc"

    datetime = fields.Date(string="日期", required=True)
    branch_factory = fields.Char(string="分厂")
    department = fields.Many2one('hr.department', string="部门", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    person_in_charge = fields.Char(string="负责人", required=True)
    bu_liao_reason = fields.Text(string="补料原因")
    line_ids = fields.One2many("mian_fu_liao_bu_liao_line", "mian_fu_liao_bu_liao_id", string="面辅料补料单明细")
    repair_material_sum = fields.Integer(string="次品总数", compute="_set_repair_material_sum", store=True)


    # 计算次品总数
    @api.depends("line_ids")
    def _set_repair_material_sum(self):

        for obj in self:

            tem_repair_material_sum = 0
            for line in obj.line_ids:
                tem_repair_material_sum = tem_repair_material_sum + line.total
            
            obj.sudo().write({
                "repair_material_sum": tem_repair_material_sum
            })



class MianFuLiaoBuLiaoLine(models.Model):
    _name = 'mian_fu_liao_bu_liao_line'
    _description = '面辅料补料单明细'

    mian_fu_liao_bu_liao_id = fields.Many2one("mian_fu_liao_bu_liao")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    color = fields.Char('颜色', compute="_set_color", store=True)
    material_science = fields.Selection([('面料', '面料'), ('辅料', '辅料')], string="面料/辅料")
    specifications = fields.Char(string="规格")

    size_xs = fields.Integer(string='XS')
    size_s = fields.Integer(string='S')
    size_m = fields.Integer(string='M')
    size_l = fields.Integer(string='L')
    size_xl = fields.Integer(string='XL')
    size_xxl = fields.Integer(string='XXL')
    size_xxxl = fields.Integer(string='XXXL')
    total = fields.Integer(string="合计", compute="_set_total", store=True)

    # 设置颜色
    @api.depends('style_number')
    def _set_color(self):

        for record in self:

            record.color = record.style_number.color


    # 计算合计
    @api.depends('size_xs', 'size_s', 'size_m', 'size_l', 'size_xl', 'size_xxl', 'size_xxxl')
    def _set_total(self):

        for record in self:

            record.total = record.size_xs + record.size_s + record.size_m + record.size_l + record.size_xl + record.size_xxl + record.size_xxxl
