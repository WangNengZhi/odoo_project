# -*- coding: utf-8 -*-
{
    'name': "仓库管理",
    'summary': "仓库管理",
    'description': "仓库管理",
    'author': "XU",
    'version': '0.1',
    'depends': ['base', 'sale_pro', 'fsn_base', 'procurement', 'fsn_outsource', 'fsn_production_preparation'],
    'data': [
        'views/views.xml',
        'views/mian_fu_liao_bu_liao.xml',
        'views/material_code.xml',

        'views/customer_repair.xml',
        'views/material_list.xml',
        'views/warehouse_bom.xml',
        'views/warehouse_bom_outbound.xml',
        'views/warehouse_bom_inventory.xml',
        'views/warehouse_bom_inventory_month.xml',
        'views/plus_material_list.xml',
        'views/plus_material_enter.xml',
        'views/plus_material_inventory.xml',
        'views/plus_material_inventory_month.xml',
        'views/plus_material_outbound.xml',
        'views/production_operation_ingredients_list.xml',
        'views/production_operation_ingredients_enter.xml',
        'views/production_operation_ingredients_inventory.xml',
        'views/production_operation_ingredients_outbound.xml',
        'views/finished_product_ware.xml',
        'views/finished_product_ware_line.xml',
        'views/finished_inventory.xml',
        'views/finished_inventory_actionstatistics.xml',
        'views/fabric_ingredients_procurement.xml',
        'views/fabric_ingredients_refund.xml',
        'views/finished_product_warehouse_statistical.xml',
        'views/outsource_order.xml',
        'views/spare_fabric_storage.xml',
        'views/spare_fabric_inventory_month.xml',
        'views/spare_material_storage.xml',
        'views/spare_material_inventory_month.xml',
        'views/menu.xml',
        'views/maintain_warehouse_menu.xml',
        'data/groups.xml',
    ],
    'sequence': 1,
    'application': True,
}