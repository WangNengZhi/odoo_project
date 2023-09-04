# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from . import mssaql_class



class sale_pro(models.Model):
    _name = 'sale_pro.sale_pro'
    _description = '销售订单'
    _rec_name = 'order_number'
    _order = "date desc"


    name = fields.Char('客户')
    customer_id = fields.Many2one("fsn_customer", string="客户", required=True)
    # 新加
    fsn_sales_line = fields.Many2one("sale_pro_line", string="销售订单明细")

    date = fields.Date('日期', required=True)
    external_order_number = fields.Char(string='外部订单号')
    order_number = fields.Char('订单号', required=True)
    order_price = fields.Char('接单价')
    # processing_type = fields.Selection([
    #     ('外发', '外发'),
    #     ('工厂', '工厂'),
    #     ('返修', '返修'),
    #     ], string="加工类型", required=True)
    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('返修', '返修'),
        ('生产', '生产'),
    ], string="加工类型", required=True)
    contract_price = fields.Float(string="合同价格", digits=(16, 5), groups='fsn_base.fsn_insiders_group')
    IE_working_hours = fields.Char('IE工时(秒)')
    workshop_unit_price = fields.Char('车间单价')
    product_name = fields.Char('品名', required=True)
    attribute = fields.Many2one("order_attribute", string="属性", required=True)
    customer_delivery_time = fields.Date('客户货期', required=True)

    anticipate_face_to_face_time = fields.Date(string="预计面辅料齐备日期")
    face_to_face_time = fields.Date('面辅齐备日期')
    plan_tailor_date = fields.Date(string="计划开裁日期")
    plan_online_date = fields.Date(string="计划上线日期")
    planned_completion_date = fields.Date(string="计划完成日期")
    production_group_ids = fields.Many2many("fsn_staff_team", string="生产组别")

    order_category = fields.Char('订单类别')
    production_group = fields.Char('生产组别（旧）')
    special_craft = fields.Char('特种工艺')
    ib_detail = fields.Many2many('ib.detail', string='制造明细')
    style_picture = fields.Image('款式图片')
    total_price = fields.Float(string="总价格", compute="_set_total_price", store=True)
    deduct_money = fields.Float(string="扣款")
    remarks = fields.Char(string="备注")


    is_conceal = fields.Boolean(string="是否隐藏")

    is_finish = fields.Selection([
        ('未上线', '未上线'),
        ('未完成', '未完成'),
        ('已完成', '已完成'),
        ('退单', '退单')
        ], string="订单状态", default="未上线", compute="set_is_finish", store=True)
    @api.depends("sale_pro_line_ids", "sale_pro_line_ids.state")
    def set_is_finish(self):
        for record in self:
            if record.sale_pro_line_ids:
                if all(i in ["已完成", "退单"] for i in record.sale_pro_line_ids.mapped("state")) and not all(i == "退单" for i in record.sale_pro_line_ids.mapped("state")):
                    record.actual_finish_date = fields.Date.today()
                    record.is_finish = "已完成"
                elif all(i == "退单" for i in record.sale_pro_line_ids.mapped("state")):
                    record.is_finish = "退单"
                else:
                    record.is_finish = "未完成"

