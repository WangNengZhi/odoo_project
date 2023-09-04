from odoo import models, fields, api

class OutsourcePlantProcessType(models.Model):
    _name = 'outsource_plant_process_type'
    _description = 'FSN外发工厂加工类型'


    name = fields.Char(string="类型名称", required=True)


class OutsourcePlantProductionLineType(models.Model):
    _name = 'outsource_plant_pl_type'
    _description = 'FSN外发工厂生产线类型'


    name = fields.Char(string="类型名称", required=True)


class OutsourcePlantResourcesType(models.Model):
    _name = 'outsource_plant_resources_type'
    _description = 'FSN外发工厂资源类型'


    name = fields.Char(string="资源名称", required=True)
    unit = fields.Char(string="单位")