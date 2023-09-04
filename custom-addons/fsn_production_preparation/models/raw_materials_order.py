from odoo import models, fields, api
from odoo.exceptions import ValidationError



class SalePro(models.Model):
    """ 继承订单"""
    _inherit = 'sale_pro.sale_pro'

    raw_materials_order_id = fields.One2many("raw_materials_order", "order_number_id", tring="面辅料订单")

    # 生成面辅料订单
    def generate_raw_materials_order(self):
        for record in self:

            # 判断是否已经存在面辅料订单
            if not record.raw_materials_order_id:
                # 循环销售订单明细
                for sale_pro_line_obj in record.sale_pro_line_ids:
                    
                    raw_materials_order_home_obj = self.env['raw_materials_order_home'].sudo().search([("sale_pro_line_id", "=", sale_pro_line_obj.id)])
                    if not raw_materials_order_home_obj:
                        raw_materials_order_home_obj = self.env['raw_materials_order_home'].sudo().create({"sale_pro_line_id": sale_pro_line_obj.id})


                    # 查询单件用量表
                    sheet_materials_objs = self.env["sheet_materials"].sudo().search(
                        [("style_number", "=", sale_pro_line_obj.style_number.id), ("state", "=", "已审批")],
                    )
                    if sheet_materials_objs:

                        sheet_materials_obj = sheet_materials_objs[0]

                        if sale_pro_line_obj.style_number.id == sheet_materials_obj.style_number.id:
                            # 循环单件用料表明细
                            for sheet_materials_line in sheet_materials_obj.sheet_materials_line_ids:

                                print(sheet_materials_line.material_name, "-------------")

                                # 厘米进制转换
                                if sheet_materials_line.unit_id.name == "厘米":
                                    unit_id = self.env["fsn_unit"].sudo().search([("name", "=", "米")]).id
                                    single_dosage = sheet_materials_line.single_dosage / 100
                                else:
                                    unit_id = sheet_materials_line.unit_id.id
                                    single_dosage = sheet_materials_line.single_dosage

                                if sheet_materials_line.is_points_size:

                                    for voucher_details in sale_pro_line_obj.voucher_details:

                                        if voucher_details.size.id == sheet_materials_obj.size.id:

                                            raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                                "date": fields.Date.today(),    # 日期
                                                "order_number_id": record.id,   # 订单id
                                                "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                                "type": sheet_materials_line.type,   # 类型
                                                "material_name": sheet_materials_line.material_name,    # 物料名称
                                                "material_specifications": sheet_materials_line.material_specifications,  # 物料规格
                                                "single_dosage": single_dosage,    # 单件用量
                                                "unit_id": unit_id,  # 单位
                                                "order_number": voucher_details.number,    # 订单数量
                                                "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                            })
                                        else:

                                            raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                                "date": fields.Date.today(),    # 日期
                                                "order_number_id": record.id,   # 订单id
                                                "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                                "type": sheet_materials_line.type,   # 类型
                                                "material_name": sheet_materials_line.material_name,    # 物料名称
                                                "material_specifications": voucher_details.size.name,  # 物料规格
                                                "single_dosage": single_dosage,    # 单件用量
                                                "unit_id": unit_id,  # 单位
                                                "order_number": voucher_details.number,    # 订单数量
                                                "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                            })

                                else:
                                
                                    raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                        "date": fields.Date.today(),    # 日期
                                        "order_number_id": record.id,   # 订单id
                                        "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                        "type": sheet_materials_line.type,   # 类型
                                        "material_name": sheet_materials_line.material_name,    # 物料名称
                                        "material_specifications": sheet_materials_line.material_specifications,  # 物料规格
                                        "single_dosage": single_dosage,    # 单件用量
                                        "unit_id": unit_id,  # 单位
                                        "order_number": sale_pro_line_obj.voucher_count,    # 订单数量
                                        "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                    })
                        else:
                            for sheet_materials_line in sheet_materials_obj.sheet_materials_line_ids:

                                # 厘米进制转换
                                if sheet_materials_line.unit_id.name == "厘米":
                                    unit_id = self.env["fsn_unit"].sudo().search([("name", "=", "米")]).id
                                    single_dosage = sheet_materials_line.single_dosage / 100
                                else:
                                    unit_id = sheet_materials_line.unit_id.id
                                    single_dosage = sheet_materials_line.single_dosage

                                if sheet_materials_line.is_points_size:

                                    for voucher_details in sale_pro_line_obj.voucher_details:

                                        if voucher_details.size.id == sheet_materials_obj.size.id:

                                            raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                                "date": fields.Date.today(),    # 日期
                                                "order_number_id": record.id,   # 订单id
                                                "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                                "type": sheet_materials_line.type,   # 类型
                                                "material_name": sheet_materials_line.material_name,    # 物料名称
                                                "material_specifications": sheet_materials_line.material_specifications,  # 物料规格
                                                "single_dosage": single_dosage,    # 单件用量
                                                "unit_id": unit_id,  # 单位
                                                "order_number": voucher_details.number,    # 订单数量
                                                "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                            })
                                        else:

                                            raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                                "date": fields.Date.today(),    # 日期
                                                "order_number_id": record.id,   # 订单id
                                                "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                                "type": sheet_materials_line.type,   # 类型
                                                "material_name": sheet_materials_line.material_name,    # 物料名称
                                                "material_specifications": voucher_details.size.name,  # 物料规格
                                                "single_dosage": single_dosage,    # 单件用量
                                                "unit_id": unit_id,  # 单位
                                                "order_number": voucher_details.number,    # 订单数量
                                                "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                            })
                                else:

                                    raw_materials_order_obj = record.raw_materials_order_id.sudo().create({
                                        "date": fields.Date.today(),    # 日期
                                        "order_number_id": record.id,   # 订单id
                                        "style_number_id": sale_pro_line_obj.style_number.id,    # 款号
                                        "type": sheet_materials_line.type,   # 类型
                                        "material_name": sheet_materials_line.material_name,    # 物料名称
                                        "single_dosage": single_dosage,    # 单件用量
                                        "unit_id": unit_id,  # 单位
                                        "order_number": sale_pro_line_obj.voucher_count,    # 订单数量
                                        "raw_materials_order_home_id": raw_materials_order_home_obj.id
                                    })


                    else:
                        raise ValidationError(f"没有发现订单号:{record.order_number}，款号:{sale_pro_line_obj.style_number.style_number}下款式的单件用量!")
            else:
                raise ValidationError(f"已经存在该订单的面辅料订单了。")




