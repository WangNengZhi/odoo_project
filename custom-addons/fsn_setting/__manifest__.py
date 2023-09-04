# -*- coding: utf-8 -*-
{
    'name': "fsn_设置",

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
    'sequence':1,
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/del_logo.xml',
        'views/data_refresh_frequency.xml',
        'views/fsn_kanban_setting.xml',
        'views/yingshi_cloud_setting.xml',
        'data/yingshi_cloud_setting_data.xml',
        # 'data/token_record.xml',

        'views/fsn_dg_setting.xml',
        'data/fsn_dg_setting_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
