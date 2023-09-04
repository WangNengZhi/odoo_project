# -*- coding: utf-8 -*-
{
    'name': "裁床管理",

    'summary': """裁床管理""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base', 'fsn_plan'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/cutting_bed_setting.xml',
        'views/cutting_bed_production_record.xml',
        'views/automatic_cutting_bed.xml',
        'views/cutting_bed_production.xml',
        'views/menu.xml',
        'data/cutting_bed_connect_setting_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
