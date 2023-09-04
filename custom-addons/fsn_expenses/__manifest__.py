# -*- coding: utf-8 -*-
{
    'name': "Fsn_费用扩展",

    'summary': """fsn_费用扩展""",

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
    'depends': ['base', 'fsn_base', 'hr_expense', 'hr_expense_extract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/expense_type.xml',
        'views/views.xml',
        'views/templates.xml',
        'data/cost_type_data.xml',
        'data/expense_type_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
