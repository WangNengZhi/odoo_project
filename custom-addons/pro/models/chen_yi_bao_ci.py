from odoo import models, fields, api

class ChenYiBaoCi(models.Model):
    _name = 'chen_yi_bao_ci'
    _description = '成衣报次单'
    _rec_name = 'data'
    _order = "data desc"

    wu_huan_pian_bu = fields.Boolean(string="无换布片")
    sunhuai_or_diushi = fields.Boolean(string="损坏/丢失")
    qve_shao_fu_liao = fields.Boolean(string="缺少辅料")
    remarks = fields.Text(string="备注")
    person_in_charge = fields.Char(string="负责人", required=True)
    data = fields.Date(string="日期", required=True)
    line_ids = fields.One2many("chen_yi_bao_ci_line", "chen_yi_bao_ci_id", string="成衣报次单明细")
    defective_products_sum = fields.Integer(string="次品总数", compute="_set_defective_products_sum", store=True)
    bao_ci_type = fields.Selection([('车间报次', '车间报次'), ('仓库报次', '仓库报次'), ('裁床报次', '裁床报次'), ('后道报次', '后道报次')], string="报次类型", required=True)

    # 计算次品总数
    @api.depends("line_ids")
    def _set_defective_products_sum(self):

        self.defective_products_sum = 0
        for line in self.line_ids:
            self.defective_products_sum = self.defective_products_sum + line.total


    def set_wdc(self):
        for record in self:
            for line in record.line_ids:
                line.set_style_number_summary()



class ChenYiBaoCiLine(models.Model):
    _name = 'chen_yi_bao_ci_line'
    _description = '成衣报次单明细'

    chen_yi_bao_ci_id = fields.Many2one("chen_yi_bao_ci", ondelete="cascade")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    color = fields.Char('颜色')

    size_xs = fields.Integer(string='XS')
    size_s = fields.Integer(string='S')
    size_m = fields.Integer(string='M')
    size_l = fields.Integer(string='L')
    size_xl = fields.Integer(string='XL')
    size_xxl = fields.Integer(string='XXL')
    size_xxxl = fields.Integer(string='XXXL')
    total = fields.Integer(string="合计", compute="_set_total", store=True)

    # 计算合计
    @api.depends('size_xs', 'size_s', 'size_m', 'size_l', 'size_xl', 'size_xxl', 'size_xxxl')
    def _set_total(self):

        for record in self:

            record.total = record.size_xs + record.size_s + record.size_m + record.size_l + record.size_xl + record.size_xxl + record.size_xxxl


    @api.model
    def create(self, vals):

        res = super(ChenYiBaoCiLine, self).create(vals)

        return res



