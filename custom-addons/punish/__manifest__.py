# -*- coding: utf-8 -*-
{
    'name': "绩效考核",

    'summary': """绩效考核""",

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
    'depends': ['base', 'mail', 'fsn_employee', 'fsn_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/personnel_award.xml',
        'views/quality_control_performance.xml',
        'views/lock_grade_check_attendance.xml',
        'views/hard_working_workers_of_year.xml',
        'views/lack_card_generate_ticket_wizard.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
