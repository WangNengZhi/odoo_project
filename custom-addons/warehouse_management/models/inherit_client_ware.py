from cmath import rect
from odoo import models, fields, api
from odoo.exceptions import ValidationError



class FinishedProductWareLine(models.Model):
    ''' 继承仓库入库出库明细'''
    _inherit = 'finished_product_ware_line'

    def set_client_ware(self):
        self.env["client_ware"].sudo().search([
            ("dDate", "=", self.date),
            ("style_number", "=", self.style_number.id)
        ])

    def state_back(self):

        res = super(FinishedProductWareLine, self).state_back()



        return res

    def state_confirm(self):

        res = super(FinishedProductWareLine, self).state_confirm()

        # for record in self:
        #     if record.type == "入库" and record.quality == "次品":
        #         self.env["client_ware"].sudo().create({
        #             "dDate": record.date,
        #             "style_number": record.style_number.id,
        #             "repair_number": record.number
        #         })

        return res