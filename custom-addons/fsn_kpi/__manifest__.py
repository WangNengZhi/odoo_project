# -*- coding: utf-8 -*-
{
    'name': "FSN_KPI",

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
    'depends': ['base', 'hr', 'web', 'fsn_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fsn_kpi_assess_project.xml',     # KPI考核项目
        'views/menu.xml',

        'views/views.xml',
        'views/templates.xml',
        'views/_inherit_hr_department.xml',    # KPI部门继承
        'views/fsn_kpi_template.xml',   # KPI模板
        'views/fsn_kpi.xml',   # KPI
        'data/fsn_kpi_group_data.xml',     # KPI群组数据




        # 'data/fsn_kpi_template_data.xml',   # 模板数据


        # 'views/kpi_template.xml',
        # 'views/after_whole_special_kpi.xml',
        
        # 'data/special_kpi_line_template.xml',   # 专机
        # 'data/sample_emp_kpi_line_template.xml',    # 样衣员
        # 'data/office_dir_kpi_line_template.xml',    # 办公室主任
        # 'data/technical_director_kpi_line_template.xml',    # 技术主管
        # 'data/workshop_dir_kpi_line_template.xml',      # 车间主任
        # 'data/human_resources_kpi_line_template.xml',   # 人事专员
        # 'data/human_head_kpi_line_template.xml',    # 人事主管
        # 'data/packaging_kpi_line_template.xml',    # 包装
        # 'data/big_iron_kpi_line_template.xml',    # 大烫
        # 'data/small_iron_kpi_line_template.xml',    # 小烫
        # 'data/lathe_worker_kpi_line_template.xml',      # 车工
        # 'data/template_molecule_kpi_line_template.xml',      # 模板师
        # 'data/group_leader_kpi_line_template.xml',      # 组长
        # 'data/collating_bills_kpi_line_template.xml',      # 理单员
        # 'data/ie_kpi_line_template.xml',      # IE
        # 'data/machine_fix_kpi_line_template.xml',      # 机修


        'report/kpi_template_qweb.xml',     # kpi打印
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
