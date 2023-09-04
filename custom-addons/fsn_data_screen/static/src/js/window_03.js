// 获取风丝袅吊挂系统数据
function get_fsn_dg_sys_data() {
    $.ajax({
        url: "/get_fsn_sys_dg_detail",
        method: "get",
        async: false
    }).success(function (res) {

        // 删除子元素
        $("#window_03_ul").empty()

        let res_obj = $.parseJSON(res);

        data_list = res_obj.data

        text = ""
        for (var record of data_list) {

            text = text + `<li><p><span>&nbsp;&nbsp;&nbsp;${record.group}</span><span>${record.staff_name}</span><span>&nbsp;${record.output}</span><span>${record.workpiece_ratio.toFixed(2)}%</span></p></li>`
        }

        $("#window_03_ul").html(text);

    })
}

get_fsn_dg_sys_data()

$(function(){

    $('.dowebok').liMarquee({
        direction: 'up',
        runshort: false,    //内容不足时不滚动
        scrollamount: 10    //速度
    });

});