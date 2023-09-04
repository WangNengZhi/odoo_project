from odoo import models, fields, api
import calendar, datetime
from calendar import monthrange

class GeneralGeneral(models.Model):
    '''总检'''
    _inherit = 'general.general'

    middle_check_month_efficiency_id = fields.Many2one("middle_check_month_efficiency", string="中查月效率表")


    def set_middle_check_month_efficiency(self):
        for record in self:

            year, month, _ = str(record.date).split("-")
            year_month = f"{year}-{month}"
            middle_check_month_efficiency_obj = self.env['middle_check_month_efficiency'].sudo().search([
                ("month", "=", year_month),
                ("group", "=", record.group),
                ("style_number", "=", record.item_no.id),
                ("invest", "=", record.invest)
            ])
            if not middle_check_month_efficiency_obj:
                middle_check_month_efficiency_obj = self.env['middle_check_month_efficiency'].sudo().create({
                    "month": year_month,
                    "group": record.group,
                    "style_number": record.item_no.id,
                    "invest": record.invest
                })
            
            record.middle_check_month_efficiency_id = middle_check_month_efficiency_obj.id

            middle_check_month_efficiency_obj.sudo().set_middle_check_ids()

            middle_check_month_efficiency_obj.sudo().set_dg_ids()

            middle_check_month_efficiency_obj.sudo().set_pro_pro_ids()

            middle_check_month_efficiency_obj.sudo().set_dg_repair_ids()
            

    @api.model
    def create(self, vals):

        res = super(GeneralGeneral, self).create(vals)

        res.sudo().set_middle_check_month_efficiency()

        return res

class InvestInvest(models.Model):
    '''中查'''
    _inherit = 'invest.invest'

    def set_middle_check_month_efficiency(self):
        for record in self:

            year, month, _ = str(record.date).split("-")
            year_month = f"{year}-{month}"
            print(year_month)

            middle_check_month_efficiency_objs = self.env['middle_check_month_efficiency'].sudo().search([
                ("month", "=", year_month),
                ("group", "=", record.group),
                ("style_number", "=", record.style_number.id),
                ("invest", "=", record.invest)
            ])
            if middle_check_month_efficiency_objs:
                for middle_check_month_efficiency_obj in middle_check_month_efficiency_objs:
                    middle_check_month_efficiency_obj.middle_check_ids = [(4, record.id)]
                    print(middle_check_month_efficiency_obj.middle_check_ids,record.id)


    @api.model
    def create(self, vals):
        print('伊玛达就是现在')

        res = super(InvestInvest, self).create(vals)
        print(res)
        res.sudo().set_middle_check_month_efficiency()

        return res



class product(models.Model):
    """ 继承组产值"""
    _inherit = 'pro.pro'


    def set_middle_check_month_efficiency(self):
        for record in self:

            year, month, _ = str(record.date).split("-")
            year_month = f"{year}-{month}"

            middle_check_month_efficiency_objs = self.env['middle_check_month_efficiency'].sudo().search([
                ("month", "=", year_month),
                ("group", "=", record.group),
                ("style_number", "=", record.style_number.id),
            ])
            if middle_check_month_efficiency_objs:
                for middle_check_month_efficiency_obj in middle_check_month_efficiency_objs:
                    middle_check_month_efficiency_obj.pro_pro_ids = [(4, record.id)]


    @api.model
    def create(self, vals):

        res = super(product, self).create(vals)

        res.sudo().set_middle_check_month_efficiency()

        return res



