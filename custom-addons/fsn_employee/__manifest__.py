# -*- coding: utf-8 -*-
{
    'name': "FSN_员工扩展",

    'summary': """
        FSN_员工扩展""",

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
    'depends': ['base', 'hr', 'hpro', 'fsn_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/fsn_employee_extend.xml',
        'views/ww_internal_post_transfer.xml',
        'views/become_full_member.xml',
        'views/advance_of_wages.xml',   # 预支工资记录
        'views/_inherit_employee_epiboly.xml',  # 外包计件明细
        'views/allowance_subsidy_setting.xml',  # 津贴补助设置
        'views/hr_employee_social_security.xml',  # 津贴补助设置
        # 'views/hr_employee_dynamics.xml',  # 每日在职员工
        'views/temporary_workers_apply.xml',
        'views/inherit_job.xml',
        'views/epiboly_contract_line.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
