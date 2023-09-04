from odoo import models, fields, api

class MhpMhp(models.Model):
    """ 继承工时成本"""
    _inherit = 'mhp.mhp'

    def set_practical_material(self):
        for record in self:
            if record.state == "已审批":

                practical_material_obj = self.env['total_cost'].sudo().search([("order_number", "=", record.style_number.id), ("style_number", "=", record.order_number.id)])
                if not practical_material_obj:
                    practical_material_obj = self.env['total_cost'].sudo().create({
                        "order_number": record.style_number.id,
                        "style_number": record.order_number.id
                    })
                
                practical_material_obj.mhp_mhp_id = record.id

            elif record.state == "待审批":

                practical_material_obj = self.env['total_cost'].sudo().search([("order_number", "=", record.order_number.id), ("style_number", "=", record.style_number.id)])
                if practical_material_obj:
                    practical_material_obj.mhp_mhp_id = False



    # 继承审批通过方法
    def examination_and_approval(self):

        res = super(MhpMhp, self).examination_and_approval()
        
        self.sudo().set_practical_material()

        return res

    # 继承回退方法
    def state_fallback(self):

        res = super(MhpMhp, self).state_fallback()

        self.sudo().set_practical_material()

        return res



class TotalCost(models.Model):
    """ 继承总成本"""
    _inherit = 'total_cost'

    man_hour_cost = fields.Float(string="工时成本", compute="set_man_hour_cost", store=True)
    @api.depends('mhp_mhp_id', 'mhp_mhp_id.totle_price', 'mhp_mhp_id.cc_totle_price', 'mhp_mhp_id.hd_totle_price')
    def set_man_hour_cost(self):
        for record in self:
            if record.mhp_mhp_id:
                record.man_hour_cost = record.mhp_mhp_id.totle_price + record.mhp_mhp_id.cc_totle_price + record.mhp_mhp_id.hd_totle_price
            else:
                record.man_hour_cost = 0


    unit_cost = fields.Float(string="单件成本", compute="set_unit_cost", store=True)
    # @api.depends('practical_material_cost', 'man_hour_cost', 'number')
    def set_unit_cost(self):
        for record in self:
            if record.number:
                record.unit_cost = (record.practical_material_cost / record.number) + record.man_hour_cost
            else:
                record.unit_cost = 0

    total_cost = fields.Float(string="总成本", compute="set_total_cost", store=True)
    @api.depends('practical_material_cost', 'man_hour_cost', 'number')
    def set_total_cost(self):
        for record in self:
            record.total_cost = record.practical_material_cost + (record.man_hour_cost * record.number)
    