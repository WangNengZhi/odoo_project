# 导入模块
import xmlrpc.client
from datetime import datetime


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "clh@fsn.com", "clh123456"
url, db, username, password = "http://192.168.14.130:8069", "123456", "clh@fsn.com", "clh123456"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

res = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read',
    [[]],
    {'fields': ['name', 'rice_tonic', 'dormitory_subsidy', 'entry_time']}
    )



segmentation_time = '2022-02-01 00:00:00'
segmentation_time = datetime.strptime(segmentation_time, "%Y-%m-%d %H:%M:%S")


for i in res:

    i["entry_time"] = datetime.strptime(i["entry_time"], "%Y-%m-%d")
    # print(i, i["entry_time"], type(i["entry_time"]))

    # if i["rice_tonic"] == "有":

    #     models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
    #         'meal_allowance_type': "薪酬之外",
    #         "meal_allowance_limit": 300,
    #     }])

    # elif i["rice_tonic"] == "没有":

    #     models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
    #         'meal_allowance_type': "薪酬之内",
    #         "meal_allowance_limit": 300,
    #     }])

    if i["dormitory_subsidy"] == "有":
        if i["entry_time"] >= segmentation_time:
            models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
                'housing_subsidy_type': "薪酬之外",
                "housing_subsidy_limit": 300,
            }])
        else:
            models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
                'housing_subsidy_type': "薪酬之外",
                "housing_subsidy_limit": 400,
            }])
    else:
        if i["entry_time"] >= segmentation_time:
            models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
                'housing_subsidy_type': "薪酬之内",
                "housing_subsidy_limit": 300,
            }])
        else:
            models.execute_kw(db, uid, password, 'hr.employee', 'write', [[i["id"]], {
                'housing_subsidy_type': "薪酬之内",
                "housing_subsidy_limit": 400,
            }])