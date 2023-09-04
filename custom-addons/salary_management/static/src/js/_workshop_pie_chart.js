// 基于准备好的dom，初始化echarts实例
var salary_pie_chart = echarts.init(document.getElementById('salary_pie_chart'));
var efficiency_pie_chart = echarts.init(document.getElementById('efficiency_pie_chart'));
var day_average_salary_pie_chart = echarts.init(document.getElementById('day_average_salary_pie_chart'));
var day_average_salary_pie_chart_integer = echarts.init(document.getElementById('day_average_salary_pie_chart_integer'));

var salary_option = {
    title: {
        text: '车间薪资',
        // subtext: 'Fake Data',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c}人 ({d}%)',
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
        name: '车间薪资',
        type: 'pie',
        radius: '50%',
        data: [],
        emphasis: {
            itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
        },

    ]
};

// 使用刚指定的配置项和数据显示图表。
salary_pie_chart.setOption(salary_option);


var efficiency_option = {
    title: {
        text: '车间效率（%）',
        // subtext: 'Fake Data',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c}人 ({d}%)',
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
        name: '车间效率（%）',
        type: 'pie',
        radius: '50%',
        data: [],
        emphasis: {
            itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
        }
    ]
};

// 使用刚指定的配置项和数据显示图表。
efficiency_pie_chart.setOption(efficiency_option);




var day_average_salary_option = {
    title: {
        text: '车间日平均薪资',
        // subtext: 'Fake Data',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c}人 ({d}%)',
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
        name: '车间日平均薪资',
        type: 'pie',
        radius: '50%',
        data: [],
        emphasis: {
            itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
        }
    ]
};

// 使用刚指定的配置项和数据显示图表。
day_average_salary_pie_chart.setOption(day_average_salary_option);




var day_average_salary_integer_option = {
    title: {
        text: '车间日平均薪资',
        // subtext: 'Fake Data',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c}人 ({d}%)',
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
        name: '车间日平均薪资',
        type: 'pie',
        radius: '50%',
        data: [],
        emphasis: {
            itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
        }
    ]
};

// 使用刚指定的配置项和数据显示图表。
day_average_salary_pie_chart_integer.setOption(day_average_salary_integer_option);


$("#pie_chart_refresh").click(function(){
    let pie_chart_date = $("#pie_chart_date").val()

    if (pie_chart_date) {
        // 获取薪酬数据
        let salary_list = get_salary_list(pie_chart_date)

        salary_option.series[0].data = salary_list
    
        salary_pie_chart.setOption(salary_option);

        // 获取效率数据
        let efficiency_list = get_efficiency_list(pie_chart_date)

        efficiency_option.series[0].data = efficiency_list

        efficiency_pie_chart.setOption(efficiency_option);

        // 获取日均薪资数据
        let day_average_salary_list = get_day_average_salary_list(pie_chart_date)

        day_average_salary_option.series[0].data = day_average_salary_list

        day_average_salary_pie_chart.setOption(day_average_salary_option);


        // # 获取日均薪资数据(整数分布)
        let day_average_salary_integer_list = get_day_average_salary_integer_list(pie_chart_date)

        day_average_salary_integer_option.series[0].data = day_average_salary_integer_list

        day_average_salary_pie_chart_integer.setOption(day_average_salary_integer_option);
    
    } else {
        alert("未设置月份！")
    }

});

// 获取日均薪资数据
function get_day_average_salary_list(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/get_day_average_salary_list",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);
            res_data = res_data.data
        }

    })

    return res_data
}


// # 获取日均薪资数据(整数分布)
function get_day_average_salary_integer_list(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/get_day_average_salary_integer_list",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);
            res_data = res_data.data
        }

    })

    return res_data
}

// 获取薪酬数据
function get_salary_list(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/get_salary_list",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);
            res_data = res_data.data
        }

    })

    return res_data
}
// 获取效率数据
function get_efficiency_list(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/get_efficiency_list",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);
            res_data = res_data.data
        }

    })

    return res_data
    
}