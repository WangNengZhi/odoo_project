

// 排序函数
function compare(property){
    return function(a,b){
        var value1 = a[property];
        var value2 = b[property];
        return value1 - value2;
    }
}


// 获取当日计划数据
function get_today_plan_data() {
    $.ajax({
        url: "/get_today_plan/",
        method: "get",
        async: false
    }).success(function (res) {
        let res_obj = $.parseJSON(res);

		let tem_obj = {}

		$("#group_output .tem_data").each(function() {

			for (var i of $(this).get()) {
				let tem_list = i.getElementsByTagName("td")

				if (tem_list[1].innerHTML in tem_obj) {
					tem_obj[tem_list[1].innerHTML] = tem_obj[tem_list[1].innerHTML] + Number(tem_list[3].innerHTML)
				} else {
					// console.log(3, tem_list[1], tem_list[3]);
					tem_obj[tem_list[1].innerHTML] = Number(tem_list[3].innerHTML)
				}
			}

		})
		let today_plan_tbody = $("#today_plan_tbody")

		// 获取已经存在的dom元素，删除掉
		let today_plan_tr = $(".today_plan_tr")
		today_plan_tr.remove()

		// 奖两个对象组合在一起
		for (var i of res_obj.today_plan_data) {
			i["actual_number"] = tem_obj[i["staff_group"]]
			i["proportion"] = (i.actual_number / i.plan_number) * 100
		}

		// 排序
		res_obj.today_plan_data.sort(compare('proportion'))

		// 生成dom元素
		var count = res_obj.today_plan_data.length
		for (var i of res_obj.today_plan_data) {



			today_plan_tbody.after(`<tr class='today_plan_tr'><td><span>${count}</span></td><td>${i.staff_group}</td><td>${i.plan_number}<br></td><td>${i.actual_number}<br></td><td>${i.proportion.toFixed(2)}%<br></td></tr>`);
			count = count - 1

		}
	})
};



export { get_today_plan_data };


