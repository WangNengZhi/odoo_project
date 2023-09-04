from odoo import models, fields, api

class OutsourceSurfaceMaterial(models.Model):
    _name = 'outsource_surface_material'
    _description = 'FSN外发面里料订单'
    # _rec_name = 'order_number'
    # _order = "date desc"


    date = fields.Date('日期', required=True)

    verifier = fields.Char(string="审核", required=True)

    store_issue = fields.Char(string="发料", required=True)

    picking = fields.Char(string="领料", required=True)

    announcements = fields.Text(string="注意事项")

    osm_style_info_ids = fields.One2many("osm_style_info", "outsource_surface_material_id", string="款式明细")

    osm_size_info = fields.One2many("osm_size_info", "outsource_surface_material_id", string="尺码明细")



class OsmStyleInfo(models.Model):
    _name = 'osm_style_info'
    _description = 'FSN外发面里料订单款式明细'


    outsource_surface_material_id = fields.Many2one("outsource_surface_material", string="面里料订单", ondelete="cascade")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    cgmlms = fields.Float(string="采购面料米数")
    ssxsms = fields.Float(string="缩水（洗水）米数")
    mldhyl = fields.Float(string="面料单耗用量")
    psdhyl = fields.Float(string="配色单耗用量")
    ncdhyl = fields.Float(string="粘衬单耗用量")
    cutting_ratio = fields.Float(string="裁剪比例")
    residue_cloth = fields.Float(string="剩余布料")



class OsmSizeInfo(models.Model):
    _name = 'osm_size_info'
    _description = 'FSN外发面里料订单尺码明细'


    outsource_surface_material_id = fields.Many2one("outsource_surface_material", string="面里料订单", ondelete="cascade")
    fsn_color = fields.Many2one("fsn_color", string="颜色", required=True)
    size = fields.Many2one("fsn_size", string="尺码", required=True)
    predict_cut_number = fields.Float(string="预计裁剪数量")
    practical_cut_number = fields.Float(string="实际裁剪数量")





