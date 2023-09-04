from odoo.exceptions import ValidationError
from odoo import models, fields, api


class FollowingProcessDetail(models.Model):
    _name = 'following_process_detail'
    _description = '后道进出明细'
    _order = 'dDate'
    _rec_name = "dDate"


    '''
        车间生产: 当天的组产值总数。
        中查退修: 当天的中查返修数。
        总检退修: 在总检中的全部退修数。
        仓库退修: 在返修产值中的全部件数。
        后道入库: 在后道产值中的全部件数。
        滞留: 滞留 = 车间生产 + 仓库退修 + 后道入库
    '''


    
    dDate = fields.Date(string='日期')
    workshop_production = fields.Integer(string="车间生产")
    middle_check_return = fields.Integer(string="中查退修", compute="set_middle_check_return", store=True)
    always_check_return = fields.Integer(string="总检退修", compute="set_always_check_return", store=True)
    warehouse_return = fields.Integer(string="仓库退修")
    following_process_enter = fields.Integer(string="后道入库")
    retention_quantity = fields.Integer(string="滞留", compute="set_retention_quantity", store=True)
    retention_total = fields.Integer(string="滞留累计", compute="set_retention_total", store=True)

    middle_check_return_ids = fields.One2many("middle_check_return_line", "following_process_detail_id", string="中查退修明细")
    always_check_return_ids = fields.One2many("always_check_return_line", "following_process_detail_id", string="总检退修明细")


    # 计算滞留累计
    @api.depends('retention_quantity')
    def set_retention_total(self):
        for record in self:

            following_process_detail_objs = self.sudo().search([
                ("dDate", "<=", record.dDate)
            ])

            tem_retention_total = 0
            for following_process_detail_obj in following_process_detail_objs:
                tem_retention_total = tem_retention_total + following_process_detail_obj.retention_quantity

            record.retention_total = tem_retention_total


    # 设置滞留
    @api.depends('workshop_production', 'warehouse_return', 'following_process_enter')
    def set_retention_quantity(self):
        for record in self:
            record.retention_quantity = record.workshop_production + record.warehouse_return - record.following_process_enter


    # 设置中查退修
    @api.depends('middle_check_return_ids', 'middle_check_return_ids.quantity')
    def set_middle_check_return(self):
        for record in self:
            
            tem_middle_check_return = 0     # 临时中查退修

            for line in record.middle_check_return_ids:
                tem_middle_check_return = tem_middle_check_return + line.quantity
            
            record.middle_check_return = tem_middle_check_return


    # 设置总检退修
    @api.depends('always_check_return_ids', 'always_check_return_ids.quantity')
    def set_always_check_return(self):
        for record in self:
            
            tem_always_check_return = 0     # 临时总检退修

            for line in record.always_check_return_ids:
                tem_always_check_return = tem_always_check_return + line.quantity
            
            record.always_check_return = tem_always_check_return


    # 获取当天组产值中的款号列表
    def get_pro_pro_style_number_list(self):

        tem_style_number_list = []  # 临时款号列表

        pro_pro_objs = self.env["pro.pro"].sudo().search([
            ("date", "=", self.dDate),
        ])

        for pro_pro_obj in pro_pro_objs:
            tem_style_number_list.append(pro_pro_obj.style_number.id)

        tem_style_number_list = list(set(tem_style_number_list))
    
        return tem_style_number_list


    # 设置车间生产
    def set_workshop_production(self):
        for record in self:

            pro_pro_objs = self.env["pro.pro"].sudo().search([
                ("date", "=", record.dDate),
            ])

            tem_workshop_production = 0

            for pro_pro_obj in pro_pro_objs:
                tem_workshop_production = tem_workshop_production + pro_pro_obj.number

            record.workshop_production = tem_workshop_production




    # 设置仓库退修
    def set_warehouse_return(self):
        for record in self:

            # 获取当天组产值中的款号列表
            # tem_style_number_list = record.get_pro_pro_style_number_list()

            repair_value_objs = self.env["repair_value"].sudo().search([
                ("date", "=", record.dDate),
                # ("style_number", "in", tem_style_number_list)
            ])

            tem_warehouse_return = 0    # 临时仓库返修

            for repair_value_obj in repair_value_objs:
                tem_warehouse_return = tem_warehouse_return + repair_value_obj.number
            
            record.warehouse_return = tem_warehouse_return


    # 设置后道入库
    def set_following_process_enter(self):
        for record in self:

            # 获取当天组产值中的款号列表
            # tem_style_number_list = record.get_pro_pro_style_number_list()

            posterior_passage_output_value_objs = self.env["posterior_passage_output_value"].sudo().search([
                ("date", "=", record.dDate),
                # ("style_number", "in", tem_style_number_list)
            ])

            tem_following_process_enter = 0     # 临时后道入库

            for posterior_passage_output_value_obj in posterior_passage_output_value_objs:
                tem_following_process_enter = tem_following_process_enter + posterior_passage_output_value_obj.number

            record.following_process_enter = tem_following_process_enter



    def all_in(self):
        for record in self:

            record.set_workshop_production()    # 车间

            record.set_warehouse_return()   # 仓库

            record.set_following_process_enter()    # 后道入库

            # record.set_middle_check_return()    # 设置中查
            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.dDate)
            ])
            for general_general_obj in general_general_objs:
                general_general_obj.sudo().set_following_process_detail()

            # record.always_check_return_ids.    # 设置总检
            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", "=", record.dDate)
            ])
            for invest_invest_obj in invest_invest_objs:
                invest_invest_obj.sudo().set_following_process_detail()



