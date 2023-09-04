# -*- coding: utf-8 -*-
{
    'name': "FSN_会计（精斗云）",

    'summary': """金蝶精斗云会计对接。""",

    'description': """金蝶精斗云会计对接。""",


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
        'views/jdy_setting.xml',
        'data/jdy_setting.xml',
        'views/jdy_subject.xml',
        'views/jdy_expenses_details.xml',
        'views/fsn_accounting_detail.xml',
        'views/cost_breakdown_system.xml',
        'views/menu.xml',
        
        'views/fsn_res_bank_exp.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
