# -*- coding: utf-8 -*-
{
    'name': "FSN_电商",

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
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/platform_type.xml',
        'views/platform_linkman.xml',
        'views/ec_product_data.xml',
        'views/ec_live_audience_analysis.xml',
        'views/ec_live_data_collect.xml',
        'views/ec_task.xml',
        'views/ec_results_manage.xml',
        'views/platform_account.xml',
        'views/flow_conversion_efficiency.xml',
        'views/ec_video_data.xml',
        'views/ec_flow_channel.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
