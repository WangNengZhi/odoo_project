# -*- coding: utf-8 -*-
{
    'name': "FSN_BOM",

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
    'depends': ['base', 'fsn_base','sale_pro', 'template_house', 'warehouse_management'],


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/fsn_bom_groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sheet_materials.xml',
        'views/practical_material.xml',
        'views/material_variation.xml',
        'views/variation_preset.xml',
        'views/material_summary_sheet.xml',
        'views/total_cost.xml',
        'views/sheet_materials_line.xml',
        'views/surface_accessories_loss.xml',
        'views/material_name_list.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
