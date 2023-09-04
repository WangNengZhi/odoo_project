// 基于准备好的dom，初始化echarts实例
var amoeba_workshop = echarts.init(document.getElementById('amoeba_workshop'));
var amoeba_after_road = echarts.init(document.getElementById('amoeba_after_road'));
var amoeba_cutting_bed = echarts.init(document.getElementById('amoeba_cutting_bed'));
var amoeba_total_workshop = echarts.init(document.getElementById('amoeba_total_workshop'));

var amoeba_workshop_option = {
	tooltip: {
		trigger: 'axis',
		axisPointer: {
		type: 'cross',
		crossStyle: {
			color: '#999'
		}
		}
	},
	legend: {
		data: ['产值', '薪资']
	},
	xAxis: [
		{
		type: 'category',
		data: [],
		axisPointer: {
			type: 'shadow'
		}
		}
	],
	yAxis: [
		{
			type: 'value',
		},
	],
	series: [
		{
		name: '产值',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
		{
		name: '薪资',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
	]
};

// 使用刚指定的配置项和数据显示图表。
amoeba_workshop.setOption(amoeba_workshop_option);



var amoeba_after_road_option = {
	tooltip: {
		trigger: 'axis',
		axisPointer: {
		type: 'cross',
		crossStyle: {
			color: '#999'
		}
		}
	},
	legend: {
		data: ['产值', '薪资']
	},
	xAxis: [
		{
		type: 'category',
		data: [],
		axisPointer: {
			type: 'shadow'
		}
		}
	],
	yAxis: [
		{
			type: 'value',
		},
	],
	series: [
		{
		name: '产值',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
		{
		name: '薪资',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
	]
};

amoeba_after_road.setOption(amoeba_after_road_option);

var amoeba_cutting_bed_option = {
	tooltip: {
		trigger: 'axis',
		axisPointer: {
		type: 'cross',
		crossStyle: {
			color: '#999'
		}
		}
	},
	legend: {
		data: ['产值', '薪资']
	},
	xAxis: [
		{
		type: 'category',
		data: [],
		axisPointer: {
			type: 'shadow'
		}
		}
	],
	yAxis: [
		{
			type: 'value',
		},
	],
	series: [
		{
		name: '产值',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
		{
		name: '薪资',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
	]
};

amoeba_cutting_bed.setOption(amoeba_cutting_bed_option);


var amoeba_total_workshop_option = {
	tooltip: {
		trigger: 'axis',
		axisPointer: {
		type: 'cross',
		crossStyle: {
			color: '#999'
		}
		}
	},
	legend: {
		data: ['产值', '薪资']
	},
	xAxis: [
		{
		type: 'category',
		data: [],
		axisPointer: {
			type: 'shadow'
		}
		}
	],
	yAxis: [
		{
			type: 'value',
		},
	],
	series: [
		{
		name: '产值',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
		{
		name: '薪资',
		type: 'bar',
		tooltip: {
			valueFormatter: function (value) {
			return value;
			}
		},
		data: []
		},
	]
};

amoeba_total_workshop.setOption(amoeba_total_workshop_option);

function sum(arr) {
	return eval(arr.join("+"));
}

$("#pie_chart_refresh").click(function(){
    let pie_chart_date = $("#pie_chart_date").val()

    if (pie_chart_date) {

        // 获取车间各组产值和总薪资
        let amoeba_workshop_option_data = get_amoeba_workshop_option_data(pie_chart_date)
        if (amoeba_workshop_option_data.status == "1") {
			amoeba_workshop_option.xAxis[0].data = amoeba_workshop_option_data.data.group_list
			amoeba_workshop_option.series[0].data = amoeba_workshop_option_data.data.output_value_list.map((item) => {
				return Number(item).toFixed(2);
			})
			amoeba_workshop_option.series[1].data = amoeba_workshop_option_data.data.salary_list.map((item) => {
				return Number(item).toFixed(2);
			})

        } else {
			alert("没有查询到该月份的薪酬信息！")
			return
        }
        amoeba_workshop.setOption(amoeba_workshop_option);

		let amoeba_total_workshop_data = get_amoeba_total_workshop_data(pie_chart_date)
        if (amoeba_total_workshop_data.status == "1") {

			amoeba_total_workshop_option.xAxis[0].data = amoeba_total_workshop_data.data.group_list
			amoeba_total_workshop_option.series[0].data = amoeba_total_workshop_data.data.total_workshop_value_list.map((item) => {
				return Number(item).toFixed(2);
			})
			amoeba_total_workshop_option.series[1].data = amoeba_total_workshop_data.data.salary_list.map((item) => {
				return Number(item).toFixed(2);
			})
		} else {
			alert("没有查询到该月份的薪酬信息！")
			return
		}

		amoeba_total_workshop.setOption(amoeba_total_workshop_option);

		// 获取后道产值和薪资
		let amoeba_after_road_data = get_amoeba_after_road_data(pie_chart_date)
		if (amoeba_after_road_data.status == "1") {
			amoeba_after_road_option.xAxis[0].data = amoeba_after_road_data.data.group_list
			amoeba_after_road_option.series[0].data = amoeba_after_road_data.data.after_road_value_list.map((item) => {
				return Number(item).toFixed(2);
			})
			amoeba_after_road_option.series[1].data = amoeba_after_road_data.data.salary_list.map((item) => {
				return Number(item).toFixed(2);
			})
		} else {
			alert("没有查询到该月份的薪酬信息！")
			return
		}
		amoeba_after_road.setOption(amoeba_after_road_option);


		// 获取裁床产值和薪资
		let amoeba_cutting_bed_data = get_amoeba_cutting_bed_data(pie_chart_date)
		if (amoeba_after_road_data.status == "1") {
			amoeba_cutting_bed_option.xAxis[0].data = amoeba_cutting_bed_data.data.group_list
			amoeba_cutting_bed_option.series[0].data = amoeba_cutting_bed_data.data.cutting_bed_value_list.map((item) => {
				return Number(item).toFixed(2);
			})
			amoeba_cutting_bed_option.series[1].data = amoeba_cutting_bed_data.data.salary_list.map((item) => {
				return Number(item).toFixed(2);
			})
		} else {
			alert("没有查询到该月份的薪酬信息！")
			return
		}
		amoeba_cutting_bed.setOption(amoeba_cutting_bed_option);



    }
});


// 获取车间各组产值和总薪资
function get_amoeba_workshop_option_data(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/salary_management/get_amoeba_workshop_option_data",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);

        }

    })

    return res_data
}


// 获取车间总产值和总薪资
function get_amoeba_total_workshop_data(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/salary_management/get_amoeba_total_workshop_data",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);

        }

    })

    return res_data
}



// 获取后道产值和薪资
function get_amoeba_after_road_data(pie_chart_date) {

    let res_data

    $.ajax({
        url: "/salary_management/get_amoeba_after_road_data",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);

        }

    })

    return res_data
}


// 获取裁床产值和薪资
function get_amoeba_cutting_bed_data(pie_chart_date) {
    let res_data

    $.ajax({
        url: "/salary_management/get_amoeba_cutting_bed_data",
        method: "get",
        async: false,
        data: {
            "date": pie_chart_date,
        },
        success: function (res) {
            res_data = $.parseJSON(res);

        }

    })

    return res_data
}