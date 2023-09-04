# -*- coding: utf-8 -*-
{
    'name': "生产订单管理",
    'summary': "生产订单管理",
    'description': "生产订单管理",
    'author': "XU",
    'version': '0.1',
    'depends': ['base', 'fsn_base', 'mail'],
    'data': [
        'views/order_attribute.xml',
        'views/views.xml',
        'views/fsn_customer.xml',
        'views/sale_pro_bar_code.xml',
        'views/fsn_sales_return.xml',
        'views/menu.xml',
        'report/tags.xml',     # 吊牌打印
    ],
    'sequence': 1,
    'application': True,
}