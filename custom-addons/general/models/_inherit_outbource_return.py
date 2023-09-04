from odoo.exceptions import ValidationError
from odoo import models, fields, api

class GeneralGeneral(models.Model):
    '''继承总检'''
    _inherit = "general.general"


    def create_outbource_return(self):
        for record in self:

            tem_lst = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', "整件一组"]
            if record.group not in tem_lst:

                general_obj = self.env['hr.employee'].sudo().search([("name", "=", record.general1)])
                if general_obj:

                
                    self.env['outbource_return'].sudo().create({
                        "date": record.date,
                        "order_id": record.order_number_id.id,
                        "style_number": record.item_no.id,
                        "problem": record.problems,
                        "quality_inspection_id": general_obj.id,
                        "number": record.repair_number,
                        "general_general_id": record.id
                    })
                else:

                    raise ValidationError(f"{record.general1}总检名字错误！")
            




    @api.model
    def create(self, vals):

        instance = super(GeneralGeneral, self).create(vals)

        # instance.sudo().create_outbource_return()

        return instance


class OutbourceReturn(models.Model):
    _inherit = "outbource_return"

    general_general_id = fields.Many2one("general.general", string="总检", ondelete="cascade")