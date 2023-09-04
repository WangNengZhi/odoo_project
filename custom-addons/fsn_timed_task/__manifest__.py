# -*- coding: utf-8 -*-
{
    'name': "定时任务",

    'summary': """
        定时任务
    """,

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
    'depends': ['base',
        'fsn_production_preparation',
        'mail',
        'suspension_system',
        'sale_pro',
        'pro',
        'fsn_employee'
        ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/inspection_task.xml',
        'data/inspect_channel.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
