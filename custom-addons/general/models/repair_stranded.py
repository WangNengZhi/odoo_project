from odoo import models, fields, api


class RepairStranded(models.Model):
    _name = 'repair_stranded'
    _description = '返修滞留'
    _rec_name = 'date'
    _order = "date desc"


    date = fields.Date(string="日期")
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号')
    type = fields.Selection([('外发', '外发'), ('工厂', '工厂')], string="加工类别", related="order_number.processing_type", store=True)
    style_number = fields.Many2one('ib.detail', string='款号')

    order_quantity = fields.Integer(string="订单数量")

    cut_quantity = fields.Integer(string="裁剪数量")

    outsource_delivery_number = fields.Integer(string="外发交货数")
    workshop_hand_number = fields.Integer(string="车间上交件数")
    dg_number = fields.Integer(string="吊挂件数（车间）")
    put_number = fields.Integer(string="入库件数")
    workshop_stranded_number = fields.Integer(string="车间滞留数（吊挂件数-车间上交数+当日吊挂返修件数-当日吊挂修复件数）", compute="set_workshop_stranded_number", store=True)
    @api.depends("dg_number", "workshop_hand_number", "intraday_dg_rework_number")
    def set_workshop_stranded_number(self):
        for record in self:
            record.workshop_stranded_number = record.dg_number - record.workshop_hand_number + record.intraday_dg_rework_number - record.intraday_dg_repair_number

    after_road_stranded_number = fields.Integer(string="后道滞留数（总滞留数-车间滞留数）", compute="set_after_road_stranded_number", store=True)
    @api.depends("stranded", "workshop_stranded_number")
    def set_after_road_stranded_number(self):
        for record in self:
            record.after_road_stranded_number = record.stranded - record.workshop_stranded_number
    stranded = fields.Integer(string="总滞留件数（车间吊挂-入库+外发交货数）", compute="set_stranded", store=True)

    @api.depends("dg_number", "dg_number", "outsource_delivery_number")
    def set_stranded(self):
        for record in self:
            record.stranded = record.dg_number - record.put_number + record.outsource_delivery_number

    dg_behind_number = fields.Integer(string="吊挂件数（后道）")
    intraday_dg_behind_number = fields.Integer(string="当日吊挂件数（后道）")
    intraday_dg_rework_number = fields.Integer(string="当日吊挂返修件数")
    intraday_dg_repair_number = fields.Integer(string="当日吊挂修复件数")
    no_examine_number = fields.Integer(string="未查件数（车间吊挂-后道吊挂）", compute="set_no_examine_number", store=True)


    @api.depends("dg_number", "dg_behind_number")
    def set_no_examine_number(self):
        for record in self:
            record.no_examine_number = record.dg_number - record.dg_behind_number


    # 获取当日吊挂信息(后道)
    def get_intraday_dg_behind_number_info(self, date, order_number_id, style_number_id) -> int:
        ''' 获取当日吊挂信息(后道)'''
        
        suspension_system_summary_list = self.env['suspension_system_summary'].search_read(
            domain=[("order_number", "=", order_number_id), ("style_number", "=", style_number_id), ("dDate", "=", date), ("group.department_id", "=", "后道")],
            fields=["total_quantity"]
        )

        return sum(i['total_quantity'] for i in suspension_system_summary_list)

    
    # 获取当日吊挂返修信息
    def get_intraday_dg_rework_number_info(self, date, order_number_id, style_number_id) -> int:
        ''' 获取当日吊挂返修信息'''

        suspension_system_rework_list = self.env['suspension_system_rework'].search_read(
            domain=[("order_number", "=", order_number_id), ("style_number", "=", style_number_id), ("date", "=", date)],
            fields=["number"]
        )

        return sum(i['number'] for i in suspension_system_rework_list)


    # 获取外发交货数
    def get_outsource_delivery_number(self, order_number_id, style_number_id) -> int:
        ''' 获取外发交货数'''

        return sum(self.env['outsource_order'].sudo().search([("order_id", "=", order_number_id), ("style_number", "=", style_number_id)]).mapped("actual_delivered_quantity"))


    # 获取车间上交件数
    def get_workshop_hand_number(self, order_number_id, style_number_id) -> int:
        ''' 获取车间上交件数'''

        return sum(self.env['pro.pro'].sudo().search([("order_number", "=", order_number_id), ("style_number", "=", style_number_id)]).mapped("number"))


    # 获取吊挂修复件数
    def get_intraday_dg_repair_number_info(self, date, order_number_id, style_number_id) -> int:
        ''' 获取吊挂修复件数'''

        suspension_system_repair_list = self.env['suspension_system_repair'].search_read(
            domain=[("order_number", "=", order_number_id), ("style_number", "=", style_number_id), ("date", "=", date)],
            fields=["number"]
        )

        return sum(i['number'] for i in suspension_system_repair_list)


    def get_cut_quantity(self, order_number_id, style_number_id) -> int:
        ''' 获取裁床数量'''


        

        return 0


    def refreshing_retention_records(self):
        ''' 刷新滞留记录'''

        date = fields.Datetime.now().date()
        self.search([("date", "=", date)]).unlink()

        sale_pro_line_list = self.env['sale_pro_line'].search_read(
            domain=[("state", "not in", ["退单", "已完成"]), ("sale_pro_id.date", ">=", "2022-10-01")],
            fields=["sale_pro_id", "style_number"]
        )

        for sale_pro_line_record in sale_pro_line_list:

            order_number_id = sale_pro_line_record['sale_pro_id'][0]
            style_number_id = sale_pro_line_record['style_number'][0]
            
            suspension_system_summary_objs = self.env['suspension_system_summary'].read_group(
                domain=[("order_number", "=", order_number_id), ("style_number", "=", style_number_id)],
                fields=['total_quantity'],
                groupby="group"
            )

            dg_total_quantity = sum(i['total_quantity'] for i in suspension_system_summary_objs if self.env['check_position_settings'].browse(i['group'][0]).department_id == "车间")

            dg_behind_total_quantity = sum(i['total_quantity'] for i in suspension_system_summary_objs if self.env['check_position_settings'].browse(i['group'][0]).department_id == "后道")
            
            rk_total_quantity = sum(self.env["finished_product_ware_line"].search([
                ("order_number", "=", order_number_id),
                ("style_number", "=", style_number_id),
                ("type", "=", "入库"),
                ("quality", "=", "合格"),
                ("character", "=", "正常"),
                ("state", "=", "确认")
            ]).mapped("number"))

            schedule_production_objs = self.env["schedule_production"].sudo().search([("order_number", "=", order_number_id), ("style_number", "=", style_number_id)])

            obj = self.create({
                "date": date,
                "order_number": order_number_id,
                "style_number": style_number_id,
                "dg_number": dg_total_quantity,
                "put_number": rk_total_quantity,
                "order_quantity": sum(schedule_production_objs.mapped("quantity_order")),
                "cut_quantity": sum(schedule_production_objs.mapped("quantity_cutting")),
                "intraday_dg_behind_number": self.get_intraday_dg_behind_number_info(date, order_number_id, style_number_id),
                "intraday_dg_rework_number": self.get_intraday_dg_rework_number_info(date, order_number_id, style_number_id),
                "outsource_delivery_number": self.get_outsource_delivery_number(order_number_id, style_number_id),
                "workshop_hand_number": self.get_workshop_hand_number(order_number_id, style_number_id),
                "intraday_dg_repair_number": self.get_intraday_dg_repair_number_info(date, order_number_id, style_number_id),
                "dg_behind_number": dg_behind_total_quantity,
            })


        