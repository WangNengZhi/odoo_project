from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductDesign(models.Model):
    _name = 'product_design'
    _description = '产品设计'
    _rec_name = 'design_number'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    design_number = fields.Char(string="设计编号")
    design_type = fields.Selection([('自主设计', '自主设计'), ('半设计', '半设计')], string="设计类型", required=True)
    designer_id = fields.Many2one('hr.employee', string='设计人', required=True)
    design_attachment_ids = fields.Many2many('ir.attachment', string="设计附件")
    design_image = fields.Image(string="设计图片", required=True)
    surface_material_cost = fields.Float(string="面辅料成本", required=True)
    fabric_composition = fields.Char(string="面料成分", required=True)
    selling_point = fields.Text(string="卖点", required=True)
    state = fields.Selection([('草稿', '草稿'), ('已审批', '已审批')], string="状态", default="草稿")


    def action_approval_operation(self):

        print(self.env.context)
        if self.env.context.get("type") == "through":
            self.state = "已审批"
        elif self.env.context.get("type") == "rollback":
            self.state = "草稿"
            


    @api.model
    def create(self, vals):


        vals['design_number'] = f"1{self.env['ir.sequence'].next_by_code('product_design_sequence')}"
        
        return super(ProductDesign, self).create(vals)

    # 检查数据唯一性
    @api.constrains('design_number')
    def _check_unique(self):
        if self.env[self._name].search_count([('design_number', '=', self.design_number)]) > 1:
            raise ValidationError(f"已经存在设计编号为{self.design_number}的记录了！设计编号不可重复！")
        


    def test(self):
        for i in self:
            i.design_number = f"1{i.design_number}"