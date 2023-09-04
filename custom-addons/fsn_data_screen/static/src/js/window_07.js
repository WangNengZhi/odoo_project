// 获取萤石token
function get_yingshi_video_url() {


    $.ajax({
        url: "/get_yingshi_video_url/",
        method: "get",
        data: {
            "device_name": "二楼办公室"
        },
        async: false
    }).success(function (res) {

        let res_obj = $.parseJSON(res);
        // console.log(res_obj);
        $("#window_07_01").attr("src", res_obj.video_url);

    })
}

get_yingshi_video_url()