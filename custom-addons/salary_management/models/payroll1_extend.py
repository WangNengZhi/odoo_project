from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import timedelta

def get_year_month(year, month, n):
    ''' 获取指定月份之前的n个月份'''

    for _ in range(n-1):
        month -= 1

        if month == 0:
            year, month = year - 1, 12
        
        yield f'{year}-{month:02}'


def get_last_year_month(year, month):
    ''' 获取指定月份之前的上一个月份'''

    month -= 1

    if month == 0:
        year, month = year - 1, 12
    
    return f'{year}-{month:02}'



class salary(models.Model):
    _inherit = "payroll1"

    is_grant_commission_bonus = fields.Boolean(string="是否发放提成", default=False, track_visibility='onchange')



    def get_current_month_commission_bonus(self, post_commission_setting_obj) -> float:
        ''' 获取当月提成（无调岗）'''
        for record in self:
            if post_commission_setting_obj.commission_type == "工厂":
                return record.get_plant_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            elif post_commission_setting_obj.commission_type == "外发":
                return record.get_outsource_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            elif post_commission_setting_obj.commission_type == "工厂和外发":
                return record.get_plant_and_outsource_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            elif post_commission_setting_obj.commission_type == "外发(按订单属性)":
                return record.get_outsource_order_attribute_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            elif post_commission_setting_obj.commission_type == "裁床产值":
                return record.get_caichuang_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            elif post_commission_setting_obj.commission_type == "后道产值":
                return record.get_houdao_commission_bonus(record.get_actual_attendance_days(), post_commission_setting_obj)
            


    def transfer_of_posts_commission_bonus(self):
        ''' 获取当月提成（有调岗）'''
        entry_date = self.name.entry_time   # 入职日期
        dimission_date = self.name.is_delete_date   # 离职日期

        this_month = self.set_begin_and_end()
        transfer_number_objs = self.env["internal.post.transfer"].sudo().search([
            ("name", "=", self.name.id),
            ("begin_start", ">=", this_month.get("begin")),
            ("begin_start", "<=", this_month.get("end")),
        ], order='begin_start')

        actual_attendance_days = self.get_actual_attendance_days()

        num = 0

        for index, transfer_number_obj in enumerate(transfer_number_objs):

            if len(transfer_number_objs) == 1:
                    
                before_actual_attendance_days = [i for i in actual_attendance_days if i < transfer_number_obj.begin_start]
                after_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj.begin_start]

                num += self.post_rout(transfer_number_obj, before_actual_attendance_days, after_actual_attendance_days)
                
            else:

                if index==0:

                    before_actual_attendance_days = [i for i in actual_attendance_days if i < transfer_number_obj.begin_start]
                    after_actual_attendance_days = []

                    num += self.post_rout(transfer_number_obj, before_actual_attendance_days, after_actual_attendance_days)
                    
                elif index==len(transfer_number_objs)-1:

                    before_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_objs[index-1].begin_start and i < transfer_number_obj.begin_start]
                    after_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj.begin_start]

                    num += self.post_rout(transfer_number_obj, before_actual_attendance_days, after_actual_attendance_days)
                else:

                    before_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_objs[index-1].begin_start and i < transfer_number_obj.begin_start]
                    after_actual_attendance_days = []

                    num += self.post_rout(transfer_number_obj, before_actual_attendance_days, after_actual_attendance_days)
            
        return num



    def post_rout(self, transfer_number_obj, before_day_list, after_day_list):
        ''' 提成类型路由'''

        before_post_commission_setting_obj = self.env['post_commission_setting'].sudo().search([("job_id", "=", transfer_number_obj.raw_job_id.id)])
        print(before_post_commission_setting_obj)
        if before_post_commission_setting_obj:
            if before_post_commission_setting_obj.commission_type == "工厂":
                before_commission_bonus = self.get_plant_commission_bonus(before_day_list)
            elif before_post_commission_setting_obj.commission_type == "外发":
                before_commission_bonus = self.get_outsource_commission_bonus(before_day_list)
            elif before_post_commission_setting_obj.commission_type == "工厂和外发":
                before_commission_bonus = self.get_plant_and_outsource_commission_bonus(before_day_list)
            elif before_post_commission_setting_obj.commission_type == "外发(按订单属性)":
                before_commission_bonus = self.get_outsource_order_attribute_commission_bonus(before_day_list, before_post_commission_setting_obj)
            elif before_post_commission_setting_obj.commission_type == "裁床产值":
                before_commission_bonus = self.get_caichuang_commission_bonus(before_day_list, before_post_commission_setting_obj)
            elif before_post_commission_setting_obj.commission_type == "后道产值":
                before_commission_bonus = self.get_houdao_commission_bonus(before_day_list, before_post_commission_setting_obj)
        else:

            before_commission_bonus = 0

        
        after_post_commission_setting_obj = self.env['post_commission_setting'].sudo().search([("job_id", "=", transfer_number_obj.job_id.id)])

        if after_post_commission_setting_obj:
            if after_post_commission_setting_obj.commission_type == "工厂":
                after_commission_bonus = self.get_plant_commission_bonus(after_day_list)
            elif after_post_commission_setting_obj.commission_type == "外发":
                after_commission_bonus = self.get_outsource_commission_bonus(after_day_list)
            elif after_post_commission_setting_obj.commission_type == "工厂和外发":
                after_commission_bonus = self.get_plant_and_outsource_commission_bonus(after_day_list)
            elif after_post_commission_setting_obj.commission_type == "外发(按订单属性)":
                after_commission_bonus = self.get_outsource_order_attribute_commission_bonus(after_day_list, after_post_commission_setting_obj)
            elif after_post_commission_setting_obj.commission_type == "裁床产值":
                after_commission_bonus = self.get_caichuang_commission_bonus(after_day_list, after_post_commission_setting_obj)
            elif after_post_commission_setting_obj.commission_type == "后道产值":
                after_commission_bonus = self.get_houdao_commission_bonus(after_day_list, after_post_commission_setting_obj)
        else:
            after_commission_bonus = 0
        
        return before_commission_bonus + after_commission_bonus
    
    def get_caichuang_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 裁床产值提成奖金'''
        cutting_bed_objs = self.env['cutting_bed'].sudo().search([("date", "in", actual_attendance_days)])

        return sum(cutting_bed_objs.mapped("pro_value")) * post_commission_setting_obj.commission_ratio


    def get_houdao_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 后道产值提成奖金'''

        target_output_value_obj = self.env['target_output_value'].sudo().search([("year_month", "=", self.date), ("employee_id", "=", self.name.id)])

        
        return target_output_value_obj.piecework_value * post_commission_setting_obj.commission_ratio



    def get_plant_and_outsource_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 工厂和外发提成奖金'''
        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂", "外发"])

        return_good_output_value = self.get_return_good_output_value(actual_attendance_days)

        return (stock_output_increase - return_good_output_value) * post_commission_setting_obj.commission_ratio


    def get_plant_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 工厂提成奖金'''
        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["工厂"])

        return_good_output_value = self.get_return_good_output_value(actual_attendance_days)

        return (stock_output_increase - return_good_output_value) * post_commission_setting_obj.commission_ratio


    def get_outsource_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 外发提成奖金'''
        stock_output_increase = self.get_warehouse_finished_product_stock_data(actual_attendance_days, ["外发"])

        return_good_output_value = self.get_return_good_output_value(actual_attendance_days)

        return (stock_output_increase - return_good_output_value) * post_commission_setting_obj.commission_ratio

    
    
    def get_outsource_order_attribute_commission_bonus(self, actual_attendance_days, post_commission_setting_obj) -> float:
        ''' 外发(按订单属性)提成奖金'''

        warehouse_finished_product_stock_objs = self.env['warehouse_finished_product_stock'].sudo().search([
            ("date", "in", actual_attendance_days), ("processing_type", "=", "外发")
        ])

        temp_commission_bonus = 0

        for warehouse_finished_product_stock_obj in warehouse_finished_product_stock_objs:
            
            post_commission_setting_line_obj = post_commission_setting_obj.post_commission_setting_line_ids.filtered(lambda line: line.order_attribute_id.id == warehouse_finished_product_stock_obj.order_number.attribute.id)

            temp_commission_bonus += (post_commission_setting_line_obj.commission_amount * warehouse_finished_product_stock_obj.change_stock)
        
        return temp_commission_bonus * post_commission_setting_obj.commission_ratio




    def get_distance_last_months(self, year, month, starting_month):
        ''' 查询距离上一次发放几个月'''
        lst = []
        starting_month_year, starting_month_month = map(int, starting_month.split('-'))

        while True:

            last_year_month = get_last_year_month(year, month)

            if last_year_month == get_last_year_month(starting_month_year, starting_month_month):
                return lst

            last_payroll1_obj = self.env['payroll1'].sudo().search([
                ("date", "=", last_year_month),
                ("name", "=", self.name.id),
                ("is_grant_commission_bonus", "=", False)
            ])

            if last_payroll1_obj:
                lst.append(last_year_month)
                year, month = map(int, last_year_month.split('-'))
            else:
                return lst



    def refresh_commission_bonus(self):
        ''' 提成刷新'''
        for record in self:

            if record.transfer_number:
                current_month_commission_bonus = record.transfer_of_posts_commission_bonus()

                post_commission_setting_obj = self.env['post_commission_setting'].sudo().search([("job_id", "=", record.job_id.id)])

                if post_commission_setting_obj:

                    year, month = map(int, record.date.split('-'))
                    payroll1_objs_list = []
                    if not post_commission_setting_obj.frequency_distribution:
                        raise ValidationError(f"提成设置频率不可为0")
                    year_month_list = list(get_year_month(year, month, post_commission_setting_obj.frequency_distribution))
                    # 检查如果改变了发放频率，发放频率变少，发放时将之前超过发放频率之前的提成算进去
                    distance_last_months_list = record.get_distance_last_months(year, month, post_commission_setting_obj.starting_month)

                    if len(year_month_list) < len(distance_last_months_list):
                        year_month_list = distance_last_months_list

                    for year_month in year_month_list:

                        # 查询该岗位的启始月份，如果超过了起始月份则break，因为从起始月份开始到当前月份不满足发放提成的发放频率要求
                        post_performance_setting_year, post_performance_setting_month = map(int, post_commission_setting_obj.starting_month.split('-'))
                        if year_month == get_last_year_month(post_performance_setting_year, post_performance_setting_month):
                            # 如果循环中某个月份等于开始月份的上一个月份 则当月不发放，并记下当月提成
                            record.is_grant_commission_bonus = False
                            record.commission_bonus = current_month_commission_bonus
                            break

                        payroll1_obj = self.env['payroll1'].sudo().search([
                            ("date", "=", year_month),
                            ("name", "=", record.name.id),
                            ("is_grant_commission_bonus", "=", False)
                        ])
                        # 循环中如果查询到某个月份的薪资明细中提成是未发放的，则添加到列表中，如果没有查询到， 则当月不发放，并记下当月提成
                        if not payroll1_obj:
                            record.is_grant_commission_bonus = False
                            record.commission_bonus = current_month_commission_bonus
                            break
                        else:
                            payroll1_objs_list.append(payroll1_obj)

                    else:
                        # 如果循环顺利结束，则说明满足发放条件，则 计算累计月份的提成总和
                        record.is_grant_commission_bonus = True
                        record.commission_bonus = current_month_commission_bonus + sum(i.commission_bonus for i in payroll1_objs_list)

                else:

                    record.is_grant_commission_bonus = False


            else:

                post_commission_setting_obj = self.env['post_commission_setting'].sudo().search([("job_id", "=", record.job_id.id)])

                if post_commission_setting_obj:

                    year, month = map(int, record.date.split('-'))
                    payroll1_objs_list = []

                    if not post_commission_setting_obj.frequency_distribution:
                        raise ValidationError(f"提成设置频率不可为0")
                    year_month_list = list(get_year_month(year, month, post_commission_setting_obj.frequency_distribution))
                    # 检查如果改变了发放频率，发放频率变少，发放时将之前超过发放频率之前的提成算进去
                    distance_last_months_list = record.get_distance_last_months(year, month, post_commission_setting_obj.starting_month)

                    if len(year_month_list) < len(distance_last_months_list):
                        year_month_list = distance_last_months_list

                    for year_month in year_month_list:

                        # 查询该岗位的启始月份，如果超过了起始月份则break，因为从起始月份开始到当前月份不满足发放提成的发放频率要求
                        post_performance_setting_year, post_performance_setting_month = map(int, post_commission_setting_obj.starting_month.split('-'))
                        if year_month == get_last_year_month(post_performance_setting_year, post_performance_setting_month):
                            # 如果循环中某个月份等于开始月份的上一个月份 则当月不发放，并记下当月提成
                            record.is_grant_commission_bonus = False
                            record.commission_bonus = record.get_current_month_commission_bonus(post_commission_setting_obj)
                            break

                        payroll1_obj = self.env['payroll1'].sudo().search([
                            ("date", "=", year_month),
                            ("name", "=", record.name.id),
                            ("is_grant_commission_bonus", "=", False)
                        ])
                        # 循环中如果查询到某个月份的薪资明细中提成是未发放的，则添加到列表中，如果没有查询到， 则当月不发放，并记下当月提成
                        if not payroll1_obj:
                            record.is_grant_commission_bonus = False
                            record.commission_bonus = record.get_current_month_commission_bonus(post_commission_setting_obj)
                            break
                        else:
                            payroll1_objs_list.append(payroll1_obj)

                    else:
                        # 如果循环顺利结束，则说明满足发放条件，则 计算累计月份的提成总和
                        record.is_grant_commission_bonus = True
                        record.commission_bonus = record.get_current_month_commission_bonus(post_commission_setting_obj) + sum(i.commission_bonus for i in payroll1_objs_list)
                
                else:

                    record.is_grant_commission_bonus = False


    is_grant_performance_bonus = fields.Boolean(string="是否发放绩效奖金", default=False, track_visibility='onchange')


    def get_erformance_bonus(self, quota, first_day, last_day):
        ''' 获取绩效奖金'''
        reward_punish_record_objs = self.env["reward_punish_record"].sudo().search([
            ("emp_id", "=", self.name.id),
            ("declare_time", ">=", first_day),
            ("declare_time", "<", last_day),
            ("state", "=", "审批通过"),
            ("record_type", "=", "punish")
        ])

        money_amount = sum(reward_punish_record_objs.mapped('money_amount'))

        
        return 0 if quota < money_amount else quota - money_amount




    def refresh_performance_bonus(self):
        ''' 绩效奖金刷新'''
        for record in self:
            if record.transfer_number:
                ''' 有转岗'''
                record.refresh_performance_bonus_transfer()
            else:
                ''' 无转岗'''
                record.refresh_performance_bonus_no_transfer()


        


    def refresh_performance_bonus_transfer(self):
        ''' 转岗绩效奖金刷新'''

        current_month_performance_bonus = self.get_many_transfer_posts_performance_bonus(self.get_actual_attendance_days())

        year, month = map(int, self.date.split('-'))

        post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", self.job_id.id), ("frequency_distribution", ">", 1)])

        if post_performance_setting_obj:
            if not post_performance_setting_obj.frequency_distribution:
                raise ValidationError(f"绩效设置频率不可为0")
            year_month_list = list(get_year_month(year, month, post_performance_setting_obj.frequency_distribution))

            # 检查如果改变了发放频率，发放频率变少，发放时将之前超过发放频率之前的提成算进去
            distance_last_months_list = self.get_distance_last_months(year, month, post_performance_setting_obj.starting_month)

            if len(year_month_list) < len(distance_last_months_list):
                year_month_list = distance_last_months_list

            payroll1_objs_list = []

            for year_month in year_month_list:

                # 查询该岗位的启始月份，如果超过了起始月份则break，因为从起始月份开始到当前月份不满足发放绩效的发放频率要求
                post_performance_setting_year, post_performance_setting_month = map(int, post_performance_setting_obj.starting_month.split('-'))
                if year_month == get_last_year_month(post_performance_setting_year, post_performance_setting_month):
                    self.is_grant_performance_bonus = False
                    self.other_deductions = 0
                    self.performance_bonus = current_month_performance_bonus
                    break

                payroll1_obj = self.env['payroll1'].sudo().search([
                    ("date", "=", year_month),
                    ("name", "=", self.name.id),
                    ("is_grant_performance_bonus", "=", False)
                ])

                if not payroll1_obj:
                    self.is_grant_performance_bonus = False
                    self.other_deductions = 0
                    self.performance_bonus = current_month_performance_bonus
                    break
                else:
                    payroll1_objs_list.append(payroll1_obj)

            else:
                self.is_grant_performance_bonus = True
                self.other_deductions = 0

                self.performance_bonus = current_month_performance_bonus + sum(i.performance_bonus for i in payroll1_objs_list)



    def get_output_plan_performance_bonus(self, job_name, post_commission, actual_attendance_days):
        ''' 通过计划产值计算绩效额度'''

        if job_name == "流水组长":
            
            target_output_value_obj = self.env['target_output_value'].sudo().search([
                ("year_month", "=", self.date),
                ("employee_id", "=", self.name.id),
            ], limit=1)
            if target_output_value_obj:
                return post_commission * (target_output_value_obj.progress / 100)
                # performance_money = (group_leader_performance_money / 26) * self.clock_in_time
            else:
                raise ValidationError(f"没有查询到流水组长{self.name.name}的目标产值记录！")

        else:
            return (post_commission / 26) * len(actual_attendance_days)



    def get_many_transfer_posts_performance_bonus(self, actual_attendance_days) -> float:
        ''' 获取调岗绩效奖金'''

        entry_date = self.name.entry_time   # 入职日期
        dimission_date = self.name.is_delete_date   # 离职日期

        this_month = self.set_begin_and_end()
        transfer_number_objs = self.env["internal.post.transfer"].sudo().search([
            ("name", "=", self.name.id),
            ("begin_start", ">=", this_month.get("begin")),
            ("begin_start", "<=", this_month.get("end")),
        ], order='begin_start')

        actual_attendance_days = self.get_actual_attendance_days()  # 实际出勤日期列表

        sum = 0 

        for index, transfer_number_obj in enumerate(transfer_number_objs):

            if len(transfer_number_objs) == 1:

                before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.raw_job_id.id), ("frequency_distribution", ">", 1)])

                if before_post_performance_setting_obj:

                    before_actual_attendance_days = [i for i in actual_attendance_days if i < transfer_number_obj.begin_start and i >= this_month.get("begin")]

                    before_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.raw_job_id.name, transfer_number_obj.before_post_commission, before_actual_attendance_days)

                    before_erformance_bonus = self.get_erformance_bonus(before_post_commission,\
                        this_month.get("begin"), transfer_number_obj.begin_start)
                else:
                    before_erformance_bonus = 0

                after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.job_id.id), ("frequency_distribution", ">", 1)])
                
                if after_post_performance_setting_obj:

                    after_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj.begin_start]

                    after_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.job_id.name, transfer_number_obj.after_post_commission, after_actual_attendance_days)

                    after_erformance_bonus = self.get_erformance_bonus(after_post_commission,\
                        transfer_number_obj.begin_start, this_month.get("end") + timedelta(days=1))
                
                else:
                    after_erformance_bonus = 0

                sum += (before_erformance_bonus + after_erformance_bonus)
            else:

                if index == 0:

                    before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.raw_job_id.id), ("frequency_distribution", ">", 1)])
                    if before_post_performance_setting_obj:

                        before_actual_attendance_days = [i for i in actual_attendance_days if i < transfer_number_obj.begin_start and i >= this_month.get("begin")]

                        before_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.raw_job_id.name, transfer_number_obj.before_post_commission, before_actual_attendance_days)

                        before_erformance_bonus = self.get_erformance_bonus(before_post_commission,\
                            this_month.get("begin"), transfer_number_obj.begin_start)
                    else:
                        before_erformance_bonus = 0
                    
                    sum += before_erformance_bonus

                elif index == len(transfer_number_objs)-1:

                    before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.raw_job_id.id), ("frequency_distribution", ">", 1)])
                    if before_post_performance_setting_obj:

                        before_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj[index-1].begin_start and i < transfer_number_obj.begin_start]

                        before_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.raw_job_id.name, transfer_number_obj.before_post_commission, before_actual_attendance_days)

                        before_erformance_bonus = self.get_erformance_bonus(before_post_commission,\
                            transfer_number_obj[index-1].begin_start, transfer_number_obj.begin_start)

                    else:
                        before_erformance_bonus = 0

                    after_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.job_id.id), ("frequency_distribution", ">", 1)])
                    
                    if after_post_performance_setting_obj:

                        after_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj.begin_start.begin_start and i <= this_month.get("end")]

                        after_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.job_id.name, transfer_number_obj.after_post_commission, after_actual_attendance_days)

                        after_erformance_bonus = self.get_erformance_bonus(after_post_commission,\
                            transfer_number_obj.begin_start, this_month.get("end") + timedelta(days=1))
                    
                    else:
                        after_erformance_bonus = 0

                    sum += (before_erformance_bonus + after_erformance_bonus)
                else:

                    before_post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", transfer_number_obj.raw_job_id.id), ("frequency_distribution", ">", 1)])
                    if before_post_performance_setting_obj:

                        before_actual_attendance_days = [i for i in actual_attendance_days if i >= transfer_number_obj[index-1].begin_start and i < transfer_number_obj.begin_start]

                        before_post_commission = self.get_output_plan_performance_bonus(transfer_number_obj.raw_job_id.name, transfer_number_obj.before_post_commission, before_actual_attendance_days)

                        before_erformance_bonus = self.get_erformance_bonus(before_post_commission,\
                            transfer_number_obj[index-1].begin_start, transfer_number_obj.begin_start)
                    else:
                        before_erformance_bonus = 0

                    sum += before_erformance_bonus
            
        return sum




    def refresh_performance_bonus_no_transfer(self):
        ''' 无转岗绩效奖金刷新'''
        for record in self:

            # 获取当月第一天和最后一天
            this_month = record.set_begin_and_end()

            post_performance_setting_obj = self.env['post_performance_setting'].sudo().search([("job_id", "=", record.job_id.id), ("frequency_distribution", ">", 1)])

            if post_performance_setting_obj:


                year, month = map(int, record.date.split('-'))
                payroll1_objs_list = []
                if not post_performance_setting_obj.frequency_distribution:
                    raise ValidationError(f"绩效设置频率不可为0")
                year_month_list = list(get_year_month(year, month, post_performance_setting_obj.frequency_distribution))
                # 检查如果改变了发放频率，发放频率变少，发放时将之前超过发放频率之前的绩效算进去
                distance_last_months_list = record.get_distance_last_months(year, month, post_performance_setting_obj.starting_month)

                if len(year_month_list) < len(distance_last_months_list):
                    year_month_list = distance_last_months_list

                performance_money = (record.name.performance_money / 26) * record.clock_in_time

                for year_month in year_month_list:

                    # 查询该岗位的启始月份，如果超过了起始月份则break，因为从起始月份开始到当前月份不满足发放绩效的发放频率要求
                    post_performance_setting_year, post_performance_setting_month = map(int, post_performance_setting_obj.starting_month.split('-'))
                    if year_month == get_last_year_month(post_performance_setting_year, post_performance_setting_month):
                        record.is_grant_performance_bonus = False
                        record.other_deductions = 0
                        record.performance_bonus = performance_money - self.get_reward_punish_record_money_amount(True, this_month.get("begin"), this_month.get("end"))
                        break

                    payroll1_obj = self.env['payroll1'].sudo().search([
                        ("date", "=", year_month),
                        ("name", "=", record.name.id),
                        ("is_grant_performance_bonus", "=", False)
                    ])

                    if not payroll1_obj:
                        record.is_grant_performance_bonus = False
                        record.other_deductions = 0
                        record.performance_bonus = performance_money - self.get_reward_punish_record_money_amount(True, this_month.get("begin"), this_month.get("end"))
                        break
                    else:
                        payroll1_objs_list.append(payroll1_obj)

                else:
                    record.is_grant_performance_bonus = True

                    record.other_deductions = 0
                    
                    record.performance_bonus = performance_money - self.get_reward_punish_record_money_amount(True, this_month.get("begin"), this_month.get("end")) + sum(i.performance_bonus for i in payroll1_objs_list)

            else:
                record.is_grant_performance_bonus = False



    def anomaly_detection01(self):
        '''工资明细 异常检测'''
        text = ""
        for record in self:
            if record.time_plan == "8:00 - 21:00, 单休":
                if record.day_average_salary < 170:
                    text = text + f"月份：{record.date}，员工: {record.name.name}\n"
            elif record.time_plan == "9:00 - 18:00, 单休":
                if record.day_average_salary < 105:
                    text = text + f"月份：{record.date}，员工: {record.name.name}\n"


        if text:
            raise ValidationError(f"{text}以上员工“应发”存在异常！")
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('检测通过！'),
                    'message': '没有发现任何异常！',
                    'sticky': False,
                    'type': 'success'
                },
            }

