from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FinishedProductWareWzard(models.TransientModel):
    _name = 'finished_product_ware_wizard'
    _description = '成品仓管理财务审批向导'

    finance_approval_status = fields.Selection([('有问题', '有问题'), ('未审批', '未审批'), ('已审批', '已审批')], string="财务部审批状态")

    finance_approval_remark = fields.Text(string="财务部审批备注")


    def set_finance_approval(self):

        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')
        for active_id in active_ids:
            active_model_obj = self.env[active_model].sudo().browse(active_id)

            if self.finance_approval_status == "有问题":
                active_model_obj.finance_approval_status = self.finance_approval_status
                active_model_obj.finance_approval_remark = self.finance_approval_remark
            elif self.finance_approval_status == "未审批":
                active_model_obj.finance_approval_status = self.finance_approval_status
                active_model_obj.finance_approval_remark = False
            elif self.finance_approval_status == "已审批":
                active_model_obj.finance_approval_status = self.finance_approval_status
                active_model_obj.finance_approval_remark = False


class FinishedProductWare(models.Model):
    _name = 'finished_product_ware'
    _description = '成品仓管理'
    _rec_name = 'receipt_number'
    _order = "date desc"


    date = fields.Date(string="日期", required=True)
    receipt_number = fields.Char(string="单据编号", required=True)

    processing_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('其他', '其他'),
        ], string="加工类型")
    production_factory = fields.Many2one("outsource_plant", string="工厂名称")
    type = fields.Selection([('入库', '入库'), ('出库', '出库')], string="类型", required=True)
    record_type = fields.Selection([('扫码', '扫码'), ('人工', '人工')], string="类型", default="人工")
    state = fields.Selection([('草稿', '草稿'),('确认', '确认')], string="状态", default="草稿")
    warehouse_principal = fields.Char(string="仓库负责人", required=True)
    docking_people = fields.Char(string="送货人/接收人", required=True)

    customer = fields.Char(string="来源/去向（旧）")
    customer_id = fields.Many2one("fsn_customer", string="来源/去向", required=True)

    note = fields.Text(string="备注")

    state = fields.Selection([('草稿', '草稿'),('确认', '确认')], string="状态", default="草稿")

    finance_approval_status = fields.Selection([('有问题', '有问题'), ('未审批', '未审批'), ('已审批', '已审批')], string="财务部审批状态", default="未审批")

    finance_approval_remark = fields.Text(string="财务部审批备注")

    # 确认弹窗
    def set_finance_approval(self):

        action = {
            'name': "财务部审批",
            'view_mode': 'form',
            'res_model': 'finished_product_ware_wizard',
            'view_id': self.env.ref('warehouse_management.finished_product_ware_wizard_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

        return action

    finished_product_ware_line_ids = fields.One2many("finished_product_ware_line", "finished_product_ware_id", string="成品仓明细")

    # 检查数据唯一性
    @api.constrains('date', 'receipt_number', 'type')
    def _check_unique(self):

        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ('receipt_number', '=', self.receipt_number),
            ('type', '=', self.type)
        ])

        if len(demo) > 1:
            raise ValidationError(f"{self.date},{self.receipt_number},{self.type}已经存在了，不可重复创建！")


    # 设置状态确认
    def set_state(self):
        for record in self:

            if record.state == "草稿":
                # 检查订单号款号
                record.check_order_number_and_style_number()
                record.state = "确认"
            elif record.state == "确认":
                record.state = "草稿"
            else:
                raise ValidationError(f"状态异常，请联系管理员！")
            # 检测库存
            record.check_inventory()


    # 检查订单号款号尺码
    def check_order_number_and_style_number(self):
        for finished_product_ware_line_id in self.finished_product_ware_line_ids:
            obj = self.env["style_number_summary"].search([
                ("order_number", "=", finished_product_ware_line_id.order_number.id),
                ("style_number", "=", finished_product_ware_line_id.style_number.id),
                ("size", "=", finished_product_ware_line_id.size.id),
            ])

            if not obj:
                raise ValidationError(f"请检查是否存在订单号:{finished_product_ware_line_id.order_number.order_number}\
                    该款号:{finished_product_ware_line_id.style_number.style_number}\
                        尺码:{finished_product_ware_line_id.size.name}！")


    # 检测库存
    def check_inventory(self):

        for i in self.finished_product_ware_line_ids:

            if i.finished_inventory_id.number < 0:
                raise ValidationError(f"库存不足，不可执行此操作！订单号:{i.order_number.order_number},款号:{i.style_number.style_number} 尺码:{i.size.name}")


    def write(self, vals):
        print(vals)

        if self.state == "确认":

            if "state" in vals and len(vals) == 1:
                pass
            elif "quality_control_collect_id" in vals and len(vals) == 1:
                pass
            elif "style_number_summary_id" in vals and len(vals) == 1:
                pass
            elif "finance_approval_status" in vals and len(vals) == 1:
                pass
            elif "finance_approval_remark" in vals and len(vals) == 1:
                pass
            else:
                raise ValidationError(f"已经确认，不可修改！。")

        res = super(FinishedProductWare, self).write(vals)

        return res


    def unlink(self):
        for record in self:
            if record.state == "确认":
                    
                raise ValidationError(f"已经确认，不可删除！。")


        res = super(FinishedProductWare, self).unlink()

        return res



    def generate_customer(self):
        for record in self:
            if record.customer:
                fsn_customer_obj = self.env['fsn_customer'].search([("name", "=", record.customer)])
                if not fsn_customer_obj:
                    fsn_customer_obj = self.env['fsn_customer'].create({"name": record.customer, "country_id": 48})

                record.customer_id = fsn_customer_obj.id




