# -*- coding: utf-8 -*-
{
    'name': "FSN后整管理",

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
    'depends': ['base', 'fsn_plan', 'suspension_system', 'warehouse_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/back_channel_progress_job_setting_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/back_channel_progress_job_setting.xml',
        'views/back_channel_progress.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
