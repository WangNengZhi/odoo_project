import { get_today_dg_data } from "/fsn_data_screen/static/src/js/get_suspension_system_data.js";

// 获取在职人数
function get_number_employees() {
    $.ajax({
        url: "/get_number_employees",
        method: "get",
        async: false
    }).success(function (res) {
        let res_obj = $.parseJSON(res);

        $("#window_02_val_01").text(res_obj.number_employees);
    })
}

// 获取订单数
function get_number_orders() {
    $.ajax({
        url: "/get_number_orders",
        method: "get",
        async: false
    }).success(function (res) {
        let res_obj = $.parseJSON(res);

        $("#window_02_val_02").text(res_obj.number_orders);
    })
}

// 获取当月以及当天产值
function get_month_output_value() {

    // 当月产值
    var month_output_value = 0

    // 获取当月产值
    $.ajax({
        url: "/get_month_output_value",
        method: "get",
        async: false
    }).success(function (res) {

        let res_obj = $.parseJSON(res);
        month_output_value = month_output_value + res_obj.month_output_value
    })

    // 获取当日产值
    let today_output_value = 0
    $(".output_value").each(function(){
        today_output_value = today_output_value + Number($(this).text())
    })

    month_output_value = month_output_value + today_output_value

    $("#window_02_val_03").text(month_output_value.toFixed(2));
    $("#window_02_val_04").text(today_output_value.toFixed(2));

}

// 获取在职人数
get_number_employees()
// 获取订单数
get_number_orders()
// 获取当月以及当天产值
get_month_output_value()

// window.setInterval(get_month_output_value, 1000);



// -------------------分割线------------------------------------------

var chart2_1 = echarts.init(document.getElementById('window_02_1'));
var chart2_2 = echarts.init(document.getElementById('window_02_2'));
var chart2_3 = echarts.init(document.getElementById('window_02_3'));
var chart2_4 = echarts.init(document.getElementById('window_02_4'));

var data1 = [
                {
                    name: "裁床",
                    value: 0,
                },
                {
                    name: "车间",
                    value: 0,
                },
                {
                    name: "后道",
                    value: 0,
                },
                {
                    name: "仓库",
                    value: 0,
                }
            ];

var colorTemplate1 = [
    [0.2, "#13dcea"],
    [0.8, "#13dcea"],
    [1, "#13dcea"]
];



var option2 = [{

    series: [{
        name: "yuxingshudu",
        type: "gauge",
        radius: "100%",
        center: ["50%", "55%"],
        min: 0,
        max: 100,
        splitNumber: 8,

        axisLine: {
            show: true, // 是否显示仪表盘轴线(轮廓线),默认 true。
            lineStyle: {
                color: colorTemplate1,
                width: 6
            }
        },
        pointer: {
            width: 4
        },

        axisLabel: {
            show: true,
            distance: 4,
            color: "#0fa5b6",
            fontSize: 6,
            formatter: "{value}",
        },
        splitLine: { // 分隔线样式。
            show: true,
            length: 6,
        },

        itemStyle: {
            color: "#056094",
            opacity: 1,
        },
        title: { // 仪表盘标题。
            show: true,
            offsetCenter: [0,
                "80%"
            ],
            color: "#13dcea",
            fontSize: 12,
        },

        detail: {
            show: true,
            offsetCenter: [0,
                "40%"
            ],
            color: "auto",
            fontSize: 10,
        },

        data: [
            data1[0]
        ]
    }]

},
// biaopan2
{

    series: [{
        name: "单机效率",
        type: "gauge",
        radius: "100%",
        center: ["50%", "55%"],
        min: 0,
        max: 100,
        splitNumber: 8,

        axisLine: {
            show: true, // 是否显示仪表盘轴线(轮廓线),默认 true。
            lineStyle: {
                color: colorTemplate1,
                width: 6
            }
        },
        pointer: {
            width: 4
        },

        axisLabel: {
            show: true,
            distance: 4,
            color: "#0fa5b6",
            fontSize: 6,
            formatter: "{value}",
        },
        splitLine: { // 分隔线样式。
            show: true,
            length: 6,
        },

        itemStyle: {
            color: "#056094",
            opacity: 1,
        },
        title: { // 仪表盘标题。
            show: true,
            offsetCenter: [0,
                "80%"
            ],
            color: "#13dcea",
            fontSize: 12,
        },

        detail: {
            show: true,
            offsetCenter: [0,
                "40%"
            ],
            color: "auto",
            fontSize: 10,
        },

        data: [
            data1[1]
        ]
    }]

},
// biao 3
{

    series: [{
        name: "单机效率",
        type: "gauge",
        radius: "100%",
        center: ["50%", "55%"],
        min: 0,
        max: 100,
        splitNumber: 8,

        axisLine: {
            show: true, // 是否显示仪表盘轴线(轮廓线),默认 true。
            lineStyle: {
                color: colorTemplate1,
                width: 6
            }
        },
        pointer: {
            width: 4
        },

        axisLabel: {
            show: true,
            distance: 4,
            color: "#0fa5b6",
            fontSize: 6,
            formatter: "{value}",
        },
        splitLine: { // 分隔线样式。
            show: true,
            length: 6,
        },

        itemStyle: {
            color: "#056094",
            opacity: 1,
        },
        title: { // 仪表盘标题。
            show: true,
            offsetCenter: [0,
                "80%"
            ],
            color: "#13dcea",
            fontSize: 12,
        },

        detail: {
            show: true,
            offsetCenter: [0,
                "40%"
            ],
            color: "auto",
            fontSize: 10,
        },

        data: [
            data1[2]
        ]
    }]

},
// biao 4
{

    series: [{
        name: "单机效率",
        type: "gauge",
        radius: "100%",
        center: ["50%", "55%"],
        min: 0,
        max: 100,
        splitNumber: 8,

        axisLine: {
            show: true, // 是否显示仪表盘轴线(轮廓线),默认 true。
            lineStyle: {
                color: colorTemplate1,
                width: 6
            }
        },
        pointer: {
            width: 4
        },

        axisLabel: {
            show: true,
            distance: 4,
            color: "#0fa5b6",
            fontSize: 6,
            formatter: "{value}",
        },
        splitLine: { // 分隔线样式。
            show: true,
            length: 6,
        },

        itemStyle: {
            color: "#056094",
            opacity: 1,
        },
        title: { // 仪表盘标题。
            show: true,
            offsetCenter: [0,
                "80%"
            ],
            color: "#13dcea",
            fontSize: 12,
        },

        detail: {
            show: true,
            offsetCenter: [0,
                "40%"
            ],
            color: "auto",
            fontSize: 10,
        },

        data: [
            data1[3]
        ]
    }]

},
];