class MiddleCheckMonthEfficiency(models.Model):
    _name = 'middle_check_month_efficiency'
    _description = '中查月效率表'
    _rec_name = 'month'
    _order = "month desc"


    month = fields.Char(string="月份")
    group = fields.Char(string='组别')
    invest = fields.Char(string='中查')
    style_number = fields.Many2one('ib.detail', string='款号')

    general_ids = fields.One2many("general.general", "middle_check_month_efficiency_id", string="总检")

    repair_number = fields.Float(string="总检返修数量", compute="set_general_info", store=True)
    general_number = fields.Float(string="总检查货数量", compute="set_general_info", store=True)

    quadratic_repair_number = fields.Float(string="二次返修数量", compute="set_general_info", store=True)
    quadratic_general_number = fields.Float(string="二次查货数量", compute="set_general_info", store=True)


    #_inherit = 'invest.invest'

    def update_middle_check_month_efficiency(self):
        #print(self.invest)
        #year, month = str(self.month).split("-")
        year, month = map(int, self.month.split("-"))   
        this_month_start, this_month_end = self.set_begin_and_end(year, month)
        invest_objs = self.env['invest.invest'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("invest", "=", self.invest),
                ])
        for invest_obj in invest_objs:
            year, month, _ = str(invest_obj.date).split("-")
            year_month = f"{year}-{month}"
            middle_check_month_efficiency_objs = self.env['middle_check_month_efficiency'].sudo().search([
                ("month", "=", year_month),
                ("group", "=", invest_obj.group),
                ("style_number", "=", invest_obj.style_number.id),
                ("invest", "=", invest_obj.invest)
            ])

            invest_objs_data = self.env['invest.invest'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", invest_obj.group),
                    ("invest", "=", invest_obj.invest),
                    ("style_number", "=", invest_obj.style_number.id)
            ])
            general_ids_data = self.env['general.general'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", invest_obj.group),
                    ("invest", "=", invest_obj.invest),
                    ("item_no", "=", invest_obj.style_number.id)
            ])
            
            pro_pro_objs = self.env['pro.pro'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", invest_obj.group),
                    ("style_number", "=", invest_obj.style_number.id)
                ])
            
            data = {
                   'middle_check_ids':invest_obj,
                   'month':year_month,
                   "invest" : invest_obj.invest,
                   "group" :invest_obj.group,
                   "style_number" : invest_obj.style_number.id,
                   'middle_check_ids':invest_objs_data,
                   "general_ids":general_ids_data,
                   'pro_pro_ids':pro_pro_objs

                }
            if not middle_check_month_efficiency_objs:
                #print(data)
                self.sudo().create(data)
                self.sudo().set_dg_ids()
                self.sudo().set_dg_repair_ids()
            else:
                middle_check_month_efficiency_objs.sudo().update(data)
                middle_check_month_efficiency_objs.sudo().set_dg_ids()
                middle_check_month_efficiency_objs.sudo().set_dg_repair_ids()
    @api.depends("general_ids", "general_ids.repair_number", "general_ids.general_number", "general_ids.secondary_repair_number", "general_ids.secondary_check_number")
    def set_general_info(self):
        for record in self:
            repair_number = 0
            general_number = 0
            quadratic_repair_number = 0
            quadratic_general_number = 0
            for i in record.general_ids:
                repair_number += i.repair_number
                general_number += i.general_number
                quadratic_repair_number += i.secondary_repair_number
                quadratic_general_number += i.secondary_check_number
            
            record.repair_number = repair_number
            record.general_number = general_number
            record.quadratic_repair_number = quadratic_repair_number
            record.quadratic_general_number = quadratic_general_number
    def update_general_info(self):
        year, month = map(int, self.month.split("-"))   
        this_month_start, this_month_end = self.set_begin_and_end(year, month)
        general_objs = self.env['general.general'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", self.group),
                    ("invest", "=", self.invest),
                    ("item_no", "=", self.style_number.id)
                ])
        for general_obj in general_objs:
            self.general_ids += general_obj
        # for record in self:

        #     print(record.general_ids)
        #     repair_number = 0
        #     general_number = 0
        #     quadratic_repair_number = 0
        #     quadratic_general_number = 0
        #     for i in record.general_ids:
        #         repair_number += i.repair_number
        #         general_number += i.general_number
        #         quadratic_repair_number += i.secondary_repair_number
        #         quadratic_general_number += i.secondary_check_number
            
        #     record.repair_number = repair_number
        #     record.general_number = general_number
        #     record.quadratic_repair_number = quadratic_repair_number
        #     record.quadratic_general_number = quadratic_general_number
        #     print(repair_number,general_number,quadratic_repair_number,quadratic_general_number)
    
    middle_check_ids = fields.Many2many("invest.invest", string="中查")
    middle_check_number = fields.Integer(string="中查查货数", compute="set_middle_check_number", store=True)
    middle_repairs_number = fields.Integer(string="中查返修数", compute="set_middle_check_number", store=True)
    @api.depends('middle_check_ids', 'middle_check_ids.check_the_quantity')
    def set_middle_check_number(self):
        for record in self:
            record.middle_check_number = sum(record.middle_check_ids.mapped("check_the_quantity"))
            record.middle_repairs_number = sum(record.middle_check_ids.mapped("repairs_number"))
    def update_middle_check_number(self):
        year, month = map(int, self.month.split("-"))   
        this_month_start, this_month_end = self.set_begin_and_end(year, month)
        invest_objs = self.env['invest.invest'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", self.group),
                    ("invest", "=", self.invest),
                    ("style_number", "=", self.style_number.id)
                ])
        self.middle_check_number = sum(invest_objs.mapped("check_the_quantity"))
        self.middle_repairs_number = sum(invest_objs.mapped("repairs_number"))
        # print(sum(invest_objs.mapped("check_the_quantity")))
        # print(sum(invest_objs.mapped("repairs_number")))

    manual_omission_ratio = fields.Float(string="手动返修率", compute="set_manual_omission_ratio", store=True, group_operator='avg')
    @api.depends('middle_repairs_number', 'middle_check_number')
    def set_manual_omission_ratio(self):
        for record in self:
            if record.middle_check_number:
                record.manual_omission_ratio = record.middle_repairs_number / record.middle_check_number
            else:
                record.manual_omission_ratio = 0

    manual_repair_ratio = fields.Float(string="手动漏查率", compute="set_manual_repair_ratio", store=True, group_operator='avg')
    @api.depends('repair_number', 'middle_check_number')
    def set_manual_repair_ratio(self):
        for record in self:
            if record.middle_check_number:
                record.manual_repair_ratio = record.repair_number / record.middle_check_number
            else:
                record.manual_repair_ratio = 0

    punishment = fields.Float(string="扣款", compute="set_punishment", store=True)
    @api.depends("repair_number")
    def set_punishment(self):
        for record in self:
            record.punishment = record.repair_number * 2

    pro_pro_ids = fields.Many2many("pro.pro", string="组产值")
    deliveries_number = fields.Integer(string="组上交货件数", compute="set_deliveries_number", store=True)
    @api.depends('pro_pro_ids', 'pro_pro_ids.number')
    def set_deliveries_number(self):
        for record in self:
            record.deliveries_number = sum(record.pro_pro_ids.mapped("number"))


    dg_ids = fields.Many2many("suspension_system_station_summary",
        relation='mcme_ssss',
        column1='middle_check_month_efficiency_id',
        column2='suspension_system_station_summary_id',
        string="吊挂")
    dg_group_number = fields.Integer(string="吊挂生产件数", compute="set_dg_group_number", store=True)
    @api.depends('dg_ids', 'dg_ids.total_quantity')
    def set_dg_group_number(self):
        for record in self:
            record.dg_group_number = sum(record.dg_ids.mapped("total_quantity"))


    auto_repair_number = fields.Integer(string="返修件数", compute="set_auto_repair_number", store=True)
    @api.depends('dg_group_number', 'deliveries_number')
    def set_auto_repair_number(self):
        for record in self:
            auto_repair_number = record.dg_group_number - record.deliveries_number
            if auto_repair_number > 0:
                record.auto_repair_number = auto_repair_number
            else:
                record.auto_repair_number = 0
    
    auto_repair_ratio = fields.Float(string="自动返修率", compute="set_auto_repair_ratio", store=True, group_operator='avg')
    @api.depends('dg_group_number', 'auto_repair_number')
    def set_auto_repair_ratio(self):
        for record in self:
            if record.dg_group_number:
                record.auto_repair_ratio = record.auto_repair_number / record.dg_group_number
            else:
                record.auto_repair_ratio = 0


    dg_repair_ids = fields.Many2many("suspension_system_rework", string="吊挂返修")
    dg_repair_number = fields.Integer(string="吊挂漏查件数", compute="set_dg_repair_number", store=True)
    @api.depends('dg_repair_ids', 'dg_repair_ids.number')
    def set_dg_repair_number(self):
        for record in self:
            record.dg_repair_number = sum(record.dg_repair_ids.mapped("number"))
            

    dg_rate_repair = fields.Float(string="吊挂漏查率", compute="set_dg_rate_repair", store=True, group_operator='avg')
    @api.depends('dg_repair_number', 'dg_group_number')
    def set_dg_rate_repair(self):
        for record in self:
            if record.dg_group_number:
                record.dg_rate_repair = record.dg_repair_number / record.dg_group_number
            else:
                record.dg_rate_repair = 0




    def set_begin_and_end(self, year, month):
        ''' 获取当月第一天和最后一天'''

        this_month_start = datetime.datetime(year, month, 1).date()
        this_month_end = datetime.datetime(year, month, calendar.monthrange(year, month)[1]).date()

        return this_month_start, this_month_end



    def set_pro_pro_ids(self):
        ''' 设置组上交货记录'''
        for record in self:
            if record.month and record.group and record.style_number:

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                pro_pro_objs = self.env['pro.pro'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", record.group),
                    ("style_number", "=", record.style_number.id)
                ])
                if pro_pro_objs:
                    record.pro_pro_ids = [(6, 0, pro_pro_objs.ids)]


    def set_dg_ids(self):
        ''' 设置吊挂生产记录'''

        map_groups = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            "整件一组": "整件一组",
        }

        for record in self:
            if record.month and record.style_number and record.group and record.invest:

                check_position_settings_obj = self.env['check_position_settings'].sudo().search([
                    ("group", "=", map_groups.get(record.group)),
                    ("department_id", "=", "车间")
                ])

                emp_obj = self.env['hr.employee'].sudo().search([("name", "=", record.invest)])

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                suspension_system_station_summary_objs = self.env['suspension_system_station_summary'].sudo().search([
                    ("dDate", ">=", this_month_start),
                    ("dDate", "<=", this_month_end),
                    ("group", "=", check_position_settings_obj.id),
                    ("employee_id", "=", emp_obj.id),
                    ("style_number", "=", record.style_number.id),
                    ("station_number", "in", check_position_settings_obj.mapped('position_line_ids.position'))
                ])

                if suspension_system_station_summary_objs:
                    record.dg_ids = [(6, 0, suspension_system_station_summary_objs.ids)]


    def set_dg_repair_ids(self):
        ''' 设置吊挂返修记录'''

        map_groups = {
            "1": "车缝一组",
            "2": "车缝二组",
            "3": "车缝三组",
            "4": "车缝四组",
            "5": "车缝五组",
            "6": "车缝六组",
            "7": "车缝七组",
            "8": "车缝八组",
            "9": "车缝九组",
            "10": "车缝十组",
            "整件一组": "整件一组",
        }

        for record in self:

            if record.month and record.style_number and record.group and record.invest:


                check_position_settings_obj = self.env['check_position_settings'].sudo().search([
                    ("group", "=", map_groups.get(record.group)),
                    ("department_id", "=", "车间")
                ])

                emp_obj = self.env['hr.employee'].sudo().search([("name", "=", record.invest)])

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                suspension_system_rework_objs = self.env['suspension_system_rework'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", check_position_settings_obj.id),
                    ("employee_id", "=", emp_obj.id),
                    ("style_number", "=", record.style_number.id),
                    ("qc_type", "=", "总检"),
                ])
                print(suspension_system_rework_objs)

                if suspension_system_rework_objs:
                    record.dg_repair_ids = [(6, 0, suspension_system_rework_objs.ids)]


    def set_middle_check_ids(self):
        for record in self:

            if record.month and record.group and record.style_number and record.invest:

                year, month = map(int, record.month.split("-"))
                
                this_month_start, this_month_end = self.set_begin_and_end(year, month)

                invest_objs = self.env['invest.invest'].sudo().search([
                    ("date", ">=", this_month_start),
                    ("date", "<=", this_month_end),
                    ("group", "=", record.group),
                    ("invest", "=", record.invest),
                    ("style_number", "=", record.style_number.id)
                ])
                if invest_objs:
                    record.middle_check_ids = [(6, 0, invest_objs.ids)]




