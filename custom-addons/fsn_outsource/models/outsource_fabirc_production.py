from odoo import models, fields, api

class OutsourceFabircProduction(models.Model):
    _name = 'outsource_fabirc_production'
    _description = 'FSN外发面辅料生产任务'
    _rec_name = 'voucher_number'
    _order = "date desc"


    date = fields.Date(string='日期', required=True)

    responsible_person = fields.Many2one("hr.employee", string="负责人", required=True)

    voucher_number = fields.Char(string="制单编号", required=True)

    style_number = fields.Many2one('ib.detail', string='款号', required=True)

    style_name = fields.Char(string="款式名称")

    place_order_date = fields.Date(string="下单日期")

    manufacturer = fields.Char(string="生产厂家")

    total_number = fields.Integer(string="总件数", compute="_value_total_number", store=True)

    note = fields.Char(string="备注")

    ofp_size_line_ids = fields.One2many("ofp_size_line", "ofp_id", string="尺码明细")

    ofp_material_line_ids = fields.One2many("ofp_material_line", "ofp_id", string="物料明细")

    verifier = fields.Char(string="审核", required=True)

    store_issue = fields.Char(string="发料", required=True)

    picking = fields.Char(string="领料", required=True)



    @api.depends('ofp_size_line_ids', 'ofp_size_line_ids.number')
    def _value_total_number(self):
        for record in self:
            record.total_number = sum(record.ofp_size_line_ids.mapped('number'))


class OfpSizeLine(models.Model):
    _name = 'ofp_size_line'
    _description = 'FSN外发面辅料生产任务尺码明细'


    ofp_id = fields.Many2one("outsource_fabirc_production", string="生产任务", ondelete="cascade")
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer(string="件数")



class OfpMaterialLine(models.Model):
    _name = 'ofp_material_line'
    _description = 'FSN外发面辅料生产任务物料明细'


    ofp_id = fields.Many2one("outsource_fabirc_production", string="生产任务", ondelete="cascade")
    material_properties = fields.Selection([('主料', '主料'), ('辅料', '辅料')], string="物料属性", required=True)
    fsn_color = fields.Many2one("fsn_color", string="颜色")
    material_number = fields.Char(string="物料编号")
    material_name = fields.Char(string="物料名称", required=True)
    material_color = fields.Many2one("fsn_color", string="物料颜色")
    specifications = fields.Char(string="门幅/规格")
    single_dosage = fields.Float(string="单件用量")
    unit = fields.Char(string="单位")
    loss = fields.Float(string="损耗（%）")
    accelerated = fields.Float(string="放量")
    plan_number = fields.Float(string="计划数量")
    actual_release_number = fields.Float(string="实发数量")
    note = fields.Char(string="备注")