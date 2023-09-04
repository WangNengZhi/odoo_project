import { get_suspension_system_summary, refresh_rate } from "/fsn_data_screen/static/src/js/window_01.js";
import { get_month_output_value, set_workshop_dashboard, set_cutting_bed_dashboard, set_after_road_dashboard, set_warehouse_dashboard} from "/fsn_data_screen/static/src/js/window_02.js";

import { get_today_plan_data } from "/fsn_data_screen/static/src/js/window_04.js";

function dateFormat(fmt, date) {
    let ret;
    const opt = {
        "Y+": date.getFullYear().toString(),        // 年
        "m+": (date.getMonth() + 1).toString(),     // 月
        "d+": date.getDate().toString(),            // 日
        "H+": date.getHours().toString(),           // 时
        "M+": date.getMinutes().toString(),         // 分
        "S+": date.getSeconds().toString()          // 秒
        // 有其他格式化字符需求可以继续添加，必须转化成字符串
    };
    for (let k in opt) {
        ret = new RegExp("(" + k + ")").exec(fmt);
        if (ret) {
            fmt = fmt.replace(ret[1], (ret[1].length == 1) ? (opt[k]) : (opt[k].padStart(ret[1].length, "0")))
        };
    };
    return fmt;
}

function loadtm(){
        let date = new Date()
        date = dateFormat("YYYY-mm-dd HH:MM:SS", date)
        $(".tmtext span").html(date);
        // setTimeout 在执行时,是在载入后延迟指定时间后,去执行一次表达式,仅执行一次


}
function p(s) {
    return s < 10 ? '0' + s: s;
}
window.setInterval( loadtm, 1000);



// 数据刷新函数
function refresh_function() {

    // window_01
    get_suspension_system_summary()


    // 获取车间产值window_02
    set_workshop_dashboard()
    // 裁床产值window_02
    set_cutting_bed_dashboard()
    // 后道产值window_02
    set_after_road_dashboard()
    // 仓库进度
    set_warehouse_dashboard()

    // 获取当月以及当天产值window_02
    get_month_output_value()


    // 获取每日生产计划完成情况window_04
    get_today_plan_data()

}

window.setInterval( refresh_function, refresh_rate);



