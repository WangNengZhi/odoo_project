# -*- coding: utf-8 -*-
{
    'name': "FSN_基础模块",

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
    'depends': ['base'],

    # always loaded
    "qweb": [
        "static/xml/file_upload.xml",
        "static/xml/fsn_month.xml",
    ],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/fsn_size.xml',
        'views/fsn_color.xml',
        'views/fsn_unit.xml',
        'views/fsn_staff_team.xml',
        'views/data_export_setting.xml',
        'views/fsn_source_where.xml',
        'data/fsn_base_group.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}
