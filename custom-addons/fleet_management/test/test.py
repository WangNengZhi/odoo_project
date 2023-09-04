# 导入模块
import xmlrpc.client


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "rszg@fsn.com", "rszg123456"
# url, db, username, password = "http://192.168.75.129:8069", "demo08", "rszg@fsn.com", "rszg123456"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))


fleet_management_ids = models.execute_kw(db, uid, password,
    'fleet_management', 'search',
    [[]])

record_ids = models.execute_kw(db, uid, password,
    'fleet_management', 'read', [fleet_management_ids])

for record in record_ids:
    print(record, record["user_people"], record["return_people"])

    hr_employee_id = models.execute_kw(db, uid, password,
    'hr.employee', 'search',
    [[["name", "=", record["user_people"]]]])

    if hr_employee_id:

        models.execute_kw(db, uid, password, 'fleet_management', 'write', [[record["id"]], {
            'user_people_id': hr_employee_id[0],
            'return_people_id': hr_employee_id[0]
        }])