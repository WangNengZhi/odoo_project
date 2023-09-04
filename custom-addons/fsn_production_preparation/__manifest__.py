# -*- coding: utf-8 -*-
{
    'name': "产前准备",

    'summary': """产前准备""",

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
    'depends': ['base', 'fsn_base', 'sale_pro', 'template_house'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/production_preparation_line_sample.xml',
        'views/production_preparation.xml',
        'views/templates.xml',
        'views/fill_materials_application.xml',
        'views/loss_accounting_statement.xml',
        'views/exchange_cutting_piece.xml',
        'views/raw_materials_order.xml',
        'views/production_drop_documents.xml',
        'views/prenatal_preparation_progress.xml',
        'views/menu.xml',
        'data/production_preparation_line_sample_data.xml',

        'report/raw_materials_order_home.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
