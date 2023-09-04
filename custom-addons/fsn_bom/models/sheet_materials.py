from odoo.exceptions import ValidationError
from odoo import models, fields, api

class SheetMaterials(models.Model):
    _name = 'sheet_materials'
    _description = '单件用料表'
    _rec_name = 'style_number'
    _order = 'date desc'
    
    date = fields.Date(string="日期", required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单编号')
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    style_number_base = fields.Char(string="款号前缀", related="style_number.style_number_base", store=True)
    product_name = fields.Char(string="品名", required=True)
    client_id = fields.Many2one("fsn_customer", string="客户", store=True)
    size = fields.Many2one("fsn_size", string="尺码", store=True, required=True)
    employee_id = fields.Many2one('hr.employee', string="负责人", required=True)
    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")
    # 审批通过
    def through(self):
        for record in self:
            if record.state == "待审批":
                record.state = "已审批"
    # 回退
    def fallback(self):
        for record in self:
            if record.state == "已审批":
                record.state = "待审批"

    # 面料
    picture = fields.Image(string='图片')
    comment = fields.Char('备注')

    float_door_width = fields.Float(string="门幅(CM)")
    float_number_of_pieces = fields.Float(string="片数")
    float_single_piece = fields.Float(string="单件(CM)")

    fabric_shrink = fields.Float(string="缩水米数（米）")
    fabric_documents_dosage = fields.Float(string="面料单耗用量（米）")
    color_documents_dosage = fields.Float(string="配色单耗用量（米）")
    adhesive_lining_dosage = fields.Float(string="粘衬单耗用量（米）")
    cutting_ratio = fields.Float(string="裁剪比例")
    remaining_cloth = fields.Float(string="剩余布料（米）")



    # 里料
    picture1 = fields.Image(string='图片')
    comment1 = fields.Char('备注')

    float_door_width1 = fields.Float(string="门幅(CM)")
    float_number_of_pieces1 = fields.Float(string="片数")
    float_single_piece1 = fields.Float(string="单件(CM)")

    fabric_shrink1 = fields.Float(string="缩水米数（米）")
    fabric_documents_dosage1 = fields.Float(string="面料单耗用量（米）")
    color_documents_dosage1 = fields.Float(string="配色单耗用量（米）")
    adhesive_lining_dosage1 = fields.Float(string="粘衬单耗用量（米）")
    cutting_ratio1 = fields.Float(string="裁剪比例")
    remaining_cloth1 = fields.Float(string="剩余布料（米）")


    # 胆布
    picture2 = fields.Image(string='图片')
    comment2 = fields.Char('备注')

    float_door_width2 = fields.Float(string="门幅(CM)")
    float_number_of_pieces2 = fields.Float(string="片数")
    float_single_piece2 = fields.Float(string="单件(CM)")



    # 棉
    picture3 = fields.Image(string='图片')
    comment3 = fields.Char('备注')

    float_door_width3 = fields.Float(string="门幅(CM)")
    float_number_of_pieces3 = fields.Float(string="片数")
    float_single_piece3 = fields.Float(string="单件(CM)")


    # 粘衬
    picture4 = fields.Image(string='图片')
    comment4 = fields.Char('备注')

    float_door_width4 = fields.Float(string="门幅(CM)")
    float_number_of_pieces4 = fields.Float(string="片数")
    float_single_piece4 = fields.Float(string="单件(CM)")


    # 配料1
    picture5 = fields.Image(string='图片')
    comment5 = fields.Char('备注')

    float_door_width5 = fields.Float(string="门幅(CM)")
    float_number_of_pieces5 = fields.Float(string="片数")
    float_single_piece5 = fields.Float(string="单件(CM)")



    # 配料2
    picture6 = fields.Image(string='图片')
    comment6 = fields.Char('备注')


    float_door_width6 = fields.Float(string="门幅(CM)")
    float_number_of_pieces6 = fields.Float(string="片数")
    float_single_piece6 = fields.Float(string="单件(CM)")



    def _set_line_ids(self):
        material_preset_ids = self.env["material_preset"].search([])

        lines = []

        for material_preset_id in material_preset_ids:
            line = {
                "type": material_preset_id.type,      # 类别
                "material_name_list_id": material_preset_id.material_name_list_id.id,   # 物料名称
                # "material_name": material_preset_id.name,   # 物料名称
                "unit": material_preset_id.unit,     # 单位
                "unit_id": material_preset_id.unit_id.id,   # 单位
                "single_dosage": 1,     # 单件用量
                "is_points_size": material_preset_id.is_size,  # 是否分尺码
                "is_must": True     # 必须
            }
            lines.append((0, 0, line))

        return lines


    sheet_materials_line_ids = fields.One2many("sheet_materials_line", "sheet_materials_id", string="单件用料明细", default=_set_line_ids, copy=True)

    @api.onchange('size')
    def set_line_material_specifications(self):
        for ling_obj in self.sheet_materials_line_ids:
            if ling_obj.is_points_size:
                ling_obj.material_specifications = self.size.name



    def write(self, vals):

        for record in self:
            if record.state == "已审批":
                if ("state" in vals) and len(vals) == 1:
                    pass
                else:

                    raise ValidationError(f"已审批的记录, 不可编辑！")


        res = super(SheetMaterials, self).write(vals)

        return res


    def unlink(self):

        for record in self:
            if record.state == "已审批":

                raise ValidationError(f"已审批的记录, 不可删除！")

        res = super(SheetMaterials, self).unlink()

        return res




class SheetMaterialsLine(models.Model):
    _name = 'sheet_materials_line'
    _description = '单件用料明细'
    _rec_name = 'material_name'


    sheet_materials_id = fields.Many2one("sheet_materials", string="单件用料表", ondelete="cascade")
    style_number_base = fields.Char(string="款号前缀", related="sheet_materials_id.style_number_base", store=True)
    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'), 
        ], string="类型", required=True)
    material_name_list_id = fields.Many2one("material_name_list", string="物料名称", required=True)
    material_name = fields.Char(string="物料名称", compute="set_material_name", store=True)
    @api.depends("material_name_list_id", "material_name_list_id.name")
    def set_material_name(self):
        for record in self:
            if record.material_name_list_id:
                record.material_name = record.material_name_list_id.name
            else:
                record.material_name = False
    material_specifications = fields.Char(string="物料规格（颜色、尺码等）", required=True)
    single_dosage = fields.Float(string="单件用量")
    unit = fields.Char(string="单位")
    unit_id = fields.Many2one("fsn_unit", string="单位", required=True)

    is_must = fields.Boolean(string="是否预设")
    is_points_size = fields.Boolean(string="是否分尺码")


    # 确认弹窗
    def confirm_deletion(self):

        action = {

            'name': "确认执行此操作吗",
            'view_mode': 'form',
            'res_model': 'sheet_materials_line',
            'view_id': self.env.ref('fsn_bom.sheet_materials_line_del_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

        return action