# if all(i in ["已完成", "退单"] for i in record.sale_pro_line_ids.mapped("state")):


    customer_payment_amount = fields.Float(string="客户付款金额")
    actual_finish_date = fields.Date(string="实际完成日期")
    is_payment = fields.Boolean(string="是否已付款")

    actual_delivered_quantity = fields.Float(string="实际交货数")

    ib_detail_ids = fields.One2many("ib.detail", "order_id", string="订单明细")

    detection_price = fields.Boolean(string="检测款号价格", compute="_set_total_price", store=True)



    # 改变状态 前进
    def action_advance(self):
        for record in self:

            if record.is_finish == "未上线":
                if record.sale_pro_line_ids:
                    record.is_finish = "未完成"
                else:
                    raise ValidationError("未发现任何订单明细信息，不可开始！")
            elif record.is_finish == "未完成":
                if record.actual_finish_date:
                    record.is_finish = "已完成"
                else:
                    raise ValidationError("未填写实际完成日期，不可完成！")



    def action_chargeback(self):
        ''' 退单'''
        for record in self:

            record.is_finish = "退单"
            style_number_summary_objs = self.env["style_number_summary"].sudo().search([("order_number", "=", record.id)])
            style_number_summary_objs.sudo().write({"state": "退单"})





    # 回退
    def state_back(self):
        for record in self:

            if record.is_finish == "已完成":

                record.is_finish = "未完成"

            else:
                raise ValidationError("状态异常，不可回退！")




    @api.constrains('order_number')
    def _check_unique(self):

        for record in self:

            demo = self.env[self._name].sudo().search([('order_number', '=', record.order_number)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在订单号为：{record.order_number}的记录了！")


    # 设置总价格
    @api.depends('ib_detail_ids', 'ib_detail_ids.detail_total_price', 'sale_pro_line_ids', 'sale_pro_line_ids.actual_cutting_price')
    def _set_total_price(self):
        for record in self:
            # 如果存在新的订单明细（则按新的订单明细计算价格）
            if record.sale_pro_line_ids:

                record.total_price = sum(record.sale_pro_line_ids.mapped('actual_cutting_price'))

            else:

                # 临时变量
                tem_var = False
                # 将总价格设置为0
                record.total_price = 0

                for line in record.ib_detail_ids:
                    record.total_price = record.total_price + line.detail_total_price
                    # 如果有款号价格为0
                    if line.price == 0:
                        tem_var = True

                record.detection_price = tem_var



    # 设置统计模块的实际完成日期
    def _set_statistics_actual_finish_date(self):


        for line in self.ib_detail_ids:

            style_number_summary_objs = self.env["style_number_summary"].sudo().search([
                ("style_number", "=", line.id)
            ])

            style_number_summary_objs.write({
                "actual_finish_date": self.actual_finish_date
            })






    def write(self, vals):

        res = super(sale_pro, self).write(vals)

        # 设置统计模块的实际完成日期
        self._set_statistics_actual_finish_date()

        return res

    @api.model
    def create(self, vals):

        res = super(sale_pro, self).create(vals)

        # 设置统计模块的实际完成日期
        res._set_statistics_actual_finish_date()

        return res







class iblling_details(models.Model):
    _name = 'ib.detail'
    _description = '制单明细与实裁'
    _rec_name = 'style_number'
    _order = "date desc"


    order_id = fields.Many2one("sale_pro.sale_pro", string="订单id")
    date = fields.Date(string='日期', required=True)
    external_style_number = fields.Char(string="外部款号")
    style_number = fields.Char(string='款号', required=True)
    style_number_base = fields.Char(string="款号前缀", compute="set_style_number_base", store=True)
    @api.depends('style_number')
    def set_style_number_base(self):
        for record in self:

            if record.style_number:
                tem_style_number = record.style_number.split("-")

                record.style_number_base = tem_style_number[0]

            else:
                record.style_number_base = False

        




    color = fields.Char('颜色')
    salesman = fields.Many2one('hr.employee', string='业务员')
    style_picture = fields.Image('样衣')
    price = fields.Float(string="价格")
    detail_total_price = fields.Float(string="总价格")
    z_xs = fields.Integer('制单XS')
    z_s = fields.Integer('制单S')
    z_m = fields.Integer('制单M')
    z_l = fields.Integer('制单L')
    z_xl = fields.Integer('制单XL')
    z_two_xl = fields.Integer('制单2XL')
    z_three_xl = fields.Integer('制单3XL')
    z_four_xl = fields.Integer('制单4XL')
    z_five_xl = fields.Integer('制单5XL')
    z_totle = fields.Integer('制单合计')

    s_xs = fields.Integer('实裁XS')
    s_s = fields.Integer('实裁S')
    s_m = fields.Integer('实裁M')
    s_l = fields.Integer('实裁L')
    s_xl = fields.Integer('实裁XL')
    s_two_xl = fields.Integer('实裁2XL')
    s_three_xl = fields.Integer('实裁3XL')
    s_four_xl = fields.Integer('实裁4XL')
    s_five_xl = fields.Integer('实裁5XL')
    s_totle = fields.Integer('实裁合计')

    is_conceal = fields.Boolean(string="是否隐藏")





    @api.onchange('z_xs', 'z_s', 'z_m', 'z_l', 'z_xl', 'z_two_xl', 'z_three_xl', 'z_four_xl', 'z_five_xl')
    def chan(self):
        self.z_totle = self.z_xs + self.z_s + self.z_m + self.z_l + self.z_xl + self.z_two_xl + self.z_three_xl + self.z_four_xl + self.z_five_xl
    @api.onchange('s_xs', 's_s', 's_m', 's_l', 's_xl', 's_two_xl', 's_three_xl', 's_four_xl', 's_five_xl')
    def chan1(self):
        self.s_totle = self.s_xs + self.s_s + self.s_m + self.s_l + self.s_xl + self.s_two_xl + self.s_three_xl + self.s_four_xl + self.s_five_xl


    # 计算总价格
    @api.onchange('price', 's_totle')
    def _set_detail_total_price(self):
        self.detail_total_price = self.price * self.s_totle


    @api.constrains('style_number')
    def _check_unique(self):

        for record in self:
            if not re.match('[0-9]{4}-[0-9]-[A-Z]{2}', record.style_number):
                raise ValidationError(f"款号不符合格式！")


            demo = self.env[self._name].sudo().search([('style_number', '=', record.style_number)])
            if len(demo) > 1:
                raise ValidationError(f"已经存在款号为：{record.style_number}的记录了！")


    # 设置返修数据
    def _set_customer_repair_line(self):

        objs = self.env["customer_repair_line"].sudo().search([
            ("item_number", "=", self.id)
            ])


        if objs:
            objs.write({
                "date": self.date,      # 日期
                "color": self.color,    # 颜色
                "coustm": self.order_id.name,  # 客户
                "reality_tailor": self.s_totle,     # 实裁数量
            })
        else:
            objs.create({
                "item_number": self.id,     # 款号
                "date": self.date,      # 日期
                "color": self.color,    # 颜色
                "coustm": self.order_id.name,  # 客户
                "reality_tailor": self.s_totle,     # 实裁数量
            })



    # 用户同步gst的工序数据
    def sync_sqlserver(self):

        tem_list = self.style_number.split("-")
        sql_server_host = self.env.company.sql_server_host
        sql_server_user = self.env.company.sql_server_user
        sql_server_password = self.env.company.sql_server_password
        sql_server_database = self.env.company.sql_server_database

        gst_sql_server_host = self.env.company.gst_sql_server_host
        gst_sql_server_user = self.env.company.gst_sql_server_user
        gst_sql_server_password = self.env.company.gst_sql_server_password
        gst_sql_server_database = self.env.company.gst_sql_server_database

        # gst数据库
        gst_sqlserver = mssaql_class.MSSQL(host=gst_sql_server_host, user=gst_sql_server_user, pwd=gst_sql_server_password, db=gst_sql_server_database)
        # 中间数据库
        middleware_sqlserver = mssaql_class.MSSQL(host=sql_server_host, user=sql_server_user, pwd=sql_server_password, db=sql_server_database)

        gst_sql = f"select * from gstv_ksgxb where wbkh = '{tem_list[0]}';"
        gst_reslist = gst_sqlserver.ExecQuery(gst_sql)

        for gst_res in gst_reslist:
            # 0订单编号 1内部id 15款式编号 3部件代码 4部件名称 2工序序号 5工序代码 7工序名称 8机器名称 11审核标志 12工段代码 13工段名称 14工段等级 20工时 22标准单价 23额外单价 24总单价 19小时指标
            # print(gst_res[0], gst_res[1], gst_res[15], gst_res[3], gst_res[4], gst_res[2], gst_res[5], gst_res[7], gst_res[8], gst_res[11], gst_res[12], gst_res[13], gst_res[14], gst_res[20], gst_res[22], gst_res[23], gst_res[24], gst_res[19])

            middleware_sql = f"select * from planning_sheet where wbkh = {gst_res[15]} and gxxh = {gst_res[2]}"
            middleware_reslist = middleware_sqlserver.ExecQuery(middleware_sql)

            if middleware_reslist:
                pass
            else:

                # 内部id 订单编号 款式编号 部件代码 部件名称 工序序号 工序代码 工序名称 机器名称 审核标志 工段代码 工段名称 工段等级 工时 标准单价 额外单价 总单价 小时指标
                middleware_sql = f"INSERT INTO planning_sheet (ksbh,ddbh,wbkh,bjdm,bjmc,gxxh,gxdm,gxmc,jqmc_C,bz,bmdm,bmmc,gzdm,gs,dj,dj2,dj3,xszb)\
                                    VALUES ('{gst_res[1]}','{gst_res[0]}','{gst_res[15]}','{gst_res[3]}','{gst_res[4]}',{gst_res[2]},'{gst_res[5]}','{gst_res[7]}','{gst_res[8]}',\
                                        '{gst_res[11]}','{gst_res[12]}','{gst_res[13]}','{gst_res[14]}',{gst_res[20]},{gst_res[22]},{gst_res[23]},{gst_res[24]},{gst_res[21]});"

                # 示例数据
                # middleware_sql = f"INSERT INTO planning_sheet (ksbh,ddbh,wbkh,bjdm,bjmc,gxxh,gxdm,gxmc,jqmc_C,bz,bmdm,bmmc,gzdm,gs,dj,dj2,dj3,xszb)\
                #                     VALUES ('1231','1232','1233','1234','1235',1236,'1237','1238','1239','123q','123w','123e','123r',1237,321.0,322.0,323.0,324.0);"

                middleware_sqlserver.ExecNonQuery(middleware_sql)





    def write(self, vals):
        res = super(iblling_details, self).write(vals)
        # 设置返修数据
        self._set_customer_repair_line()

        return res


    @api.model
    def create(self, vals):

        instance = super(iblling_details, self).create(vals)
        # 设置返修数据
        instance._set_customer_repair_line()

        # 创建款号时，同步gst数据到中间数据库
        # instance.sync_sqlserver()


        return instance


    def set_gst_all(self):

        for record in self:

            record.sync_sqlserver()


    def set_all(self):

        objs = self.env[""].sudo().search([])

        for obj in objs:


            style_number_summary_objs = self.env["style_number_summary"].sudo().search([
                ("style_number", "=", obj.id)
            ])
            if style_number_summary_objs:
                style_number_summary_objs.sudo().set_order_number_value()
                style_number_summary_objs.sudo().set_workshop()
                style_number_summary_objs.sudo().set_cutting_bed()
                style_number_summary_objs.sudo().set_posterior_passage()
                style_number_summary_objs.sudo().set_enter_warehouse()
                style_number_summary_objs.sudo().set_out_of_warehouse()
                style_number_summary_objs.sudo()._set_finish_plan_date()
            else:
                new_obj = style_number_summary_objs.sudo().create({
                    "style_number": obj.id,
                })
                new_obj.sudo().set_order_number_value()
                new_obj.sudo().set_workshop()
                new_obj.sudo().set_cutting_bed()
                new_obj.sudo().set_posterior_passage()
                new_obj.sudo().set_enter_warehouse()
                new_obj.sudo().set_out_of_warehouse()
                new_obj.sudo()._set_finish_plan_date()









class schedule(models.Model):
    _name = 'sch.sch'
    _description = '订单进度表'

    # style_number = fields.Many2one('ib.detail', '款号')
    order_number = fields.Many2one('sale_pro.sale_pro', '订单号', required=True)
    production_order = fields.Char('生产下单')
    picking_date = fields.Date('领料日期')
    cut_date = fields.Date('裁剪日期')
    special_craft = fields.Char('特种工艺')
    actually_line = fields.Char('实际上线')
    sample_sealing_is_complete = fields.Char('封样完成')
    the_eight_pieces_completed = fields.Char('首八件完成')
    start_delivery = fields.Char('开始交货')
    over_delivery = fields.Char('交货完成')
    futures_achievement_rate = fields.Char('期货达成率')
    style_number = fields.Many2many('style.num.sch', string='款号')

    @api.onchange('order_number')
    def ocn(self):
        if self.order_number:
            return {
                'domain': {'style_number': [('order_number', '=', self.order_number.display_name)]}}




class summary(models.Model):
    _name = 'sum.sum'
    _description = '汇总表'
    _rec_name = 'order_number'

    # style_number = fields.Many2one('ib.detail', string='款号')
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    workshop_delivery_date = fields.Date(string='车间交货日期')
    workshop_return_date = fields.Date(string='车间退货日期')
    number_of_deliveries = fields.Float(string='交货数')
    number_of_returns = fields.Float(string='退货数')
    customer_date = fields.Date(string='交客户日期')
    return_customer_date = fields.Date(string='退客户日期')
    number_of_customers = fields.Float(string='交客户数量')
    customer_refund = fields.Float(string='客户退数')
    remark = fields.Char(string='备注')
    return_rate = fields.Float(string='退货率(%)')
    sch = fields.Many2many('sch.sch', string='进度')

    @api.onchange('sch')
    def _change_date(self):
        if self.order_number:
            sch = self.sch
            number_of_deliveries = []
            number_of_returns = []
            number_of_customers = []
            customer_refund = []
            id = self.sch.style_number.ids
            # demo = self.env['款号进度表'].sudo().search([('id', '=', id)])

            for i in id:
                demo = self.env['style.num.sch'].sudo().search([('id', '=', i)])
                number_of_deliveries.append(abs(float(demo.number_of_deliveries)))
                number_of_returns.append(abs(float(demo.number_of_returns)))
                number_of_customers.append(abs(float(demo.number_of_customers)))
                customer_refund.append(abs(float(demo.customer_refund)))
            self.number_of_deliveries = sum(number_of_deliveries)
            self.number_of_returns = sum(number_of_returns)
            self.number_of_customers = sum(number_of_customers)
            self.customer_refund = sum(customer_refund)
            number_of_customers = sum(number_of_customers)
            customer_refund = sum(customer_refund)
            if number_of_customers:
                self.return_rate = (customer_refund / number_of_customers) * 100
            else:
                self.return_rate = ''

    @api.onchange('order_number')
    def ocn(self):
        if self.order_number:
            return {
                'domain': {'sch': [('order_number', '=', self.order_number.display_name)]}}



    @api.onchange('customer_refund', 'number_of_customers')
    def _compu_customer(self):
        if self.number_of_customers:
            self.return_rate = (self.customer_refund / self.number_of_customers) * 100


class style_num_sch(models.Model):
    _name = 'style.num.sch'
    _description = '单款进度表'

    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    workshop_delivery_date = fields.Date(string='车间交货日期')
    workshop_return_date = fields.Date(string='车间退货日期')
    number_of_deliveries = fields.Char(string='交货数')
    number_of_returns = fields.Char(string='退货数')
    customer_date = fields.Date(string='交客户日期')
    return_customer_date = fields.Date(string='退客户日期')
    number_of_customers = fields.Float(string='交客户数量')
    customer_refund = fields.Float(string='客户退数')
    remark = fields.Char(string='备注')