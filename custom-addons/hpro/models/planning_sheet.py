from odoo.exceptions import ValidationError
from odoo import models, fields, api
from decimal import Decimal

class Man_hour_process(models.Model):
    _name = 'mhp.mhp'
    _description = '工时单'
    _inherit = ['mail.thread']
    _rec_name='order_number'
    _order = "create_date desc"



    customer = fields.Char(related='style_number.name', string='客户(旧)')
    order_number = fields.Many2one('ib.detail', string='款式编号', required=True)
    style_number = fields.Many2one('sale_pro.sale_pro', string='订单编号', required=True)
    client_id = fields.Many2one("fsn_customer", string="客户", related="style_number.customer_id", store=True)
    order_price = fields.Char(string="接单价", related="style_number.order_price", store=True)
    date = fields.Date(string='分析日期', required=True)
    analyst = fields.Char(string='分析员', required=True)

    totle_time = fields.Float(string='线上时间汇总', compute="_value_info", store=True, digits=(16, 3))
    totle_price = fields.Float(string='线上总单价', track_visibility='onchange', compute="_value_info", store=True, digits=(16, 3))
    cc_totle_time = fields.Float(string='裁床时间汇总', compute="_value_info", store=True, digits=(16, 3))
    cc_totle_price = fields.Float(string='裁床总单价', track_visibility='onchange', compute="_value_info", store=True, digits=(16, 3))
    hd_totle_time = fields.Float(string='后道时间汇总', compute="_value_info", store=True, digits=(16, 3))
    hd_totle_price = fields.Float(string='后道总单价', track_visibility='onchange', compute="_value_info", store=True, digits=(16, 3))

    work_order = fields.Many2many('work.work', string='工序单', compute="_value_work_order", store=True)

    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")

    difficulty_coefficient = fields.Float(string="难度系数", required=True)

    order_price = fields.Char(string="接单价", related="style_number.order_price", store=True)
    price_multiples = fields.Float(string="价格倍数")


    # 检查难度系数
    @api.constrains('difficulty_coefficient')
    def _check_difficulty_coefficient(self):
        for record in self:

            if record.difficulty_coefficient == 0:
                raise ValidationError("难度系数不可为0！")


    @api.depends('order_number')
    def _value_work_order(self):
        for record in self:
            if record.order_number:
                work_order_ids = record.work_order.sudo().search([("order_number", "=", record.order_number.id)])
                # record.work_order = [(6, 0, work_order_ids)]
                record.work_order = work_order_ids

    @api.depends('work_order')
    def _value_info(self):
        for record in self:

            if record.work_order:

                record.cc_totle_time = sum(record.work_order.filtered(lambda x: x.process_type == "裁床").mapped('standard_time'))
                record.cc_totle_price = sum(record.work_order.filtered(lambda x: x.process_type == "裁床").mapped('standard_price'))
                record.totle_time = sum(record.work_order.filtered(lambda x: x.process_type == "线上").mapped('standard_time'))
                record.totle_price = sum(record.work_order.filtered(lambda x: x.process_type == "线上").mapped('standard_price'))
                record.hd_totle_time = sum(record.work_order.filtered(lambda x: x.process_type == "后道").mapped('standard_time'))
                record.hd_totle_price = sum(record.work_order.filtered(lambda x: x.process_type == "后道").mapped('standard_price'))





    # 验证总单价
    def validation_totle_price(self):
        for record in self:

            if record.order_price:
                if record.totle_price:
                    record.price_multiples = float(record.order_price) / record.totle_price
                else:
                    record.price_multiples = 0

                # 给出返回action
                form_view = self.env.ref('hpro.validation_mhp_mhp_form')
                action = {
                    'name': "数据检测！",
                    'res_model': 'mhp.mhp',
                    'res_id': record.id,
                    'views': [(form_view.id, 'form')],
                    'type': 'ir.actions.act_window',
                    'target': 'new'
                }
                return action

            else:
                raise ValidationError("接单价不可为0！")



    # 设置技术科模块IE工时字段
    def set_template_house_ie_working_hours(self):
        for record in self:
            if "th_per_management" in self.env:
                th_per_management_objs = self.env["th_per_management"].sudo().search([("style_number", "=", record.order_number.id)])

                if th_per_management_objs:
                    for th_per_management_obj in th_per_management_objs:
                        th_per_management_obj.sudo().write({
                            "IE_working_hours": sum(record.work_order.filtered(lambda x: x.process_type == "线上" or x.process_type == "后道").mapped('standard_time'))
                            })


    # 审批通过
    def examination_and_approval(self):
        for record in self:
            for work_order_obj in record.work_order:

                work_order_obj.state = "已审批"

            record.state = "已审批"

            # 设置技术科模块IE工时字段
            record.set_template_house_ie_working_hours()


    # 回退
    def state_fallback(self):
        for record in self:

            for work_order_obj in record.work_order:

                work_order_obj.state = "待审批"

            record.state = "待审批"



    def write(self, vals):

        if self.state == "已审批":

            if "state" in vals and len(vals) == 1:
                pass
            else:
                raise ValidationError(f"该记录已经审批通过，不可修改!")

        res = super(Man_hour_process, self).write(vals)


        return res



    def unlink(self):
        for record in self:
            if record.state == "已审批":
                raise ValidationError(f"该记录已经审批通过，不可删除!")

        res = super(Man_hour_process, self).unlink()

        return res


