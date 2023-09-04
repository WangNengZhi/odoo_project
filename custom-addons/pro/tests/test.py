from os import lseek


# 导入模块
import xmlrpc.client
from datetime import datetime, date
import sys

# 获取命令行参数
# model_name = sys.argv[1]      # 模型名称
# date = sys.argv[2]            # 日期时间字段
# db_name = sys.argv[3] # 数据库名
# user = sys.argv[4]    # 用户名
# password = sys.argv[5]        # 密码


# # 定义 Odoo服务url地址的，数据库名，登录账号，密码
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "bx@fsn.com", "xb123456"


# common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# common.version()

# # 获取Odoo的res.users表的id
# uid = common.authenticate(db, username, password, {})

# models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


# # 查询周为Fasle的记录
# res = models.execute_kw(db, uid, password,
#         "hr.employee", 'search',
#     [[]]
#     )

# for i in res:
#     models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i], {
#         # 'production_value_difference': 0,
#         # 'wx_password': '123',
#     }])
#     print(i)