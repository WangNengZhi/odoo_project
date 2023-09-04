# -*- coding: utf-8 -*-
{
    'name': "FSN企业微信扩展",

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
    'depends': ['base', 'fsn_outsource'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/fsn_work_wx_approval_record.xml',
        'views/menu.xml',
        'views/workwx_select_page.xml',
    ],

}
