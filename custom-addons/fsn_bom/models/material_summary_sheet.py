from odoo.exceptions import ValidationError
from odoo import models, fields, api
from decimal import Decimal

class PracticalMaterial(models.Model):
    _name = 'material_summary_sheet'
    _description = '物料汇总'
    _rec_name = 'material_name'
    _order = 'date_order desc'

    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    date_order = fields.Date(string="下单日期", related="order_id.date", store=True)
    date_contract = fields.Date(string="合同日期", related="order_id.customer_delivery_time", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    order_quantity = fields.Integer(string="订单数量")
    material_name = fields.Char(string="物料名称")
    material_type = fields.Selection([
        ('面料', '面料'),
        ('辅料', '辅料'),
        ('特殊工艺', '特殊工艺'),
    ], string="物料类型")

    plan_dosage = fields.Float(string="计划用量")
    actual_dosage = fields.Float(string="采购用量")
    actual_usage = fields.Float(string='实际用量')
    dosage_difference = fields.Float(string="用量差异", compute="set_dosage_difference", store=True)
    @api.depends('plan_dosage', 'actual_dosage')
    def set_dosage_difference(self):
        for record in self:
            if record.actual_dosage:
                record.dosage_difference = (record.plan_dosage - record.actual_dosage) / record.actual_dosage
            else:
                record.dosage_difference = 0

    inventory_dosage = fields.Float(string="库存量")
    outbound_dosage = fields.Float(string="出库量")
    enter_dosage = fields.Float(string="入库量")

    return_goods_dosage = fields.Float(string="退货量")

    unit = fields.Char(string="单位")
    unit_price = fields.Float(string="单价", digits=(16, 3))


    plan_money_sum = fields.Float(string="计划金额", compute="set_plan_money_sum", store=True, digits=(16, 3))
    @api.depends('plan_dosage', 'unit_price')
    def set_plan_money_sum(self):
        for record in self:

            record.plan_money_sum = record.plan_dosage * record.unit_price
    actual_money_sum = fields.Float(string="实际金额", compute="_set_money_sum", store=True, digits=(16, 3))
    @api.depends('actual_dosage', 'unit_price')
    def set_actual_money_sum(self):
        for record in self:

            record.actual_money_sum = record.actual_dosage * record.unit_price

    tax = fields.Float(string="税点", digits=(16, 10))
    plan_after_tax_amount = fields.Float(string="计划税后金额", compute="set_plan_after_tax_amount", store=True, digits=(16, 3))
    @api.depends('plan_money_sum', 'tax')
    def set_plan_after_tax_amount(self):
        for record in self:
            if record.tax:
                record.plan_after_tax_amount = record.plan_money_sum * (1 + record.tax)
            else:
                record.plan_after_tax_amount = record.plan_money_sum

    actual_after_tax_amount = fields.Float(string="实际税后金额", compute="set_actual_after_tax_amount", store=True, digits=(16, 3))
    @api.depends('actual_money_sum', 'tax')
    def set_actual_after_tax_amount(self):
        for record in self:
            if record.tax:
                record.actual_after_tax_amount = record.actual_money_sum * (1 + record.tax)
            else:
                record.actual_after_tax_amount = record.actual_money_sum

    state = fields.Selection([
        ('已确认', '已确认'),
        ('未确认', '未确认')
    ], string="状态", default="未确认")

    def confirm(self):
        for record in self:
            if record.state != "已确认":
                record.state = "已确认"
            else:
                raise ValidationError(f"已经是已确认状态了，无需再已确认！")

    def back(self):
        for record in self:
            if record.state != "未确认":
                record.state = '未确认'
            else:
                raise ValidationError(f"已经是未确认状态了，无需再未确认！")

    # 刷新
    # def refresh_material_summary_sheet(self):
    #
    #     practical_material_objs = self.env["practical_material"].sudo().search([("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)])
    #     for practical_material_ob in practical_material_objs:
    #
    #         # 查询仓库更新实际用量
    #         stocks = self.env['finished_inventory'].search([('style_number', '=', practical_material_ob.style_number.id)])
    #         for stock in stocks:
    #             styles = self.env['sheet_materials_line'].search([('sheet_materials_id.style_number', '=', stock.style_number.id)])
    #             for s in styles:
    #                 result = s.single_dosage * stock.stock
    #
    #         if practical_material_ob.type == "面料":
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_outbound"].search([("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_inventory"].search([("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #         else:
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_outbound"].search([("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_inventory"].search([("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", practical_material_ob.order_id.id),
    #             ("style_number", "=", practical_material_ob.style_number.id),
    #             ("material_name", "=", practical_material_ob.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": "",
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": practical_material_ob.order_id.id,
    #                 "style_number": practical_material_ob.style_number.id,
    #                 "material_name": practical_material_ob.material_name,
    #                 "material_type":  practical_material_ob.type,
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": "",
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #
    #
    #
    #     raw_materials_order_objs = self.env["raw_materials_order"].sudo().search([("order_number_id", "!=", False), ("style_number_id", "!=", False)])
    #     for raw_materials_order_obj in raw_materials_order_objs:
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", raw_materials_order_obj.order_number_id.id),
    #             ("style_number", "=", raw_materials_order_obj.style_number_id.id),
    #             ("material_name", "=", raw_materials_order_obj.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": raw_materials_order_obj.order_number_id.id,
    #                 "style_number": raw_materials_order_obj.style_number_id.id,
    #                 "material_name": raw_materials_order_obj.material_name,
    #                 "material_type": raw_materials_order_obj.type,
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })

    # def refresh_material_summary_sheet(self):
    #     practical_material_objs = self.env["practical_material"].sudo().search(
    #         [("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)])
    #     for practical_material_ob in practical_material_objs:
    #         stocks = self.env['finished_inventory'].search(
    #             [('style_number', '=', practical_material_ob.style_number.id),
    #              ('order_number', '=', practical_material_ob.order_id.id)])
    #         result = sum(stock.stock for stock in stocks)  # 计算stock.stock的累加和
    #
    #         styles = self.env['sheet_materials_line'].search(
    #             [('sheet_materials_id.style_number', '=', practical_material_ob.style_number.id),
    #              ('sheet_materials_id.order_number', '=', practical_material_ob.order_id.id)])
    #         cumulative_multiplier = 1  # 初始化累积乘法器
    #         for s in styles:
    #             cumulative_multiplier *= s.single_dosage
    #
    #         # 在循环结束后应用累积乘法器
    #         result *= cumulative_multiplier
    #
    #         # 在循环结束后应用累积乘法器
    #         result *= cumulative_multiplier
    #
    #         if practical_material_ob.type == "面料":
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_outbound"].search(
    #                 [("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in
    #                                    self.env["plus_material_inventory"].search([(
    #                                        "material_coding.material_code",
    #                                        "=",
    #                                        practical_material_ob.material_code.id)]))
    #         else:
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_outbound"].search(
    #                 [("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in
    #                                    self.env["warehouse_bom_inventory"].search([(
    #                                        "material_coding.material_code",
    #                                        "=",
    #                                        practical_material_ob.material_code.id)]))
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", practical_material_ob.order_id.id),
    #             ("style_number", "=", practical_material_ob.style_number.id),
    #             ("material_name", "=", practical_material_ob.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": practical_material_ob.order_id.id,
    #                 "style_number": practical_material_ob.style_number.id,
    #                 "material_name": practical_material_ob.material_name,
    #                 "material_type": practical_material_ob.type,
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #
    #     raw_materials_order_objs = self.env["raw_materials_order"].sudo().search(
    #         [("order_number_id", "!=", False), ("style_number_id", "!=", False)])
    #     for raw_materials_order_obj in raw_materials_order_objs:
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", raw_materials_order_obj.order_number_id.id),
    #             ("style_number", "=", raw_materials_order_obj.style_number_id.id),
    #             ("material_name", "=", raw_materials_order_obj.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": raw_materials_order_obj.order_number_id.id,
    #                 "style_number": raw_materials_order_obj.style_number_id.id,
    #                 "material_name": raw_materials_order_obj.material_name,
    #                 "material_type": raw_materials_order_obj.type,
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #
    #     return True

    def refresh_material_summary_sheet(self):
        practical_material_objs = self.env["practical_material"].sudo().search([
            ("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)
        ])#实际用量表里查询

        material_results = {}  # 存储每个面料的实际用量结果

        for practical_material_ob in practical_material_objs:
            result = 0  # 初始化结果变量

            # 查询成品仓库更新实际用量
            stocks = self.env['finished_inventory'].search([
                ('style_number', '=', practical_material_ob.style_number.id),
                ('order_number', '=', practical_material_ob.order_id.id)
            ])
            result = sum(stock.stock for stock in stocks)  # 计算stock.stock的累加和
            #print(stocks.order_number.order_number)
            # 获取相应的sheet_materials_line用于款号(style_number)和物料名称(material_name)
            styles = self.env['sheet_materials_line'].search([
                ('sheet_materials_id.style_number.style_number_base', '=',
                 practical_material_ob.style_number.style_number_base),
                ('material_name', '=', practical_material_ob.material_name)
            ])
            if styles:
                result *= styles[0].single_dosage  # 将结果乘以sheet_materials_line的single_dosage
            # if practical_material_ob.order_id.order_number == "2302014":
            #     print("得到数据啦",styles[0].single_dosage,practical_material_ob.material_name,result)
            # 将每个材料的result值存储在material_results字典中
            material_results[practical_material_ob.material_name] = result

            if practical_material_ob.type == "面料":
                outbound_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_outbound"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id)
                ]))
                inventory_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_inventory"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id)
                ]))
                enter_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_enter"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id),('consigner', '!=', '风丝袅')
                ]))
            else:
                outbound_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_outbound"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id)
                ]))
                inventory_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_inventory"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id)
                ]))
                enter_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom"].search([
                    ("material_coding.material_code", "=", practical_material_ob.material_code.id),('consigner', '!=', '风丝袅')
                ]))

            material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
                ("order_id", "=", practical_material_ob.order_id.id),
                ("style_number", "=", practical_material_ob.style_number.id),
                ("material_name", "=", practical_material_ob.material_name)
            ])
            data = {
                "actual_dosage": practical_material_ob.amount,
                "actual_usage": result,
                "unit": practical_material_ob.unit,
                "unit_price": practical_material_ob.unit_price,
                "outbound_dosage": outbound_number,
                "inventory_dosage": inventory_number,
                "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
            }
            if material_summary_sheet_obj:
                material_summary_sheet_obj.sudo().write({
                    "actual_dosage": practical_material_ob.amount + (practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0),
                    "actual_usage": result,
                    "unit": practical_material_ob.unit,
                    "unit_price": practical_material_ob.unit_price,
                    "outbound_dosage": outbound_number,
                    "inventory_dosage": inventory_number,
                    "enter_dosage": enter_number,
                    'actual_money_sum': practical_material_ob.amount * practical_material_ob.unit_price,
                    "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
                })
            else:
                self.env["material_summary_sheet"].sudo().create({
                    "order_id": practical_material_ob.order_id.id,
                    "style_number": practical_material_ob.style_number.id,
                    "material_name": practical_material_ob.material_name,
                    "material_type": practical_material_ob.type,
                    "actual_dosage": practical_material_ob.amount + (practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0),
                    "actual_usage": result,
                    "unit": practical_material_ob.unit,
                    "unit_price": practical_material_ob.unit_price,
                    "outbound_dosage": outbound_number,
                    "inventory_dosage": inventory_number,
                    "enter_dosage": enter_number,
                    "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
                })

        # 更新实际用量
        # for material_name, actual_usage in material_results.items():
        #     material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
        #         ("material_name", "=", material_name)
        #     ])
        #     if material_summary_sheet_obj:
        #         material_summary_sheet_obj.sudo().write({
        #             "actual_usage": actual_usage
        #         })

        raw_materials_order_objs = self.env["raw_materials_order"].sudo().search([
            ("order_number_id", "!=", False), ("style_number_id", "!=", False)
        ])#面辅料订单明细里查询
        for raw_materials_order_obj in raw_materials_order_objs:
            sale_pro_ids = self.env["sale_pro_line"].sudo().search([
                ("sale_pro_id.order_number", "=", raw_materials_order_obj.order_number_id.order_number),
                ("style_number", "=", raw_materials_order_obj.style_number_id.id),
            ])
            material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
                ("order_id", "=", raw_materials_order_obj.order_number_id.id),
                ("style_number", "=", raw_materials_order_obj.style_number_id.id),
                ("material_name", "=", raw_materials_order_obj.material_name)
            ])
            if sale_pro_ids.state != '退单' or raw_materials_order_obj.order_number != 0:#增加判定条件
                if material_summary_sheet_obj:
                    material_summary_sheet_obj.sudo().write({
                        "plan_dosage": raw_materials_order_obj.total_amount,
                        'plan_money_sum': raw_materials_order_obj.total_amount * material_summary_sheet_obj.unit_price,
                        "order_quantity": raw_materials_order_obj.order_number
                    })
                else:
                    self.env["material_summary_sheet"].sudo().create({
                        "order_id": raw_materials_order_obj.order_number_id.id,
                        "style_number": raw_materials_order_obj.style_number_id.id,
                        "material_name": raw_materials_order_obj.material_name,
                        "material_type": raw_materials_order_obj.type,
                        "plan_dosage": raw_materials_order_obj.total_amount,
                        "order_quantity": raw_materials_order_obj.order_number
                    })

        return True

    # def refresh_material_summary_sheet(self):
    #     practical_material_objs = self.env["practical_material"].sudo().search([
    #         ("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)
    #     ])
    #
    #     material_results = {}  # 存储每个面料的实际用量结果
    #
    #     for practical_material_ob in practical_material_objs:
    #         result = 0  # 初始化结果变量
    #
    #         # 查询成品仓库更新实际用量
    #         stocks = self.env['finished_inventory'].search([
    #             ('style_number', '=', practical_material_ob.style_number.id),
    #             ('order_number', '=', practical_material_ob.order_id.id)
    #         ])
    #         result = sum(stock.stock for stock in stocks)  # 计算stock.stock的累加和
    #
    #         # 获取相应的sheet_materials_line用于款号(style_number)和物料名称(material_name)
    #         styles = self.env['sheet_materials_line'].search([
    #             ('sheet_materials_id.style_number.style_number_base', '=',
    #              practical_material_ob.style_number.style_number_base),
    #             ('material_name', '=', practical_material_ob.material_name)
    #         ])
    #
    #         if styles:
    #             result *= styles[0].single_dosage  # 将结果乘以sheet_materials_line的single_dosage
    #
    #         if practical_material_ob.type == "面料":
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_outbound"].search([
    #                 ("material_coding.material_code", "=", practical_material_ob.material_code.id)
    #             ]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_inventory"].search([
    #                 ("material_coding.material_code", "=", practical_material_ob.material_code.id)
    #             ]))
    #         else:
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_outbound"].search([
    #                 ("material_coding.material_code", "=", practical_material_ob.material_code.id)
    #             ]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_inventory"].search([
    #                 ("material_coding.material_code", "=", practical_material_ob.material_code.id)
    #             ]))
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", practical_material_ob.order_id.id),
    #             ("style_number", "=", practical_material_ob.style_number.id),
    #             ("material_name", "=", practical_material_ob.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": practical_material_ob.order_id.id,
    #                 "style_number": practical_material_ob.style_number.id,
    #                 "material_name": practical_material_ob.material_name,
    #                 "material_type": practical_material_ob.type,
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #
    #     # 更新实际用量
    #     for material_name, actual_usage in material_results.items():
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("material_name", "=", material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_usage": actual_usage
    #             })
    #
    #     raw_materials_order_objs = self.env["raw_materials_order"].sudo().search([
    #         ("order_number_id", "!=", False), ("style_number_id", "!=", False)
    #     ])
    #     for raw_materials_order_obj in raw_materials_order_objs:
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", raw_materials_order_obj.order_number_id.id),
    #             ("style_number", "=", raw_materials_order_obj.style_number_id.id),
    #             ("material_name", "=", raw_materials_order_obj.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": raw_materials_order_obj.order_number_id.id,
    #                 "style_number": raw_materials_order_obj.style_number_id.id,
    #                 "material_name": raw_materials_order_obj.material_name,
    #                 "material_type": raw_materials_order_obj.type,
    #                 "actual_usage": result,
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #
    #     return True


    # 还原
    # def refresh_material_summary_sheet(self):
    #     # practical_material_objs = self.env["practical_material"].sudo().search(
    #     #     [("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)])
    #
    #     practical_material_objs = self.env["practical_material"].sudo().search(
    #         [("state", "=", "已采购"), ("order_id", "!=", False), ("style_number", "!=", False)])
    #
    #     material_results = []  # 存储每个面料的实际用量结果
    #
    #     for practical_material_ob in practical_material_objs:
    #         result = 0  # 初始化结果变量
    #
    #         # 查询仓库更新实际用量
    #         stocks = self.env['finished_inventory'].search(
    #             [('style_number', '=', practical_material_ob.style_number.id),
    #              ('order_number', '=', practical_material_ob.order_id.id)])
    #         result = sum(stock.stock for stock in stocks)  # 计算stock.stock的累加和
    #
    #         styles = self.env['sheet_materials_line'].search(
    #             [('sheet_materials_id.style_number', '=', practical_material_ob.style_number.id)])
    #         for s in styles:
    #             result *= s.single_dosage
    #             break
    #
    #         # material_results.append(result)  # 将当前面料的实际用量结果添加到列表中
    #
    #         if practical_material_ob.type == "面料":
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["plus_material_outbound"].search(
    #                 [("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in
    #                                    self.env["plus_material_inventory"].search([(
    #                                        "material_coding.material_code",
    #                                        "=",
    #                                        practical_material_ob.material_code.id)]))
    #         else:
    #             outbound_number = sum(Decimal(str(i.amount)) for i in self.env["warehouse_bom_outbound"].search(
    #                 [("material_coding.material_code", "=", practical_material_ob.material_code.id)]))
    #             inventory_number = sum(Decimal(str(i.amount)) for i in
    #                                    self.env["warehouse_bom_inventory"].search([(
    #                                        "material_coding.material_code",
    #                                        "=",
    #                                        practical_material_ob.material_code.id)]))
    #
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", practical_material_ob.order_id.id),
    #             ("style_number", "=", practical_material_ob.style_number.id),
    #             ("material_name", "=", practical_material_ob.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": practical_material_ob.order_id.id,
    #                 "style_number": practical_material_ob.style_number.id,
    #                 "material_name": practical_material_ob.material_name,
    #                 "material_type": practical_material_ob.type,
    #                 "actual_dosage": practical_material_ob.amount,
    #                 "actual_usage": result,
    #                 "unit": practical_material_ob.unit,
    #                 "unit_price": practical_material_ob.unit_price,
    #                 "outbound_dosage": outbound_number,
    #                 "inventory_dosage": inventory_number,
    #                 "return_goods_dosage": practical_material_ob.fabric_ingredients_refund_id.amount if practical_material_ob.fabric_ingredients_refund_id else 0
    #             })
    #
    #     # 更新实际用量
    #     for index, material_result in enumerate(material_results):
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("material_name", "=", practical_material_objs[index].material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "actual_usage": material_result
    #             })
    #
    #     raw_materials_order_objs = self.env["raw_materials_order"].sudo().search(
    #         [("order_number_id", "!=", False), ("style_number_id", "!=", False)])
    #     for raw_materials_order_obj in raw_materials_order_objs:
    #         material_summary_sheet_obj = self.env["material_summary_sheet"].sudo().search([
    #             ("order_id", "=", raw_materials_order_obj.order_number_id.id),
    #             ("style_number", "=", raw_materials_order_obj.style_number_id.id),
    #             ("material_name", "=", raw_materials_order_obj.material_name)
    #         ])
    #         if material_summary_sheet_obj:
    #             material_summary_sheet_obj.sudo().write({
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #         else:
    #             self.env["material_summary_sheet"].sudo().create({
    #                 "order_id": raw_materials_order_obj.order_number_id.id,
    #                 "style_number": raw_materials_order_obj.style_number_id.id,
    #                 "material_name": raw_materials_order_obj.material_name,
    #                 "material_type": raw_materials_order_obj.type,
    #                 "plan_dosage": raw_materials_order_obj.total_amount,
    #                 "order_quantity": raw_materials_order_obj.order_number
    #             })
    #
    #     return True



