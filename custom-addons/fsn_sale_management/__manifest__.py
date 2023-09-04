# -*- coding: utf-8 -*-
{
    'name': "FSN_销售扩展",
    'summary': """
        FSN_销售扩展
    """,
    'description': """
        FSN_销售扩展
    """,

    'author': "wdc",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'sale_pro', 'warehouse_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_pro.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
}