class MiddleCheckReturnLine(models.Model):
    _name = 'middle_check_return_line'
    _description = '后道进出中查退修明细'


    following_process_detail_id = fields.Many2one("following_process_detail", string="后道进出明细", ondelete="cascade")
    dDate = fields.Date(related="following_process_detail_id.dDate", string="日期", store=True)
    gGroup = fields.Char(string="组别")
    quantity = fields.Integer(string="数量")


    # 设置中查退修
    def set_middle_check_return(self):
        for record in self:

            invest_invest_objs = self.env["invest.invest"].sudo().search([
                ("date", "=", record.dDate),
                ("group", "=", record.gGroup),
            ])

            tem_quantity = 0

            for invest_invest_obj in invest_invest_objs:
                tem_quantity = tem_quantity + invest_invest_obj.repairs_number

            record.quantity = tem_quantity



class AlwaysCheckReturnLine(models.Model):
    _name = 'always_check_return_line'
    _description = '后道进出总检退修明细'


    following_process_detail_id = fields.Many2one("following_process_detail", string="总检进出明细", ondelete="cascade")
    dDate = fields.Date(related="following_process_detail_id.dDate", string="日期", store=True)
    gGroup = fields.Char(string="组别")
    quantity = fields.Integer(string="数量")


    # 获取当天组产值中的款号列表
    def get_pro_pro_style_number_list(self):

        tem_style_number_list = []  # 临时款号列表

        pro_pro_objs = self.env["pro.pro"].sudo().search([
            ("date", "=", self.dDate),
        ])

        for pro_pro_obj in pro_pro_objs:
            tem_style_number_list.append(pro_pro_obj.style_number.id)

        tem_style_number_list = list(set(tem_style_number_list))
    
        return tem_style_number_list


    # 设置总检退修
    def set_always_check_return(self):
        for record in self:

            # 获取当天组产值中的款号列表
            # tem_style_number_list = record.get_pro_pro_style_number_list()

            general_general_objs = self.env["general.general"].sudo().search([
                ("date", "=", record.dDate),
                ("group", "=", record.gGroup),
                # ("item_no", "in", tem_style_number_list)
            ])

            tem_quantity = 0     # 临时总检数量

            for general_general_obj in general_general_objs:
                tem_quantity = tem_quantity + general_general_obj.repair_number

            record.quantity = tem_quantity





