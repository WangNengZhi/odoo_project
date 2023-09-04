from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ManufacturingOrderLine(models.Model):
    _name = 'manufacturing_order_line'
    _description = 'FSN生产工单明细'
    _rec_name = 'style_number'
    _order = "style_number desc"


    # 设置line_ids的默认值
    def _set_line_ids(self):
        sample_ids = self.env["manufacturing_bom_default"].search([])

        lines = []

        for sample_id in sample_ids:
            line = {
                "name": sample_id.name,      # 物料名称
                "type": sample_id.type,     # 物料类型
                "quantity_demanded": sample_id.quantity_demanded,   # 需求量
                "unit_price": sample_id.unit_price,     # 单价
            }
            lines.append((0, 0, line))

        return lines



    manufacturing_order = fields.Many2one("manufacturing_order", string="生产工单", ondelete="cascade")
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    size = fields.Many2one("fsn_size", string="尺码")
    number = fields.Float(string="件数")
    state = fields.Selection([('草稿', '草稿'), ('确认', '确认'), ('作废', '作废')], string="状态", default="草稿", required=True)
    price = fields.Float(string="价格", compute="_value_price", store=True, digits=(16, 5))

    manufacturing_bom_ids = fields.One2many("manufacturing_bom", "manufacturing_order_line_id", string="物料清单", default=_set_line_ids)

    manufacturing_special_process_ids = fields.One2many("manufacturing_special_process", "manufacturing_order_line_id", string="特殊工艺")


    # 计算价格
    @api.depends('manufacturing_bom_ids', 'manufacturing_bom_ids.price', 'manufacturing_special_process_ids', 'manufacturing_special_process_ids.price')
    def _value_price(self):
        for record in self:
            record.price = sum(self.manufacturing_bom_ids.mapped('price')) + sum(self.manufacturing_special_process_ids.mapped('price'))



    # 状态 前进
    def action_forward(self):
        if self.state == "草稿":

            if self.manufacturing_bom_ids or self.manufacturing_special_process_ids:
                pass
            else:
                raise ValidationError(f"没有检测到任何的物料清单或特殊工艺，不可确认！")


            not_ready_objs_list = list(filter(lambda manufacturing_bom: manufacturing_bom.quantity_demanded != manufacturing_bom.reserved_amount, self.manufacturing_bom_ids))

            not_process_ready_objs_list = list(filter(lambda manufacturing_special_process: manufacturing_special_process.quantity_demanded != manufacturing_special_process.reserved_amount, self.manufacturing_special_process_ids))

            if not_ready_objs_list or not_process_ready_objs_list:
                raise ValidationError(f"检测到物料或特殊工艺没有备齐，不可开始！")
            else:
                self.state = "确认"


    # 作废
    def action_cancellatio(self):

        self.state = "作废"







    def action_open_form(self):

        action = {
            'name': "生产工单明细",
            'view_mode': 'form',
            'res_model': 'manufacturing_order_line',
            'view_id': self.env.ref('fsn_production.manufacturing_order_line_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': dict(self._context),
            'target': 'new'
        }

        return action



