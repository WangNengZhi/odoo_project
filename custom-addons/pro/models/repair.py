from calendar import month
import inspect
from xmlrpc.client import SERVER_ERROR
from odoo.exceptions import ValidationError
from odoo import models, fields, api

from datetime import datetime, timedelta
import time

class RepairValue(models.Model):
    _name = "repair_value"
    _description = '返修产值'
    _rec_name = "date"
    _order = "date desc"


    date = fields.Date('日期', required=True)
    style_number = fields.Many2one('ib.detail', string='款号', required=True)
    # group = fields.Char(string="组别")
    week = fields.Char(string="周")
    number = fields.Integer('件数')
    # num_people = fields.Integer('人数', required=True)
    # avg_value = fields.Float('人均产值', compute="_set_avg_value", store=True)
    pro_value = fields.Float('产值', compute="set_pro_value", store=True)
    repair_value_week_id = fields.Many2one('repair_value_week', string="裁床产值(周)")
    repair_type = fields.Selection([('客户返修', '客户返修'),
                                    ('仓库返修', '仓库返修'),
                                    ('现场返修', '现场返修'),
                                    ], string="返修类型", required=True)
    repair_value_group_line_ids = fields.One2many("repair_value_group", "repair_value_id", string="返修组别", compute="set_repair_value_group_line_ids", store=True)



    # 设置后道进出明细
    def set_following_process_detail(self):
        following_process_detail_obj = self.env["following_process_detail"].sudo().search([
            ("dDate", "=", self.date)
        ])
        if following_process_detail_obj:
            following_process_detail_obj.set_warehouse_return()
        else:
            new_obj = following_process_detail_obj.create({
                "dDate": self.date
            })
            new_obj.set_warehouse_return()



    # 设置总检效率表(日)返修数量
    def set_always_check_eff_day(self):

        always_check_eff_day_objs = self.env["always_check_eff_day"].sudo().search([("dDate", "=", self.date)])
        if always_check_eff_day_objs:
            for always_check_eff_day_obj in always_check_eff_day_objs:
                always_check_eff_day_obj.sudo().set_repair_quantity()




    # 设置总检效率表返修数量
    def set_always_check_efficiency(self):

        style_number_line_objs = self.env["style_number_line"].sudo().search([
            ("name", "=", self.style_number.id)
        ])
        if style_number_line_objs:

            for style_number_line_obj in style_number_line_objs:
                style_number_line_obj.always_check_efficiency_id.sudo().set_repair_quantity()


    # 设置品控绩效记录
    def set_quality_control_performance(self):

        month = f"{self.date.year}-{self.date.month}"

        for repair_value_group_line_id in self.repair_value_group_line_ids:

            quality_control_performance_objs = self.env["quality_control_performance"].sudo().search([
                ("month", "=", month),
                ("group", "=", repair_value_group_line_id.name)
            ])
            if quality_control_performance_objs:

                quality_control_performance_objs.sudo().set_assess_index()
            
            else:
                now_obj = self.env["quality_control_performance"].sudo().create({
                    "month": month,
                    "group": repair_value_group_line_id.name
                })
                now_obj.sudo().set_assess_index()


    # 设置返修组别
    @api.depends('style_number')
    def set_repair_value_group_line_ids(self):
        for record in self:
            tem_group_list = []
            pro_pro_objs = self.env["pro.pro"].sudo().search([
                ("style_number", "=", record.style_number.id)
            ])
            for pro_pro_obj in pro_pro_objs:
                tem_group_list.append(pro_pro_obj.group)
            # 列表去重
            tem_group_list = list(set(tem_group_list))

            repair_group_list = []
            for tem_group in tem_group_list:
                line = {
                    "name": tem_group
                }
                repair_group_list.append((0, 0, line))
            
            record.repair_value_group_line_ids = repair_group_list



    @api.constrains('date', "style_number", "repair_type")
    def _check_unique(self):
        demo = self.env[self._name].sudo().search([
            ('date', '=', self.date),
            ("order_number", "=", self.order_number.id),
            ("style_number", "=", self.style_number.id),
            ("repair_type", "=", self.repair_type),
            ])
        if len(demo) > 1:
            raise ValidationError(f"已经存在日期为：{self.date}款号为：{self.style_number.style_number}的{self.repair_type}产值记录了！")


    @api.depends('style_number', 'number', 'order_number' ,"order_number.order_price")
    def set_pro_value(self):
        for obj in self:
            obj.pro_value = obj.number * float(obj.order_number.order_price)



    # 设置客户仓库返修统计
    def set_client_warehouse_repair(self):
        dDate = f"{self.date.year}-{self.date.month}"

        client_warehouse_repair_objs = self.env["client_warehouse_repair"].sudo().search([
            ("month", "=",  dDate),
            ("style_number", "=", self.style_number.id)      # 款号
        ])

        if client_warehouse_repair_objs:
            client_warehouse_repair_objs.sudo().set_data()
        else:

            new_obj = client_warehouse_repair_objs.sudo().create({
                "month": dDate,
                "style_number": self.style_number.id     # 款号
            })
            new_obj.sudo().set_data()



    # 设置款号件数汇总数据
    def set_style_number_summary(self):
        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id)
            # ("style_number", "=", self.style_number.id)
        ])
        if style_number_summary_objs:
            style_number_summary_objs.sudo().set_posterior_passage()
        else:
            new_obj = style_number_summary_objs.sudo().create({
                "style_number": self.style_number.id,
            })
            new_obj.sudo().set_posterior_passage()


    # 减少款号件数汇总数据(删除时使用)
    def reduce_style_number_summary(self):

        style_number_summary_objs = self.env["style_number_summary"].sudo().search([
            ("style_number", "=", self.style_number.id)
        ])

        style_number_summary_objs.write({
            "posterior_passage": style_number_summary_objs.posterior_passage + self.number
        })


    @api.model
    def create(self, vals):


        datetime_obj = datetime.strptime(vals['date'], "%Y-%m-%d")
        year = datetime_obj.year
        week = datetime_obj.isocalendar()
        vals["week"] = f"{year}年第{week[1]}周"

        instance = super(RepairValue, self).create(vals)


        repair_value_week_obj = self.env["repair_value_week"].sudo().search([("week", "=", vals["week"])])

        if repair_value_week_obj:

            # 产值
            tem_pro_value = repair_value_week_obj.pro_value + instance.pro_value


            tem_style_number_list = repair_value_week_obj.style_number.split(",")
            tem_style_number_list.append(instance.style_number.style_number)      # 将款号添加到列表中
            tem_style_number_list = list(set(tem_style_number_list))    # 去重
            tem_style_number = ",".join(tem_style_number_list)

            repair_value_week_obj.sudo().write({
                "style_number": tem_style_number,   # 款号
                "number": repair_value_week_obj.number + vals["number"],   # 件数
                "pro_value": tem_pro_value,     # 产值

            })
            instance.repair_value_week_id = repair_value_week_obj.id
        else:

            new_repair_value_week_obj = self.env["repair_value_week"].sudo().create({
                "week": vals["week"],   # 周
                "style_number": instance.style_number.style_number,    # 款号
                "number": vals["number"],   # 件数
                "pro_value": instance.pro_value,     # 产值

            })

            instance.repair_value_week_id = new_repair_value_week_obj.id

        # 款号汇总
        # instance.set_style_number_summary()

        instance.set_client_warehouse_repair()
        # 设置总检效率表返修数量
        instance.set_always_check_efficiency()
        # 设置总检效率表（日）返修数量
        instance.set_always_check_eff_day()
        # 设置品控绩效记录
        instance.set_quality_control_performance()
        # 设置后道进出明细
        instance.set_following_process_detail()

        return instance


    def unlink(self):

        for record in self:

            # 删除组明细
            # record.repair_value_group_line_ids.unlink()

            repair_value_objs = self.env[self._name].sudo().search([("week", "=", record["week"])])
            if len(repair_value_objs) == 1:
                record.repair_value_week_id.sudo().unlink()     # 删除组产值(周)
            else:
                # 计算删除后的人数
                # tem_num_people_sum = 0
                # for cutting_bed_obj in repair_value_objs:
                #     tem_num_people_sum = tem_num_people_sum + cutting_bed_obj.num_people
                # tem_num_people = (tem_num_people_sum - record.num_people) / (len(repair_value_objs) - 1)
                
                # 计算总产值 
                tem_pro_value = record.repair_value_week_id.pro_value - record.pro_value

                # 计算人均产值
                # tem_avg_value = tem_pro_value / tem_num_people

                # 查询相同款号的数量
                style_number_obj = self.env["repair_value"].sudo().search([("style_number", "=", record.style_number.id), ("week", "=", record.week)])
                
                # 如果只有一个，则删除，否则则不删除
                if len(style_number_obj) == 1:
                    tem_style_number_list = record.repair_value_week_id.style_number.split(",")
                    if record.style_number.style_number in tem_style_number_list:
                        tem_style_number_list.remove(record.style_number.style_number)
                    tem_style_number = ",".join(tem_style_number_list)
                else:
                    tem_style_number = record.repair_value_week_id.style_number

                record.repair_value_week_id.sudo().write({
                    "style_number": tem_style_number,   # 款号
                    "number": record.repair_value_week_id.number - record.number,    # 件数
                    # "num_people": tem_num_people,  # 人数
                    # "avg_value": tem_avg_value,  # 人均产值
                    "pro_value": tem_pro_value,   # 产值
                })
            # 款号汇总
            # record.reduce_style_number_summary()

            # 获取临时款号id
            tem_style_number = record.style_number.id

            dDate = f"{self.date.year}-{self.date.month}"
            DayDate = self.date
            # 获取临时组别明细
            group_line = self.repair_value_group_line_ids

            super(RepairValue, record).unlink()

            # 删除时，客户仓库返修，一起更新数据
            client_warehouse_repair_obj = self.env["client_warehouse_repair"].sudo().search([
                ("month", "=",  dDate),
                ("style_number", "=", tem_style_number)
            ])
            if client_warehouse_repair_obj:
                client_warehouse_repair_obj.sudo().set_data()

            # 删除时，总检效率表，一起更新数据
            style_number_line_objs = self.env["style_number_line"].sudo().search([
                ("name", "=", tem_style_number)
            ])
            if style_number_line_objs:

                for style_number_line_obj in style_number_line_objs:
                    style_number_line_obj.always_check_efficiency_id.sudo().set_repair_quantity()

            # 删除时，总检效率表（日），一起更新数据
            always_check_eff_day_objs = self.env["always_check_eff_day"].sudo().search([("dDate", "=", DayDate)])
            if always_check_eff_day_objs:
                for always_check_eff_day_obj in always_check_eff_day_objs:
                    always_check_eff_day_obj.sudo().set_repair_quantity()

            # 删除时，品控绩效记录，一起更新数据
            for group_obj in group_line:

                quality_control_performance_objs = self.env["quality_control_performance"].sudo().search([
                    ("month", "=", dDate),
                    ("group", "=", group_obj.name)
                ])
                if quality_control_performance_objs:
                    quality_control_performance_objs.sudo().set_assess_index()

            # 删除时，设置后道进出明细
            following_process_detail_obj = self.env["following_process_detail"].sudo().search([
                ("dDate", "=", DayDate)
            ])
            if following_process_detail_obj:
                following_process_detail_obj.sudo().set_warehouse_return()

        
        return super(RepairValue, self).unlink()



