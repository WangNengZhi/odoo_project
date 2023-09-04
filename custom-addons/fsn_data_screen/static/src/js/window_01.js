import { get_today_dg_data } from "/fsn_data_screen/static/src/js/get_suspension_system_data.js";

// 排序
function compare(property){
    return function(a,b){
        var value1 = a[property];
        var value2 = b[property];
        return value1 - value2;
    }
}

// 获取组产量数据
function get_suspension_system_summary() {

    // 获取吊挂数据
    let data_list = get_today_dg_data("车间")


    let group_output_table1 = $("#group_output")
    let group_output_table_first_line = group_output_table1.find(".tb_title")

    // 按产量排序
    data_list.sort(compare('nNumber'))

    // 删除之前的行
    let group_output_table = $("#group_output")
    let tem_tr = group_output_table.find(".tem_data")
    tem_tr.remove();


    for (var data of data_list) {
        $.ajax({
            url: "/get_mono_price",
            method: "get",
            // dataType: "json",
            data: {
                "mono": data.MONo
            },
            async: false
        }).success(function (res) {

            let res_obj = $.parseJSON(res);
            data["output_value"] = (data.nNumber * res_obj.price).toFixed(2)

            group_output_table_first_line.after(`<tr class="tem_data"><td>${data.dDate}</td><td>${data.gGroup}</td><td>${data.MONo}</td>
            <td>${data.nNumber}</td><td class="output_value">${data.output_value}</td></tr>`)

        })


    }


}

get_suspension_system_summary()

function get_refresh_rate(view_name) {

    $.ajax({
        url: "/get_refresh_rate",
        method: "get",
        data: {
            "view_name": view_name
        },
        async: false
    }).success(function (res) {
        let res_obj = $.parseJSON(res);
        refresh_rate = res_obj.refresh_frequency
    })

}

var refresh_rate = 1000000

get_refresh_rate("组产量")

// window.setInterval(get_suspension_system_summary, refresh_rate);
export { get_suspension_system_summary, refresh_rate };




