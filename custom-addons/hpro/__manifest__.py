{
    'name': "工时工序",
    'summary': "工时工序",
    'description': "工时工序",
    'author': "My Company",
    'version': '0.1',
    'depends': ['base','mail','hr', 'pro', 'fsn_base', 'suspension_system', 'fsn_bom'],
    'data':['views/templates.xml',
            'views/views.xml',
            'views/em.xml',
            'views/material_table.xml',
            'views/attendance.xml',
            'views/material_list.xml',
            'views/hr_search.xml',
            'views/xinzi.xml',
			'views/reality_material_list.xml',
            'views/planning_sheet.xml',

            'views/automatic_scene_process.xml',    # 自动工序
            'views/automatic_efficiency_table.xml',     # 自动效率表
            'views/automatic_process_comparison.xml',       # 自动工序对比
            "views/automatic_dg_piece_rate.xml",    # 吊挂计件工资
            "views/automatic_employee_information.xml",    # 自动员工信息表
            'views/fsn_bom_total_cost.xml',
            'views/fsn_bom_planning_sheet.xml',
            'views/long_term_temp_rate.xml',
            "views/menu.xml",
            ],
    'sequence':1,
    'application': True,
}