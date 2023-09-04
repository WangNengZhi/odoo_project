from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta



class Fixedassetprocurement(models.Model):
    _name = 'fixed_asset_procurement'
    _description = '固定资产采购台账'
    _order = "date desc"


    date = fields.Date(string="采购日期")
    property_name = fields.Char(string="资产名称")
    type = fields.Char(string="规格型号")
    contract_number = fields.Float(string="合同编码")
    procurement_price = fields.Float(string="采购金额")
    supplier_name = fields.Char(string="供应商名称")
    invoice_number = fields.Char(string="发票号码")
    warranty_period_date = fields.Char(string="保修期限")
    expected_service_date = fields.Char(string="预计使用年限")
    department_name = fields.Char(string="采购部门")
    procurement_personnel_name = fields.Char(string="采购人员")
    notes = fields.Char(string="备注")
    month = fields.Char(string='日期月份')
    year = fields.Char(string='日期年份')
    def get_fixed_asset_procurement(self):
        # first_day_month = datetime(today.year, today.month, 1)
        # first_day_year = datetime(today.year, 1, 1)
        # last_month_firstday = first_day_month - relativedelta(months=1)
        # last_month_lostday = first_day_month - timedelta(days=1)
        #机修采购信息获取
        maintain_procurement_dates = self.env['maintain_procurement'].sudo().search([('state', '=', '已采购')])
        for maintain_procurement_date in maintain_procurement_dates:
            maintain_procurement_date_old = self.env['fixed_asset_procurement'].sudo().search([('date', '=', maintain_procurement_date.date),
                                                                                            ('property_name', '=', maintain_procurement_date.material_name),
                                                                                            ('type', '=', maintain_procurement_date.specification),
                                                                                            ('procurement_price', '=', maintain_procurement_date.money_sum),
                                                                                            ])
            if not maintain_procurement_date_old:
                data = {
                     'date' :maintain_procurement_date.date,
                     'property_name' :maintain_procurement_date.material_name,
                     'type' :maintain_procurement_date.specification,

                     'procurement_price' :maintain_procurement_date.money_sum,
                     'supplier_name' :maintain_procurement_date.supplier_supplier_id.supplier_name,

                     'department_name' :maintain_procurement_date.department_name,
                     'procurement_personnel_name' :maintain_procurement_date.manager.name,
                     'month' :maintain_procurement_date.date.strftime("%Y-%m"),
                     'year' :maintain_procurement_date.date.strftime("%Y"),
            
                }      
                #self.env['fabric_ingredients_account_month'].sudo().search([('type', '=', month_date_type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
                self.sudo().create(data)
        #办公室用品采购
        office_procurement_enter_dates = self.env['office_procurement_enter'].sudo().search([('state', '=', '已采购')])
        for office_procurement_enter_date in office_procurement_enter_dates:
            office_procurement_enter_date_old = self.env['fixed_asset_procurement'].sudo().search([('date', '=', office_procurement_enter_date.date),
                                                                                            ('property_name', '=', office_procurement_enter_date.material_name),
                                                                                            ('type', '=', office_procurement_enter_date.specification),
                                                                                            ('procurement_price', '=', office_procurement_enter_date.money_sum),
                                                                                            ])
            if not office_procurement_enter_date_old:
                if not office_procurement_enter_date.admin_department:
                    office_procurement_enter_date.admin_department.name = '无'
                data = {
                     'date' :office_procurement_enter_date.date,
                     'property_name' :office_procurement_enter_date.material_name,
                     'type' :office_procurement_enter_date.specification,

                     'procurement_price' :office_procurement_enter_date.money_sum,
                     'supplier_name' :office_procurement_enter_date.supplier_supplier_id.supplier_name,

                     'department_name' :office_procurement_enter_date.admin_department.name,
                     'procurement_personnel_name' :office_procurement_enter_date.manager.name,
                     'notes' :office_procurement_enter_date.remark,
                     'month' :office_procurement_enter_date.date.strftime("%Y-%m"),
                     'year' :office_procurement_enter_date.date.strftime("%Y"),
            
                }      
                #self.env['fabric_ingredients_account_month'].sudo().search([('type', '=', month_date_type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
                self.sudo().create(data)
        #面辅料采购盘点
        fabric_ingredients_procurement_dates = self.env['fabric_ingredients_procurement'].sudo().search([('state', '=', '已采购')])
        for fabric_ingredients_procurement_date in fabric_ingredients_procurement_dates:
            fabric_ingredients_procurement_date_old = self.env['fixed_asset_procurement'].sudo().search([('date', '=', fabric_ingredients_procurement_date.date),
                                                                                            ('property_name', '=', fabric_ingredients_procurement_date.material_name),
                                                                                            ('type', '=', fabric_ingredients_procurement_date.specification),
                                                                                            ('procurement_price', '=', fabric_ingredients_procurement_date.money_sum),
                                                                                            ])
            if not fabric_ingredients_procurement_date_old:
                data = {
                     'date' :fabric_ingredients_procurement_date.date,
                     'property_name' :fabric_ingredients_procurement_date.material_name,
                     'type' :fabric_ingredients_procurement_date.specification,

                     'procurement_price' :fabric_ingredients_procurement_date.money_sum,
                     'supplier_name' :fabric_ingredients_procurement_date.supplier_supplier_id.supplier_name,

                     'department_name' :fabric_ingredients_procurement_date.department_name,
                     'procurement_personnel_name' :fabric_ingredients_procurement_date.manager.name,
                     'notes' :fabric_ingredients_procurement_date.remark,
                     'month' :fabric_ingredients_procurement_date.date.strftime("%Y-%m"),
                     'year' :fabric_ingredients_procurement_date.date.strftime("%Y"),
            
                }      
                #self.env['fabric_ingredients_account_month'].sudo().search([('type', '=', month_date_type), ('month', '=', today.month), ('year', '=', today.year)]).write(data)
                self.sudo().create(data)