# -*- coding: utf-8 -*-
{
    'name': "FSN_外发",

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
    'depends': ['base', 'fsn_base', 'sale_pro'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/outsource_plant_process_type.xml',
        'views/outsource_plant_pl_type.xml',
        'views/outsource_plant_resources_type.xml',
        'views/outsource_plant.xml',
        'views/outsource_order.xml',
        'views/outbound_price.xml',
        'views/outsource_fabirc_production.xml',
        'views/outsource_fabirc_retreat.xml',
        'views/outsource_surface_material.xml',
        'views/outbource_return.xml',
        'views/outbound_order_progress.xml',
        'views/production_order_details.xml',
        'views/menu.xml',
        'controllers/enterprise_wechat/outward_delivery_approve/fsn_size_select.xml',
        'controllers/enterprise_wechat/outward_delivery_approve/fsn_workwx_order_number_select.xml',
        'controllers/enterprise_wechat/outward_delivery_approve/fsn_workwx_outsource_order_line_select.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