// 车间计划仪表盘
function set_workshop_dashboard() {

    $.ajax({
        url: "/get_today_plan_workshop",
        method: "get",
        async: false,
        data: {
            "dashboard_name": "车间"
        },
    }).success(function (res) {
        let res_obj = $.parseJSON(res);
        let plan_count = res_obj.plan_count

        if (plan_count != 0) {

            let count = 0

            $("#group_output .tem_data").each(function() {

                for (var i of $(this).get()) {
                    let tem_list = i.getElementsByTagName("td")

                    count = count + Number(tem_list[3].innerHTML)
                }

            })
            // 给数据源赋值
            data1[1].value = Number(((count / plan_count) * 100).toFixed(0))
            // 生成仪表盘
            chart2_2.setOption(option2[1])

        }

    })
}



// 裁床计划仪表盘
function set_cutting_bed_dashboard() {

    $.ajax({
        url: "/get_recently_cutting_bed",
        method: "get",
        async: false,
    }).success(function (res) {

        let res_obj = $.parseJSON(res);
        let actual_number = res_obj.cutting_bed_count
        let today = res_obj.today

        $.ajax({
            url: "/get_today_plan_workshop",
            method: "get",
            async: false,
            data: {
                "today": today,
                "dashboard_name": "裁床"
            },
        }).success(function (res) {

            let res_obj = $.parseJSON(res);

            // 给数据源赋值
            data1[0].value = Number(((actual_number / res_obj.plan_count) * 100).toFixed(0))
            // 生成仪表盘
            chart2_1.setOption(option2[0])
        })


    })

}



// 后道计划仪表盘
function set_after_road_dashboard() {

    $.ajax({
        url: "/get_today_plan_workshop",
        method: "get",
        async: false,
        data: {
            "dashboard_name": "后道"
        },
    }).success(function (res) {
        let res_obj = $.parseJSON(res);
        let plan_count = res_obj.plan_count

        if (plan_count != 0) {

            let data_list = get_today_dg_data("后道")

            let count = 0
            for (let record of data_list) {
                count = count + record.nNumber
            }

            // 给数据源赋值
            data1[2].value = Number(((count / plan_count) * 100).toFixed(0))
            // 生成仪表盘
            chart2_3.setOption(option2[2])

        }

    })

}


// 仓库仪表盘
function set_warehouse_dashboard() {
    $.ajax({
        url: "/get_order_voucher_number",
        method: "get",
        async: false,
        // data: {
        //     "dashboard_name": "后道"
        // },
    }).success(function (res) {
        let res_obj = $.parseJSON(res);
        console.log(res_obj);

        // 给数据源赋值
        data1[3].value = Number((res_obj.warehouse_outbound_progress * 100).toFixed(0))
        // 生成仪表盘
        chart2_4.setOption(option2[3])
    })

}


// 使用刚指定的配置项和数据显示图表
// chart2_1.setOption(option2[0])

// chart2_4.setOption(option2[3])


export { get_month_output_value, set_workshop_dashboard, set_cutting_bed_dashboard, set_after_road_dashboard, set_warehouse_dashboard};


