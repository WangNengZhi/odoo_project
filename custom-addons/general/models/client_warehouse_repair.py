from odoo import models, fields, api
import calendar, datetime


class ClientWarehouseRepair(models.Model):
    _name = 'client_warehouse_repair'
    _description = '客户仓库返修'
    _rec_name = 'style_number'
    # _order = "style_number desc"


    month = fields.Char(string="月份")
    # date = fields.Date(string="日期")
    style_number = fields.Many2one('ib.detail', string='款号')
    repair_amount = fields.Float(string="返修件数")
    repair_scene = fields.Float(string="现场返修件数")
    repair_value = fields.Float(string="返修产值", compute="set_repair_value", store=True)
    workshop_amount = fields.Float(string="车间件数")
    repair_proportion = fields.Float(string="返修率", compute="set_repair_proportion", store=True)
    repair_group_line_ids = fields.One2many("repair_group_line", "client_warehouse_repair_id", string="返修组别")
    assess_index = fields.Float(string="考核", compute="set_repair_proportion", store=True)



    # 计算月的第一天和最后一天
    def compute_start_and_end(self):

        if self.month:
            # 获取当前月份的第一天和最后一天
            date_list = self.month.split("-")
            date_year = int(date_list[0])
            date_month = int(date_list[1])
            last_day = calendar.monthrange(date_year, date_month)[1]## 最后一天
            start = datetime.date(date_year, date_month, 1)
            end = datetime.date(date_year, date_month, last_day)

            return {"start": start, "end": end}


    # 设置返修率
    @api.depends('repair_amount', 'repair_scene', 'workshop_amount')
    def set_repair_proportion(self):
        for record in self:
            if record.workshop_amount:
                # 返修率
                record.repair_proportion = ((record.repair_amount + record.repair_scene) / record.workshop_amount) * 100
            else:
                record.repair_proportion = 0
            
            if (record.repair_amount + record.repair_scene):
                # 考核
                record.assess_index = 2 * ((record.repair_amount + record.repair_scene) - (record.workshop_amount * 0.03))
            else:
                record.assess_index = 0
        
    
    # 设置返修产值
    @api.depends('repair_amount', 'repair_scene', 'style_number', 'style_number.price')
    def set_repair_value(self):
        for record in self:
            record.repair_value = (record.repair_amount + record.repair_scene) * record.style_number.price

    


    # 设置客户仓库返修统计数据
    def set_data(self):

        for record in self:

            # 获取一个月的开始实际和结束实际
            date_dict = self.compute_start_and_end()   
            
            # 查询返修产值表
            repair_value_objs = self.env["repair_value"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("style_number", "=", record.style_number.id),
            ])
            # 临时返修数
            tem_repair_amount = 0
            # 临时现场返修
            tem_repair_scene = 0
            # 临时返修产值
            tem_repair_value = 0
            # 组别
            repair_group_list = []

            for repair_value_obj in repair_value_objs:

                if repair_value_obj.repair_type == "现场返修":
                    tem_repair_scene = tem_repair_scene + repair_value_obj.number
                else:
                    tem_repair_amount = tem_repair_amount + repair_value_obj.number
                # 临时返修产值
                tem_repair_value = tem_repair_value + repair_value_obj.pro_value
                
                # repair_value_obj.repair_value_group_line_ids

                for group_line in repair_value_obj.repair_value_group_line_ids:
                    line = {
                        "name": group_line.name
                    }
                    repair_group_list.append((0, 0, line))
            

            # 查询组产值表
            pro_pro_objs = self.env["pro.pro"].sudo().search([
                ("date", ">=", date_dict['start']),
                ("date", "<=", date_dict['end']),
                ("style_number", "=", record.style_number.id),
            ])
            # 临时车间数量
            tem_repair_quantity = 0
            for pro_pro_obj in pro_pro_objs:
                tem_repair_quantity = tem_repair_quantity + pro_pro_obj.number

            record.repair_group_line_ids = repair_group_list
            record.repair_scene = tem_repair_scene
            record.repair_amount = tem_repair_amount
            record.workshop_amount = tem_repair_quantity



        


    @api.model
    def create(self, vals):

        instance = super(ClientWarehouseRepair, self).create(vals)

    
        return instance



class RepairGroupLine(models.Model):
    _name = 'repair_group_line'
    _description = '款号汇总返修组别明细'
    # _rec_name = "name"
    _order = "name"

    client_warehouse_repair_id = fields.Many2one("client_warehouse_repair", ondelete="cascade")
    name = fields.Char(string="名称")

    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        repair_value_group_obj = self.env["repair_group_line"].sudo().search([
            ("client_warehouse_repair_id", "=", vals["client_warehouse_repair_id"]),
            ("name", "=", vals["name"])
            ])
        if repair_value_group_obj:
            repair_value_group_obj.unlink()
            

        instance = super(RepairGroupLine, self).create(vals)
    
        return instance