# -*- coding: utf-8 -*-
{
    'name': "盘点",

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
    'depends': ['base', 'sale_pro', 'fsn_production', 'warehouse_management', 'fsn_sale_management', 'pro', 'fsn_sale', 'fsn_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/setting.xml',
        'views/expenses_detail_statistics.xml',
        'views/bank_account.xml',
        'views/fsn_income_detail.xml',
        'views/operating_cost.xml',
        'views/fsn_operate.xml',
        'views/order_cost.xml',
        'views/fsn_charge_up.xml',
        'views/cost_sales.xml',
        'views/views.xml',
        'views/fabric_ingredients_account_month.xml',
        'views/monthly_report_of_labor_costs.xml',
        'views/facturing_cost_month.xml',
        'views/templates.xml',
        'views/fixed_asset_procurement.xml',
        'views/classification_of_fixed_assets.xml',
        'views/accounts_receivable_aging.xml',
        'views/cash_income_and_expenditure_registration.xml',
        # 'views/server_action.xml',    # 服务器动作 未用
        'data/account_type.xml',
        # 'views/ib_detail.xml',
    ],
    "qweb": [
        "static/src/xml/month_choice.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