class RawMaterialsOrderHome(models.Model):
    _name = "raw_materials_order_home"
    _description = '面辅料订单'
    _rec_name = "style_number_id"
    _order = "date desc"

    date = fields.Date(string="日期", default=fields.Date.today())
    sale_pro_line_id = fields.Many2one("sale_pro_line", string="订单明细", ondelete='restrict')
    order_number_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="sale_pro_line_id.sale_pro_id", store=True)
    style_number_id = fields.Many2one('ib.detail', string='款号', related="sale_pro_line_id.style_number", store=True)
    raw_materials_order_ids = fields.One2many("raw_materials_order", "raw_materials_order_home_id", string="面辅料订单明细")

class RawMaterialsOrder(models.Model):
    _name = "raw_materials_order"
    _description = '面辅料订单明细'
    _rec_name = "material_name"
    _order = "create_date desc"

    raw_materials_order_home_id = fields.Many2one("raw_materials_order_home", string="面辅料订单", ondelete="cascade")
    active = fields.Boolean(default=True)
    date = fields.Date(string="日期", required=True)
    state = fields.Selection([('草稿', '草稿'), ('通过', '通过'), ('拒绝', '拒绝')], string="状态", default="草稿")
    order_number_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    style_number_id = fields.Many2one('ib.detail', string='款号', required=True)
    type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'), 
        ], string="类型", required=True)
    material_name = fields.Char(string="物料名称", required=True)
    material_specifications = fields.Char(string="物料规格")
    single_dosage = fields.Float(string="单件用量")
    unit = fields.Char(string="单位")
    unit_id = fields.Many2one("fsn_unit", string="单位", required=True)
    order_number = fields.Float(string="订单数量")
    total_amount = fields.Float(string="总用量", compute="set_total_amount", store=True)
    @api.depends('single_dosage', 'order_number')
    def set_total_amount(self):
        for record in self:
            if record.order_number and record.single_dosage:
                record.total_amount = record.order_number * record.single_dosage

    def test(self):
        for record in self:
            
            sale_pro_line_obj = self.env['sale_pro_line'].sudo().search([('sale_pro_id', "=", record.order_number_id.id), ("style_number", "=", record.style_number_id.id)])
            print(sale_pro_line_obj)
            if sale_pro_line_obj:

                raw_materials_order_home_obj = self.env['raw_materials_order_home'].sudo().search([("sale_pro_line_id", "=", sale_pro_line_obj.id)])
                if not raw_materials_order_home_obj:
                    raw_materials_order_home_obj = self.env['raw_materials_order_home'].sudo().create({"sale_pro_line_id": sale_pro_line_obj.id})
            
                record.raw_materials_order_home_id = raw_materials_order_home_obj.id


    fabric_ingredients_procurement_id = fields.Many2one("fabric_ingredients_procurement", string="面辅料采购")


    # 确认弹窗
    def confirmation_button(self):
        button_type = self._context.get("type")
        name = ""
        if button_type == "fallback":
            name = "确认回退吗？"
        elif button_type == "through":
            name = "确认通过吗？"
        elif button_type == "refused":
            name = "确认拒绝吗？"
        action = {
            'name': name,
            'view_mode': 'form',
            'res_model': 'raw_materials_order',
            'view_id': self.env.ref('fsn_production_preparation.raw_materials_order_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

        return action

    # 状态改变
    def action_state_changes(self):
        button_type = self._context.get("type")

        if button_type == "fallback":
            self.state = "草稿"

            self.del_purchase()
        elif button_type == "refused":
            self.state = "拒绝"

            self.create_purchase()
        elif button_type == "through":
            self.state = "通过"

            self.create_purchase()


    # 删除面辅料采购
    def del_purchase(self):
        for record in self:

            if record.fabric_ingredients_procurement_id:
                if record.fabric_ingredients_procurement_id.state == "待审批":

                    record.fabric_ingredients_procurement_id.sudo().unlink()

                else:
                    raise ValidationError(f"面辅料采购已经审批通过！不可回退！")

    # 创建面辅料采购
    def create_purchase(self):
        for record in self:

            fabric_ingredients_procurement_id = self.env["fabric_ingredients_procurement"].sudo().create({
                "date": fields.Date.today(),    # 日期
                "type": record.type,    # 面辅料类型
                "order_id": record.order_number_id.id,     # 订单号
                "style_number": record.style_number_id.id,    # 款号
                "material_name": record.material_name,   # 物品名称
                "specification": record.material_specifications,    # 物品规格
                "amount": record.total_amount,  # 数量
                "unit": record.unit_id.name,    # 单位
                "raw_materials_order_id": record.id,    
            })

            record.fabric_ingredients_procurement_id = fabric_ingredients_procurement_id


    def unlink(self):

        for record in self:
            if record.state == "通过":

                raise ValidationError(f"已审批的记录, 不可删除！")

        res = super(RawMaterialsOrder, self).unlink()

        return res
    
