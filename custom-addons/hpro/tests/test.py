# import openpyxl
# # 导入模块
# import xmlrpc.client
# from datetime import datetime
#
#
# # 定义 Odoo服务url地址的，数据库名，登录账号，密码http://192.168.158.128:8069/
# # url, db, username, password = "http://192.168.158.128:8069", "demo04", "admin", "admin"
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "clh@fsn.com", "clh123456"
# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# common.version()
#
# # 获取Odoo的res.users表的id
# uid = common.authenticate(db, username, password, {})
#
# models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
#
# print(models)
#
#
#
#
# # [datetime.datetime(2021, 8, 25, 0, 0), None, 4395, 0, None, '点位，一件5个位', None, None, 20, 0.133334, None, '舒莹', None, None, 100]
# def fsn_create(data_list):
#
#     if data_list[0] == None:
#         print("结束")
#     else:
#
#         # 查询款式编号的
#         order_number = None
#         if data_list[2]:
#             order_number_res = models.execute_kw(db, uid, password,
#                 'ib.detail', 'search',
#                 [[["style_number", "=", data_list[2]]]]
#                 )
#
#             if order_number_res == []:
#                 pass
#             else:
#                 order_number = order_number_res[0]
#         else:
#             pass
#
#
#
#         # # 员工id
#         emp_res = models.execute_kw(db, uid, password,
#             'hr.employee', 'search',
#             [[["name", "=", data_list[11]]]]
#             )
#
#         if emp_res == []:
#             pass
#         else:
#             if order_number:
#
#                 # 创建记录
#                 wwchat_info_id = models.execute_kw(db, uid, password, 'on.work', 'create', [{
#                     'date1': data_list[0].strftime('%Y-%m-%d'),   #  日期
#                     'order_number': order_number,   # 款式编号
#                     'employee_id': data_list[3],    # 工序号
#                     # 'part_name': "",    # 部件名称
#                     'process_abbreviation': data_list[5] if data_list[5] else "",     # 工序描述
#                     # 'mechanical_type': "",      # 机器类型
#                     'process_level': data_list[7] if data_list[7] else "",    # 工序等级
#                     'standard_time': data_list[8],    # 标准时间
#                     'standard_price': data_list[9],   # 原单价
#                     'employee': emp_res[0],      # 员工
#                     'employee_id2': "",     # 员工编号
#                     'group': data_list[13] if data_list[13] else "",    # 组别
#                     'over_number': data_list[14] if data_list[14] else 0,   # 件数
#                 }])
#             else:
#
#                 # 创建记录
#                 wwchat_info_id = models.execute_kw(db, uid, password, 'on.work', 'create', [{
#                     'date1': data_list[0].strftime('%Y-%m-%d'),   #  日期
#                     # 'order_number': order_number,   # 款式编号
#                     'employee_id': data_list[3],    # 工序号
#                     # 'part_name': "",    # 部件名称
#                     'process_abbreviation': data_list[5] if data_list[5] else "",     # 工序描述
#                     # 'mechanical_type': "",      # 机器类型
#                     'process_level': data_list[7] if data_list[7] else "",    # 工序等级
#                     'standard_time': data_list[8],    # 标准时间
#                     'standard_price': data_list[9],   # 原单价
#                     'employee': emp_res[0],      # 员工
#                     'employee_id2': "",     # 员工编号
#                     'group': data_list[13] if data_list[13] else "",    # 组别
#                     'over_number': data_list[14] if data_list[14] else 0,   # 件数
#                 }])
#
#
#
#
# def main():
#     # 打开工作簿
#     wb = openpyxl.load_workbook('eee.xlsx')
#     # 获取表单
#     sh = wb['Sheet1']
#     # 按行读取
#     rows = sh.rows
#     count = 0
#     # 循环每行
#     for row in list(rows):
#         data_list = []
#         # 循环每列
#         for i in row:
#             # 打印每个格子的值
#             data_list.append(i.value)
#
#         print(data_list)
#
#         fsn_create(data_list)
#         count = count + 1
#         print(count)
#
#
# if __name__ == '__main__':
#
#     main()