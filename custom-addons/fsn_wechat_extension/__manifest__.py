# -*- coding: utf-8 -*-
{
    'name': "FSN微信小程序扩展",

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
    'depends': ['base', 'suspension_system'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/_inherit_employee.xml',
        'views/wechat_extension_group.xml',
        'views/wechat_process_confirm.xml',
        'views/fsn_delivery_process.xml',
        'views/approval_process_config.xml',
        'views/wechat_delivery.xml',
        'views/menu.xml',
        'data/wechat_extension_group.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}