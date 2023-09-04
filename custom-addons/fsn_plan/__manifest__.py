# -*- coding: utf-8 -*-
{
    'name': "风丝袅_计划",

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
    'depends': ['base', 'planning', 'web_gantt', 'sale_pro'],

    # always loaded
    'data': [
        # 'static/src/xml/fsn_plan_templates.xml',
        'views/fsn_plan.xml',
        # 'views/fsn_plan_wizard.xml',
        'views/fsn_month_plan.xml',
        'views/target_output_value.xml',
        'views/target_output_value_top.xml',
        'views/send_out_output_value.xml',
        'views/quality_control_output_value.xml',
        'views/quality_control_dep_output_value.xml',
        'views/technology_output_value.xml',
        'views/personnel_manage.xml',
        'views/menu.xml',
        'views/templates.xml',
        'views/develop_manage.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/fsn_plan_templates.xml",
    ]
}
