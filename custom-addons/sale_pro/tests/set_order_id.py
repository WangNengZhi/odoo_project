# 导入模块
import xmlrpc.client
from datetime import datetime, date
import sys


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "mqc@fsn.com", "mqc123456"
# url, db, username, password = "http://192.168.158.129:8069", "demo02", "admin", "admin"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


print(models)



res1 = models.execute_kw(db, uid, password,
	"sale_pro.sale_pro", 'search_read',
	[[["order_number", "=", "2828"]]],
    {'fields': ['order_number']}
	)
print(res1)
res2 = models.execute_kw(db, uid, password,
	"ib.detail", 'search_read',
	[[["style_number", "=", "2828-DBW"]]],
    {'fields': ['contract_type']}
	)
print(res2)
# for i in res:

#     models.execute_kw(db, uid, password, 'sale_pro.sale_pro', 'write', [[i["id"]], {
#         'ib_detail_ids': i["ib_detail"]
#     }])


# for i in res:
#     models.execute_kw(db, uid, password, 'ib.detail', 'write', [[i], {
#         'order_id': i["id"]
#     }])i
models.execute_kw(db, uid, password, 'ib.detail', 'write', [[res2[0]["id"]], {
    'order_id': res1[0]["id"]
}])