class RepairValueGroup(models.Model):
    _name = 'repair_value_group'
    _description = '返修组别'
    # _rec_name = "name"

    repair_value_id = fields.Many2one("repair_value")
    name = fields.Char(string="名称")


    # 设置品控绩效记录
    def set_quality_control_performance(self):


        month = f"{self.repair_value_id.date.year}-{self.repair_value_id.date.month}"

        quality_control_performance_objs = self.env["quality_control_performance"].sudo().search([
            ("month", "=", month),
            ("group", "=", self.name)
        ])
        if quality_control_performance_objs:

            quality_control_performance_objs.sudo().set_assess_index()
        
        else:
            now_obj = self.env["quality_control_performance"].sudo().create({
                "month": month,
                "group": self.name
            })
            now_obj.sudo().set_assess_index()



    @api.model
    def create(self, vals):
        # 如果已经有重复name的记录了，则删除该重复记录
        repair_value_group_obj = self.env["repair_value_group"].sudo().search([
            ("repair_value_id", "=", vals["repair_value_id"]),
            ("name", "=", vals["name"])
            ])
        if repair_value_group_obj:
            repair_value_group_obj.unlink()

        instance = super(RepairValueGroup, self).create(vals)

        # instance.set_quality_control_performance()
    
        return instance


    def unlink(self):

        # month = f"{self.repair_value_id.date.year}-{self.repair_value_id.date.month}"
        # group = self.name

        res = super(RepairValueGroup, self).unlink()

        # quality_control_performance_objs = self.env["quality_control_performance"].sudo().search([
        #     ("month", "=", month),
        #     ("group", "=", group)
        # ])
        # if quality_control_performance_objs:
        #     quality_control_performance_objs.sudo().set_assess_index()

        return res





class RepairValueWeek(models.Model):
    _name = 'repair_value_week'
    _description = '返修产值(周)'
    _order = "week desc"

    week = fields.Char('周')
    style_number = fields.Char('款号')
    number = fields.Integer('件数')
    pro_value = fields.Float('产值')
    # num_people = fields.Integer('人数')
    # avg_value = fields.Float('人均产值')