from odoo import models, fields, api
from odoo.exceptions import ValidationError



class PlusMaterialOutbound(models.Model):
    _name = 'plus_material_outbound'
    _description = '仓库布料单(出库)'
    _rec_name = 'material_name'
    _order = "date desc"


    date = fields.Date(string="日期", required=True, default=fields.Datetime.now())
    state = fields.Selection([('草稿', '草稿'),('已出库', '已出库')], string="状态", default="草稿")
    odd_numbers = fields.Char(string="出库单号", required=True)


    inventory = fields.Many2one("plus_material_inventory", string="库存", required=True)
    material_coding = fields.Many2one("plus_material_list", string="面料编码", related="inventory.material_coding", store=True)

    inventory_number = fields.Float(string="库存数量", related="inventory.amount", store=True)

    order_id = fields.Many2one('sale_pro.sale_pro', string='订单号', related="inventory.order_id", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', related="inventory.style_number", store=True)


    client = fields.Char(string="客户", related="material_coding.client", store=True)
    material_name = fields.Char(string="面料名称", related="material_coding.material_name", store=True)
    specification = fields.Char(string="规格", related="material_coding.specification", store=True)
    color = fields.Char(string="颜色", related="material_coding.color", store=True)
    unit = fields.Char(string="单位", related="material_coding.unit", store=True)
    unit_price = fields.Float(string="单价", related="material_coding.unit_price", store=True, digits=(16, 5))

    amount = fields.Float(string="数量", required=True)
    money_sum = fields.Float(string="金额", digits=(16, 5))
    remark = fields.Char(string="备注")

    consigner = fields.Char(string="发货人（旧）")
    select_consigner = fields.Many2one("hr.employee", string="发货人", required=True)

    supplier = fields.Char(string="班组（旧）")

    fsn_source_where_id = fields.Many2one("fsn_customer", string="来源/去向", required=True, domain="[('customer_type', '=', '公司')]")
    fsn_source_where_name = fields.Char(string="来源/去向, 名称", related="fsn_source_where_id.name")
    
    def set_receive_department_domain(self):

        receive_department_domain_list = ["外发部", "裁床部", "车间", "缝纫", "整件", "后道部", "仓储部", "销售部", "直播运营", "业务部", "临时收货人"]
        department_id_list = []

        for i in receive_department_domain_list:
            department_objs = self.env['hr.department'].search([("name", "like", i)])
            department_id_list.extend(department_objs.ids)
        
        return [('id', '=', department_id_list)]

    receive_department = fields.Many2one("hr.department", string="收货部门", domain=lambda self: self.set_receive_department_domain())

    consignee = fields.Char(string="收货人（旧）")
    consignee_id = fields.Many2one('hr.employee', string="收货人")


    @api.onchange('receive_department')
    def _onchange_consignee_id(self):

        self.consignee_id = False

        if self.receive_department:
            if self.receive_department.name == "临时收货人":
                return {'domain': {'consignee_id': []}}
            else:
                return {'domain': {'consignee_id': [('department_id', '=', self.receive_department.id), ("is_delete", "=", False)]}}
        else:
            return {'domain': {'consignee_id': []}}

    external_contacts = fields.Many2one("fsn_customer", string="外部收货人")


    @api.onchange('fsn_source_where_id')
    def _onchange_external_contacts(self):

        self.external_contacts = False

        if self.fsn_source_where_id:
            return {'domain': {'external_contacts': [('fsn_customer_id', '=', self.fsn_source_where_id.id), ('customer_type', '=', '个人')]}}
        else:
            return {'domain': {'external_contacts': []}}

    plus_material_inventory_id = fields.Many2one("plus_material_inventory", string="库存id")





    # 确认出库
    def affirm_outbound(self):

        if self.amount > self.inventory.amount:
            raise ValidationError(f"出库数量不能大于库存数量!")
        
        else:

            # 添加到库存表中的出库明细中
            self.plus_material_inventory_id = self.inventory.id

            self.state = "已出库"



    # 出库回退
    def back_button(self):
        for record in self:
            record.state = "草稿"
            record.plus_material_inventory_id = False



    def write(self, vals):

        if self.state == "已出库":

            if ("state" in vals or "surface_accessories_loss_id" in vals) and len(vals) == 1:
                pass
            else:

                raise ValidationError(f"{self.odd_numbers}已经出库，不可修改或者删除。")

        res = super(PlusMaterialOutbound, self).write(vals)

        return res


    def unlink(self):

        for record in self:

            if record.state == "已出库":

                raise ValidationError(f"{self.odd_numbers}已经出库，不可修改或者删除。")


        res = super(PlusMaterialOutbound, self).unlink()

        return res











