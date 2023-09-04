{
    'name': "统计",
    'summary': "统计",
    'description': "统计产值",
    'author': "My Company",
    'version': '0.1',
    'depends': ['base', 'sale_pro', 'mail', 'warehouse_management', 'suspension_system', 'cutting_bed', 'fsn_production_preparation', 'fsn_plan'],
    'data':[
        'views/views.xml',
        'views/pro_pro_week.xml',
        'views/totlepro_totlepro_week.xml',
        'views/ji_jian_week.xml',
        'views/posterior_passage_output_value.xml',
        'views/cutting_bed.xml',
        'views/warehouse_out.xml',
        "views/repair.xml",
        "views/templates.xml",
        "views/style_number_summary.xml",
        "views/casual_wage.xml",    # 临时工工资
        'views/chen_yi_bao_ci.xml',
        'views/following_process_detail.xml',   # 后道进出明细
        'views/posterior_passage_wait_output_value.xml',   # 后道待检产值
        "views/enter_warehouse.xml",    # 入库产值
        "views/day_qing_day_bi.xml",    # 日清日毕
        "views/lose_record.xml",
        "views/warehouse_production.xml",
        "views/outgoing_output.xml",
        "views/schedule_production.xml",
        "views/warehouse_finished_product_stock.xml",
        "views/day_qing_day_bi_wizard.xml",

    ],
    'sequence':1,
    'application': True,
    'qweb':[
        # "static/src/xml/day_qing_day_bi_refresh.xml"
    ],
}