# -*- coding: utf-8 -*-
{
    'name': "FSN设计部",

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

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'sequence':1,
    'application': True,
    # always loaded
    'data': [
        'security/fsn_design_department.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',

        'views/product_design.xml',
        'views/design_department_performance.xml',
        'views/menu.xml',



    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
