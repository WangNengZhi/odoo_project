// 排序函数
function compare(property){
    return function(a,b){
        var value1 = a[property];
        var value2 = b[property];
        return value1 - value2;
    }
}


// 获取最近日期各组返修率
function get_recently_group_statistical() {

    $.ajax({
        url: "/get_recently_group_statistical/",
        method: "get",
        async: false,
    }).success(function (res) {

        let res_obj = $.parseJSON(res);

		let window_05_date = $("#window_05_date")
        window_05_date.text(res_obj.date)

        let data_list = res_obj.recently_group_statistical
		let group_statistical = $("#group_statistical")

        // 计数
        var count = data_list.length

        for (var i of data_list) {
            group_statistical.after(`<tr><td><span>${count}</span></td><td>${i.group}</td><td>${i.assess_index.toFixed(2)}%<br></td></tr>`)
			count = count - 1
        }

    })
}

get_recently_group_statistical()