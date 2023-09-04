from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta



class CuttingBed(models.Model):
    _name = "cutting_bed"
    _description = '裁床产值'
    _rec_name = "date"
    _order = "date desc"

    cutting_bed_production_id = fields.Many2one("cutting_bed_production", string="裁床产量", ondelete="cascade")
    date = fields.Date('日期', required=True, compute="set_number", store=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True, compute="set_number", store=True)
    product_size = fields.Many2one("fsn_size", string="尺码", required=True, compute="set_number", store=True)
    week = fields.Char(string="周")
    number = fields.Integer('件数', compute="set_number", store=True)
    @api.depends('cutting_bed_production_id',\
        'cutting_bed_production_id.date',\
            'cutting_bed_production_id.order_number',\
                'cutting_bed_production_id.style_number',\
                    'cutting_bed_production_id.product_size',\
                        'cutting_bed_production_id.complete_productionp')
    def set_number(self):
        for record in self:
            if record.cutting_bed_production_id:

                record.write({
                    "date": record.cutting_bed_production_id.date,
                    "order_number": record.cutting_bed_production_id.order_number.id,
                    "style_number": record.cutting_bed_production_id.style_number.id,
                    "product_size": record.cutting_bed_production_id.product_size.id,
                    "number": record.cutting_bed_production_id.complete_productionp
                })

            else:
                record.number = 0
    num_people = fields.Integer('人数', required=True)
    pro_value = fields.Float('产值', compute="set_pro_value", store=True)
    cutting_bed_week_id = fields.Many2one('cutting_bed_week', string="裁床产值(周)")


    @api.constrains('date', "style_number")
    def _check_unique(self):
        for record in self:
            demo = self.env[record._name].sudo().search([
                ('date', '=', record.date),
                ("order_number", "=", record.order_number.id),
                ("style_number", "=", record.style_number.id),
                ("product_size", "=", record.product_size.id),
                ])
            if len(demo) > 1:
                raise ValidationError(f"已经存在日期为：{record.date}款号为：{record.style_number.style_number}的产值记录了！")


    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)






    def set_cutting_bed_week(self):
        for record in self:

            year = record.date.year
            week = record.date.isocalendar()
            week_name = f"{year}年第{week[1] + 1}周"


            cutting_bed_week_obj = self.env['cutting_bed_week'].search([("week", "=", week_name)])

            if not cutting_bed_week_obj:
                cutting_bed_week_obj = self.env['cutting_bed_week'].create({"week": week_name})
            record.cutting_bed_week_id = cutting_bed_week_obj.id


    @api.model
    def create(self, vals):

        instance = super(CuttingBed, self).create(vals)


        instance.set_cutting_bed_week()

        return instance






class CuttingBedWeek(models.Model):
    _name = 'cutting_bed_week'
    _description = '裁床产值(周)'
    _order = "week desc"

    cutting_bed_id = fields.One2many("cutting_bed", "cutting_bed_week_id", string="裁床产值")
    week = fields.Char('周')
    style_number = fields.Char('款号', compute="set_cutting_bed_week_info", store=True)
    number = fields.Integer('件数', compute="set_cutting_bed_week_info", store=True)
    pro_value = fields.Float('产值', compute="set_cutting_bed_week_info", store=True)
    num_people = fields.Integer('人数', compute="set_cutting_bed_week_info", store=True)


    @api.depends('cutting_bed_id', 'cutting_bed_id.num_people', 'cutting_bed_id.number')
    def set_cutting_bed_week_info(self):
        for record in self:
            record.style_number = ",".join(record.cutting_bed_id.mapped("style_number.style_number"))

            record.number = sum(record.cutting_bed_id.mapped("number"))

            record.pro_value = sum(record.cutting_bed_id.mapped("pro_value"))
            if record.cutting_bed_id:
                record.num_people = sum(record.cutting_bed_id.mapped("num_people")) / len(record.cutting_bed_id)
            else:

                record.num_people = 0
