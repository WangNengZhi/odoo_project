# -*- coding: utf-8 -*-
{
    'name': "采购",

    'summary': """采购""",

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
    "qweb": [
        "static/src/xml/material_type_selection.xml",
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/procurement_group_.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/supplier_supplier.xml',  # 供应商

        'views/office_object_instance.xml',
        'views/office_procurement_inventory.xml',
        'views/office_procurement_put.xml',
        'views/office_procurement_enter.xml',
        'views/office_procurement_outbound.xml',

        'views/template_purchase_order.xml',
        'views/equipment_leasing.xml',
        'views/maintain_object_instance.xml',
        'views/maintain_inventory.xml',
        'views/maintain_procurement.xml',
        'views/maintain_recipients.xml',
        'views/maintain_return.xml',
        'views/maintain_put.xml',
        'views/asset_classification.xml',
        'views/use_registration_form.xml',
        'views/maintenance_records.xml',


        'views/fabric_ingredients_procurement.xml',
        'views/fabric_ingredients_refund.xml',
        'views/fabric_ingredients_summary.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