class FinishedProductWareLine(models.Model):
    _name = 'finished_product_ware_line'
    _description = '成品仓管理明细'
    _order = "date desc"


    finished_product_ware_id = fields.Many2one("finished_product_ware", ondelete="cascade", string="单据")
    date = fields.Date(string="日期", related='finished_product_ware_id.date', store=True)
    process_type = fields.Selection([
        ('外发', '外发'),
        ('工厂', '工厂'),
        ('其他', '其他'),
        ], string="加工类型", related='finished_product_ware_id.processing_type', store=True)
    production_factory = fields.Many2one("outsource_plant", string="工厂名称", related='finished_product_ware_id.production_factory', store=True)
    type = fields.Selection([('入库', '入库'), ('出库', '出库')], string="类型", related='finished_product_ware_id.type', store=True)
    source_destination = fields.Many2one("fsn_customer", string="来源/去向", related='finished_product_ware_id.customer_id', store=True)
    # state = fields.Selection([('草稿', '草稿'),('确认', '确认')], string="状态", related='finished_product_ware_id.state', store=True)
    state = fields.Selection([('草稿', '草稿'),('确认', '确认')], string="状态", compute="set_state", store=True)
    @api.depends('finished_product_ware_id', 'finished_product_ware_id.state')
    def set_state(self):
        for record in self:
            if record.finished_product_ware_id:
                record.state = record.finished_product_ware_id.state

                record.finished_inventory_id.set_number()
                record.finished_inventory_id.set_normal_number()
    
    def state_back(self):
        for record in self:
            record.state = "草稿"

    def state_confirm(self):
        for record in self:
            # 检测库存
            record.finished_product_ware_id.check_inventory()
            record.state = "确认"

    size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer(string="件数")

    quality = fields.Selection([('合格', '合格'), ('次品', '次品'), ('报次', '报次'), ('半成品', '半成品'), ('裁片', '裁片'), ('裁片报次', '裁片报次')], string="产品质量", required=True)

    character = fields.Selection([('正常', '正常'), ('返修', '返修'), ('退货', '退货')], string="性质", required=True)


    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号', required=True)
    customer_id = fields.Many2one("fsn_customer", string="客户", related='order_number.customer_id', store=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    @api.onchange('order_number')
    def style_number_domain(self):
        self.style_number = False
        if self.order_number:
            
            return {'domain': {'style_number': [("id", "in", self.order_number.sale_pro_line_ids.style_number.ids)]}}
        else:
            return {'domain': {'style_number': []}}
    fsn_color = fields.Many2one("fsn_color", string="颜色", compute="_set_fsn_color", store=True)
    # 设置颜色
    @api.depends('style_number')
    def _set_fsn_color(self):
        for record in self:
            record.fsn_color = record.style_number.fsn_color.id



    size = fields.Many2one("fsn_size", string="尺码", required=True)
    number = fields.Integer(string="件数")



    # 检查数据件数不可为负数
    @api.constrains('number')
    def _check_number(self):
        for record in self:
            if record.number <= 0:
                raise ValidationError(f"{record.date},{record.order_number.order_number},{self.style_number.style_number}件数不合法！")



    def write(self, vals):

        if self.state == "确认":

            if "state" in vals and len(vals) == 1:
                pass
            elif "quality_control_collect_id" in vals and len(vals) == 1:
                pass
            elif "back_channel_progress_id" in vals and len(vals) == 1:
                pass
            else:             
                raise ValidationError(f"已经确认，不可修改！。")
                

        res = super(FinishedProductWareLine, self).write(vals)

        return res

