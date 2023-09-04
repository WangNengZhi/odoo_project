# 导入模块
import xmlrpc.client
from datetime import datetime, date
import sys


# 定义 Odoo服务url地址的，数据库名，登录账号，密码
# url, db, username, password = "http://192.168.20.188:8069", "odoo14e", "jh@fsn.com", "jh123456"
url, db, username, password = "http://192.168.75.129:8069", "demo08", "jh@fsn.com", "jh123456"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()

# 获取Odoo的res.users表的id
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))



warehouse_management_ids = models.execute_kw(db, uid, password,
    'warehouse_management', 'search',
    [[]])
    # [[]], {'limit': 100})

warehouse_management_objs = models.execute_kw(db, uid, password,
	"warehouse_management", 'read',
	[warehouse_management_ids],
    {'fields': ['date', 'type', 'number_delivery', 'inbound_order_number', 'inbound_sender', 'inbound_recipient', 'outgoer', 'receiving_customers', 'remark', 'inbound_and_outbound', 'arrival_number']},
	)

for warehouse_management_obj in warehouse_management_objs:

    # 单据编号
    receipt_number = warehouse_management_obj['inbound_order_number'] if warehouse_management_obj['inbound_order_number'] else warehouse_management_obj['number_delivery']
    # 仓库负责人
    warehouse_principal = warehouse_management_obj['inbound_recipient'] if warehouse_management_obj['arrival_number'] else warehouse_management_obj['outgoer']
    # 送货人/接收人
    docking_people = warehouse_management_obj['inbound_sender'] if warehouse_management_obj['arrival_number'] else warehouse_management_obj['receiving_customers']
    # 类型
    type = "入库" if warehouse_management_obj['arrival_number'] else "出库"


    if receipt_number:
        tem_id = models.execute_kw(db, uid, password,
        'finished_product_ware', 'search',
        [[["receipt_number", "=", receipt_number], ["type", "=", type], ["date", "=", warehouse_management_obj["date"]]]])

        if tem_id:
            finished_product_ware_id = tem_id[0]
        else:
            finished_product_ware_id = models.execute_kw(db, uid, password, 'finished_product_ware', 'create', [{
                'date': warehouse_management_obj["date"],
                'receipt_number': receipt_number,
                'type': type,
                'state': "确认",
                'warehouse_principal': warehouse_principal if warehouse_principal else "无",
                'docking_people': docking_people if docking_people else "无",
                'note': warehouse_management_obj['remark'],
            }])
    
    else:

        finished_product_ware_id = models.execute_kw(db, uid, password, 'finished_product_ware', 'create', [{
            'date': warehouse_management_obj["date"],
            'receipt_number': "无",
            'type': type,
            'state': "确认",
            'warehouse_principal': warehouse_principal if warehouse_principal else "无",
            'docking_people': docking_people if docking_people else "无",
            'note': warehouse_management_obj['remark'],
        }])

    inbound_and_outbound_objs = models.execute_kw(db, uid, password,
        "inbound.outbound", 'read',
        [warehouse_management_obj["inbound_and_outbound"]],
        {'fields': ['date', 'style_number', 'item_number', 'warehousing_xs', 'warehousing_s', 'warehousing_m', 'warehousing_l', 'warehousing_xl', 'warehousing_two_xl', 'warehousing_three_xl', 'warehousing_four_xl', 'warehousing_repair_parts', 'warehousing_total',
        'out_of_stock_xs', 'out_of_stock_s', 'out_of_stock_m', 'out_of_stock_l', 'out_of_stock_xl', 'out_of_stock_two_xl', 'out_of_stock_three_xl', 'out_of_stock_four_xl', 'out_of_stock_repair_parts', 'out_of_total']}
        )

    for inbound_and_outbound_obj in inbound_and_outbound_objs:

        def create_finished_product_ware_line(size, quality, number):

            if number < 0:
                quality = "退货"

            fsn_size_id = models.execute_kw(db, uid, password,
                'fsn_size', 'search',
                [[["name", "=", size]]])
            

            print(size, inbound_and_outbound_obj['style_number'], inbound_and_outbound_obj['item_number'], finished_product_ware_id)
            print(fsn_size_id, number, quality)

            models.execute_kw(db, uid, password, 'finished_product_ware_line', 'create', [{
                'finished_product_ware_id': finished_product_ware_id,
                'order_number': inbound_and_outbound_obj['style_number'][0],   # 订单号
                'style_number': inbound_and_outbound_obj['item_number'][0],    # 款号
                'size': fsn_size_id[0],  # 尺码
                'number': number,   # 件数
                'quality': quality,     # 质量
            }])

        if inbound_and_outbound_obj["warehousing_total"]:   # 入库
            if inbound_and_outbound_obj["warehousing_xs"]:
                create_finished_product_ware_line("XS", "合格", inbound_and_outbound_obj["warehousing_xs"])
            if inbound_and_outbound_obj["warehousing_s"]:
                create_finished_product_ware_line("S", "合格", inbound_and_outbound_obj["warehousing_s"])
            if inbound_and_outbound_obj["warehousing_m"]:
                create_finished_product_ware_line("M", "合格", inbound_and_outbound_obj["warehousing_m"])
            if inbound_and_outbound_obj["warehousing_l"]:
                create_finished_product_ware_line("L", "合格", inbound_and_outbound_obj["warehousing_l"])
            if inbound_and_outbound_obj["warehousing_xl"]:
                create_finished_product_ware_line("XL", "合格", inbound_and_outbound_obj["warehousing_xl"])
            if inbound_and_outbound_obj["warehousing_two_xl"]:
                create_finished_product_ware_line("XXL", "合格", inbound_and_outbound_obj["warehousing_two_xl"])
            if inbound_and_outbound_obj["warehousing_three_xl"]:
                create_finished_product_ware_line("XXXL", "合格", inbound_and_outbound_obj["warehousing_three_xl"])
            if inbound_and_outbound_obj["warehousing_four_xl"]:
                create_finished_product_ware_line("XXXXL", "合格", inbound_and_outbound_obj["warehousing_four_xl"])
            if inbound_and_outbound_obj["warehousing_repair_parts"]:
                create_finished_product_ware_line("S", "退货", inbound_and_outbound_obj["warehousing_repair_parts"])
        elif inbound_and_outbound_obj["out_of_total"]:  # 出库
            if inbound_and_outbound_obj["out_of_stock_xs"]:
                create_finished_product_ware_line("XS", "合格", inbound_and_outbound_obj["out_of_stock_xs"])
            if inbound_and_outbound_obj["out_of_stock_s"]:
                create_finished_product_ware_line("S", "合格", inbound_and_outbound_obj["out_of_stock_s"])
            if inbound_and_outbound_obj["out_of_stock_m"]:
                create_finished_product_ware_line("M", "合格", inbound_and_outbound_obj["out_of_stock_m"])
            if inbound_and_outbound_obj["out_of_stock_l"]:
                create_finished_product_ware_line("L", "合格", inbound_and_outbound_obj["out_of_stock_l"])
            if inbound_and_outbound_obj["out_of_stock_xl"]:
                create_finished_product_ware_line("XL", "合格", inbound_and_outbound_obj["out_of_stock_xl"])
            if inbound_and_outbound_obj["out_of_stock_two_xl"]:
                create_finished_product_ware_line("XXL", "合格", inbound_and_outbound_obj["out_of_stock_two_xl"])
            if inbound_and_outbound_obj["out_of_stock_three_xl"]:
                create_finished_product_ware_line("XXXL", "合格", inbound_and_outbound_obj["out_of_stock_three_xl"])
            if inbound_and_outbound_obj["out_of_stock_four_xl"]:
                create_finished_product_ware_line("XXXXL", "合格", inbound_and_outbound_obj["out_of_stock_four_xl"])
            if inbound_and_outbound_obj["out_of_stock_repair_parts"]:
                create_finished_product_ware_line("S", "退货", inbound_and_outbound_obj["out_of_stock_repair_parts"])
        else:
            pass