class work_order(models.Model):
    _name = 'work.work'
    _description = '工序单'
    _rec_name='employee_id'
    _order = "date desc"


    date = fields.Date(string='日期')
    order_number = fields.Many2one('ib.detail', string='款式编号', required=True)
    employee_id = fields.Char(string='工序号', required=True)
    part_name = fields.Char(string='部件名称')
    process_abbreviation = fields.Char(string='工序描述', required=True)
    mechanical_type = fields.Char(string='机器类型')
    process_level = fields.Char(string='工序等级', required=True)
    standard_time = fields.Float(string='标准时间')
    standard_price = fields.Float(string='原单价', digits=(16, 3))
    label = fields.Text(string='标签')
    state = fields.Selection([('待审批', '待审批'), ('已审批', '已审批')], string="状态", default="待审批")

    process_type = fields.Selection([('裁床', '裁床'), ('线上', '线上'), ('后道', '后道')], string="工序类型", required=True)

    def delete_operation(self):
        """删除选中的数据"""
        for record in self:
            record.unlink()


    # 检查工序价格
    @api.constrains('process_level', 'standard_time', 'standard_price')
    def inspection_process_price(self):

        for record in self:

            type = record.order_number.style_number.split('-')[1]

            if type == "1":
                pass
            else:

                # 如果标准工时不为0
                if record.standard_time:

                    def abnormal_detection(coefficient):

                        if (Decimal(str(record.standard_time)) * Decimal(str(coefficient))).quantize(Decimal('0.000')) < Decimal(str(record.standard_price)).quantize(Decimal('0.000')):
                            raise ValidationError(f"款号为{record.order_number.style_number}工序号为{record.employee_id}工序等级为{record.process_level}的工价不可大于工时 * {coefficient}！")   

                    if record.process_level.strip() == "A":
                        abnormal_detection(0.00666)
                    elif record.process_level.strip() == "B":
                        abnormal_detection(0.00583)
                    elif record.process_level.strip() == "C":
                        abnormal_detection(0.00555)
                    elif record.process_level.strip() == "D":
                        abnormal_detection(0.00527)
                    else:
                        raise ValidationError(f"款号为{record.order_number.style_number}工序号为{record.employee_id}的工序等级输入错误！")

            # 检测总价格
            # record.inspection_total_process_price()

    # 检测总价格
    def inspection_total_process_price(self):
        
        objs = self.search([("order_number", "=", self.order_number.id)])
        
        if Decimal(str(sum(i.standard_price for i in objs.filtered(lambda x: x.process_type == "后道")))).quantize(Decimal('0.000')) > 4.2:
            raise ValidationError(f"款号为{self.order_number.style_number}的后道工序总价格不可超过4.2元！")
        
        if Decimal(str(sum(i.standard_price for i in objs.filtered(lambda x: x.process_type == "裁床")))).quantize(Decimal('0.000')) > 1:
            raise ValidationError(f"款号为{self.order_number.style_number}的裁床工序总价格不可超过1元！")


    # 手动检测工序价格
    def manual_examination_process_price(self):

        abnormal_information = []

        for record in self:
            type = record.order_number.style_number.split('-')[1]

            if type == "1":
                pass
            else:

                def abnormal_detection(coefficient):

                    if (Decimal(str(record.standard_time)) * Decimal(str(coefficient))).quantize(Decimal('0.000')) < Decimal(str(record.standard_price)).quantize(Decimal('0.000')):
                        abnormal_information.append(f"款号为{record.order_number.style_number}工序号为{record.employee_id}工序等级为{record.process_level}的工价不可大于工时 * {coefficient}！\n")

                if record.process_level.strip() == "A":
                    abnormal_detection(0.00666)
                elif record.process_level.strip() == "B":
                    abnormal_detection(0.00583)
                elif record.process_level.strip() == "C":
                    abnormal_detection(0.00555)
                elif record.process_level.strip() == "D":
                    abnormal_detection(0.00527)
                else:
                    raise ValidationError(f"款号为{record.order_number.style_number}工序号为{record.employee_id}的工序等级输入错误！")
            
        raise ValidationError("".join(abnormal_information) if abnormal_information else "未检测道异常记录！")
        




    @api.constrains('order_number', 'employee_id')
    def _check_unique(self):
        for record in self:

            demo = self.env[self._name].sudo().search([
                ('order_number', '=', record.order_number.id),
                ("employee_id", "=", record.employee_id)
                ])
            if len(demo) > 1:
                raise ValidationError(f"款号为{record.order_number.style_number}工序号为{record.employee_id}的记录已经存在了！不可重复创建。")



    def write(self, vals):

        if self.state == "已审批":
            if "state" in vals and len(vals) == 1:
                pass
            else:
                raise ValidationError(f"该记录已经审批通过，不可修改!")

        res = super(work_order, self).write(vals)


        return res



    def unlink(self):
        for record in self:

            if record.state == "已审批":
                raise ValidationError(f"该记录已经审批通过，不可删除!")

        res = super(work_order, self).unlink()

        return res


