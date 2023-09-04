from datetime import datetime, timedelta, date
import calendar

from odoo import models, fields, api


class DesignDepartmentPerformance(models.Model):
    _name = 'design_department_performance'
    _description = '设计部绩效'
    _order = "date desc"

    date = fields.Date(string="日期", required=True)
    design_number = fields.Many2one('product_design', string="设计编号", required=True)
    style_number = fields.Many2one('style_number_base', string='款号')
    designer = fields.Many2one('hr.employee', string='设计师')
    sales_volume = fields.Float(string='销量')


    # def update_design_department_performance(self):
    #     """更新设计部绩效"""
    #
    #     # 获取当前年份和月份
    #     current_date = datetime.now()
    #     year = current_date.year
    #     month = current_date.month
    #
    #     if month < 10:
    #         formatted_date = f"{year}-0{month}"
    #     else:
    #         formatted_date = f"{year}-{month}"
    #
    #     start_date = date(year, month, 1)
    #     _, last_day = calendar.monthrange(year, month)
    #     end_date = date(year, month, last_day)
    #
    #     # 查询设计师
    #     designer_name = self.env['hr.employee'].search([('job_id.name', '=', '设计师'), ('is_delete', '=', False)])
    #
    #     for designer in designer_name:
    #         # 查询设计设计编号
    #         products = self.env['product_design'].search([('designer_id', '=', designer.id)])
    #
    #         style_id = []  # 初始化 style_id 列表
    #
    #         for product in products:
    #             lst = []  # 初始化 lst 列表
    #
    #             # 技术科样衣查询
    #             sample_clothes = self.env['th_per_management'].search(
    #                 [('product_design_id', '=', product.design_number)])
    #             for sample in sample_clothes:
    #                 lst.append(sample.style_number.style_number_base_id.id)
    #
    #             # 样衣科制版查询
    #             prints = self.env['fsn_platemaking_record'].search([('product_design_id', '=', product.design_number)])
    #             for p in prints:
    #                 lst.append(p.style_number_id.style_number_base_id.id)
    #
    #             for i in set(lst):
    #                 style_id.extend(self.env['ib.detail'].search([("style_number_base_id", "=", i)]).ids)
    #
    #             style_id = list(set(style_id))
    #
    #             # 销售查询
    #             sales = self.env['fsn_sales_order_line'].search([('style_number', 'in', style_id),
    #                                                              ('fsn_sales_order_id.fsn_delivery_date', '>=',
    #                                                               start_date),
    #                                                              ('fsn_sales_order_id.fsn_delivery_date', '<=',
    #                                                               end_date)])
    #
    #
    #         existing_data = self.env['design_department_performance'].search([('design_number', '=', product.id),
    #                                                                           ('date', '=', formatted_date)])
    #
    #         if not existing_data:
    #             data = {
    #                 'date': formatted_date,
    #                 'design_number': product.id,
    #                 'designer': designer.id,
    #                 'sales_volume': sum(sales.mapped('quantity'))
    #             }
    #             self.env['design_department_performance'].create(data)
    #         else:
    #             # 更新销售数量
    #             existing_data.sudo().write({'sales_volume': sum(sales.mapped('quantity'))})

    # def update_design_department_performance(self):
    #     """更新设计部绩效"""
    #
    #     # 获取当前年份和月份
    #     current_date = datetime.now()
    #     year = current_date.year
    #     month = current_date.month
    #
    #     if month < 10:
    #         formatted_date = f"{year}-0{month}"
    #     else:
    #         formatted_date = f"{year}-{month}"
    #
    #     start_date = date(year, month, 1)
    #     _, last_day = calendar.monthrange(year, month)
    #     end_date = date(year, month, last_day)
    #
    #     # 查询设计师
    #     designer_name = self.env['hr.employee'].search([('job_id.name', '=', '设计师'), ('is_delete', '=', False)])
    #
    #     for designer in designer_name:
    #         # 查询设计设计编号
    #         products = self.env['product_design'].search([('designer_id', '=', designer.id)])
    #
    #         style_id = []  # 初始化 style_id 列表
    #
    #         for product in products:
    #             lst = []  # 初始化 lst 列表
    #
    #             # 技术科样衣查询
    #             sample_clothes = self.env['th_per_management'].search(
    #                 [('product_design_id', '=', product.design_number)])
    #             for sample in sample_clothes:
    #                 lst.append(sample.style_number.style_number_base_id.id)
    #
    #             # 样衣科制版查询
    #             prints = self.env['fsn_platemaking_record'].search([('product_design_id', '=', product.design_number)])
    #             for p in prints:
    #                 lst.append(p.style_number_id.style_number_base_id.id)
    #             for i in set(lst):
    #                 print(type(i))
    #                 style_id.extend(self.env['ib.detail'].search([("style_number_base_id", "=", i)]).ids)
    #
    #                 style_id = list(set(style_id))
    #
    #                 # 销售查询
    #                 sales = self.env['fsn_sales_order_line'].search([('style_number', 'in', style_id),
    #                                                                  ('fsn_sales_order_id.fsn_delivery_date', '>=',
    #                                                                   start_date),
    #                                                                  ('fsn_sales_order_id.fsn_delivery_date', '<=',
    #                                                                   end_date)])
    #
    #                 existing_data = self.env['design_department_performance'].search([('design_number', '=', product.id),
    #                                                                                   ('date', '=', formatted_date)])
    #
    #                 if not existing_data:
    #                     data = {
    #                         'date': formatted_date,
    #                         'design_number': product.id,
    #                         'designer': designer.id,
    #                         'style_number': i,
    #                         'sales_volume': sum(sales.mapped('quantity'))
    #                     }
    #                     print(data)
    #                     # self.env['design_department_performance'].create(data)
    #                 else:
    #                     # 更新销售数量
    #                     existing_data.sudo().write({'sales_volume': sum(sales.mapped('quantity'))})

    # def update_design_department_performance(self):
    #     """更新设计部绩效"""
    #
    #     # 获取当前年份和月份
    #     current_date = datetime.now()
    #     year = current_date.year
    #     month = current_date.month
    #
    #     start_date = date(year, month, 1)
    #     _, last_day = calendar.monthrange(year, month)
    #     end_date = date(year, month, last_day)
    #
    #     # 查询设计师
    #     designer_name = self.env['hr.employee'].search([('job_id.name', '=', '设计师'), ('is_delete', '=', False)])
    #
    #     for designer in designer_name:
    #         # 查询设计设计编号
    #         products = self.env['product_design'].search([('designer_id', '=', designer.id)])
    #
    #         style_quantities = {}  # 用于存储每个款号对应的销售数量
    #
    #         for product in products:
    #             lst = []  # 初始化 lst 列表
    #
    #             # 技术科样衣查询
    #             sample_clothes = self.env['th_per_management'].search(
    #                 [('product_design_id', '=', product.design_number)])
    #             for sample in sample_clothes:
    #                 lst.append(sample.style_number.style_number_base_id.id)
    #
    #             # 样衣科制版查询
    #             prints = self.env['fsn_platemaking_record'].search([('product_design_id', '=', product.design_number)])
    #             for p in prints:
    #                 lst.append(p.style_number_id.style_number_base_id.id)
    #
    #             for style_id in set(lst):
    #                 # 销售查询
    #                 sales = self.env['fsn_sales_order_line'].search([('style_number', '=', style_id)])
    #
    #                 quantity_sum = sum(sales.mapped('quantity'))  # 计算销售数量总和
    #                 style_quantities[style_id] = style_quantities.get(style_id, 0.0) + quantity_sum
    #
    #         for style_id, quantity in style_quantities.items():
    #             existing_data = self.env['design_department_performance'].search([('design_number', '=', product.id),
    #                                                                               ('date', '=', formatted_date),
    #                                                                               ('style_number', '=', style_id)])
    #
    #             if not existing_data:
    #                 data = {
    #                     'date': '',
    #                     'design_number': product.id,
    #                     'designer': designer.id,
    #                     'style_number': style_id,
    #                     'sales_volume': quantity
    #                 }
    #                 self.env['design_department_performance'].create(data)
    #             else:
    #                 # 更新销售数量
    #                 existing_data.sudo().write({'sales_volume': quantity})

    def update_design_department_performance(self):
        """更新设计部绩效"""

        # 查询设计师
        designer_name = self.env['hr.employee'].search([('job_id.name', '=', '设计师'), ('is_delete', '=', False)])

        for designer in designer_name:
            # 查询设计设计编号
            products = self.env['product_design'].search([('designer_id', '=', designer.id)])

            for product in products:
                lst = []  # 初始化 lst 列表

                # 技术科样衣查询
                sample_clothes = self.env['th_per_management'].search(
                    [('product_design_id', '=', product.design_number)])
                for sample in sample_clothes:
                    lst.append(sample.style_number.style_number_base_id.id)
                    # lst.append(sample.style_number.id)

                # 样衣科制版查询
                prints = self.env['fsn_platemaking_record'].search([('product_design_id', '=', product.design_number)])
                for p in prints:
                    lst.append(p.style_number_id.style_number_base_id.id)
                    # lst.append(p.style_number_id.id)

                for style_id in set(lst):
                    data = []  # 用于存储每个款号每个月的销量数据

                    # 销售查询
                    sales = self.env['fsn_sales_order'].search([
                        ('fsn_sales_order_line_ids.style_number', '>=', style_id)
                    ])

                    # sales = self.env['fsn_sales_order'].search([])

                    for sale in sales:
                        quantity_sum = sum(
                            sales.filtered(lambda s: s.date == sale.date).mapped('fsn_sales_order_line_ids.quantity'))  # 计算销售数量总和

                        data.append({
                            'date': sale.date,
                            'design_number': product.id,
                            'designer': designer.id,
                            'style_number': style_id,
                            'sales_volume': quantity_sum
                        })
                    for entry in data:
                        existing_data = self.env['design_department_performance'].search([
                            ('design_number', '=', entry['design_number']),
                            ('style_number', '=', entry['style_number']),
                            ('date', '=', entry['date'])
                        ])

                        if not existing_data.exists():
                            self.env['design_department_performance'].create(entry)
                        else:
                            # 更新销售数量
                            existing_data.sudo().write({'sales_volume': entry['sales_volume']})
