# 导入模块
import xmlrpc.client
from datetime import datetime, date
import sys

# 获取命令行参数
# model_name = sys.argv[1]	# 模型名称
# date = sys.argv[2]		# 日期时间字段
# db_name = sys.argv[3]	# 数据库名
# user = sys.argv[4]	# 用户名
# password = sys.argv[5]	# 密码


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "yl@fsn.com", "yl123456"


common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

res = models.execute_kw(db, uid, password,
	"posterior_passage_output_value_week", 'search',
	[[["week", "=", "2021年第31周"]]]
	)
print(res)
    # 10461-BK,63002-WT,24395-BK,63001-B-WT,10481-BK,73010-KHK,13002-WT,51009-PK
models.execute_kw(db, uid, password, 'posterior_passage_output_value_week', 'write', [[res[0]], {
    'style_number': "10461-BK,63002-WT,24395-BK,63001-B-WT,10481-BK,73010-KHK,13002-WT,51009-PK,10461-3-BK"
}])