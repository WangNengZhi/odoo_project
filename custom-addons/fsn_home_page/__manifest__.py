# -*- coding: utf-8 -*-
{
    'name': "FSN主页扩展",

    'summary': """FSN主页扩展""",

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
    'depends': ['base', 'web_enterprise', 'fsn_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/scroll_bar_config.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': [
        'static/src/xml/fsn_home_page_roll.xml',
    ],
}
