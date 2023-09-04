# -*- coding: utf-8 -*-
{
    'name': "板房管理",

    'summary': """板房管理""",

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
    'depends': ['base', 'fsn_base'],

    # always loaded
    'data': [
        'data/template_house_group.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/machine_setting.xml',
        'views/template_machine_record.xml',
        'views/template_income.xml',

        'views/th_per_management.xml',
        'views/fsn_platemaking_record.xml',
        'views/fsn_template_record.xml',
        'views/fsn_process_sheet.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
