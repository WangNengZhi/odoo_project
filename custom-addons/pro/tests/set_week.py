# 导入模块
import xmlrpc.client
from datetime import datetime
import sys

# 获取命令行参数
model_name = sys.argv[1]	# 模型名称
date = sys.argv[2]		# 日期时间字段
db_name = sys.argv[3]	# 数据库名
user = sys.argv[4]	# 用户名
password = sys.argv[5]	# 密码


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
url, db, username, password = "http://localhost:8069", db_name, user, password

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


# 查询周为Fasle的记录
res = models.execute_kw(db, uid, password,
	model_name, 'search',
	[[["week", "=", False]]]
	)
# print(res)

# 根据查询到的记录id获取记录中的内容e
res_date_list = models.execute_kw(db, uid, password,
	model_name, 'read',
	[res], {'fields': [date]})
# print(res_date_list)

for res_date in res_date_list:

	datetime_obj = datetime.strptime(res_date[date], "%Y-%m-%d")

	year = datetime_obj.year
	week = datetime_obj.isocalendar()

	pro_week = f"{year}年第{week[1]}周"


	models.execute_kw(db, uid, password, model_name, 'write', [[res_date["id"]], {
		'week': pro_week,
	}])

