# -*- coding: utf-8 -*-
{
    'name': "吊挂系统",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

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
    'depends': ['base', 'hr', 'fsn_setting'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/suspension_system_get_seqno.xml',
        'views/suspension_system_details.xml',
        'views/suspension_system_summary.xml',
        'views/check_position_settings.xml',
        'views/suspension_system_line.xml',
        'views/suspension_system_station_summary.xml',
        'views/suspension_system_rework.xml',
        'views/suspension_system_repair.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/index.xml',
    ],
}
