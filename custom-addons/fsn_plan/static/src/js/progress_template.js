odoo.define('fsn_plan.GanttRow', function (require) {
    "use strict";

    const HrGanttView = require('web_gantt.GanttView');
    const viewRegistry = require('web.view_registry');
    const HrGanttRow = require('web_gantt.GanttRow');
    const GanttRenderer = require('web_gantt.GanttRenderer');


    const Fsn_ganttRow = HrGanttRow.extend({

        init: function (parent, pillsInfo, viewInfo, options) {
            this._super.apply(this, arguments);

            // 页面加载完成后执行
            $(function(){
                setTimeout(function(){

                    // 循环获取数据
                    for (let pill of pillsInfo.pills) {
                        // 获取dom元素并赋值
                        let div_dom = document.querySelector(`[data-id="${pill.id}"]`)
                        if (div_dom) {

                            let p_dom = div_dom.getElementsByTagName('p')

                            p_dom[0].innerText = `${pill.style_number[1]}——${pill.plan_number}——${pill.actual_number}——${pill.progress_bar.toFixed(2)}%`
                            // 把字体设置为黑色
                            p_dom[0].style.color="#000000";
                            
                            if (pill.plan_number == 0 && pill.actual_number != 0) {
                                // 计划数为0时,设置为紫色
                                div_dom.style.background="#800080";
                            } else {
                                // 根据百分比设置背景颜色
                                if (pill.progress_bar > 59 && pill.progress_bar < 80) {
                                    div_dom.style.background="#FFFF00";
                                } else if (pill.progress_bar < 60) {
                                    div_dom.style.background="#FF0000";
                                }
                            }




                            
                        } else {
                            console.log("报错");
                        }

                    }

            　　},100);　　　　//延时0.1秒

            });


        },


    });

    const FsnGanttRenderer = GanttRenderer.extend({
        config: Object.assign({}, GanttRenderer.prototype.config, {
            GanttRow: Fsn_ganttRow
        }),
    });

    const FsnGanttView = HrGanttView.extend({
        config: Object.assign({}, HrGanttView.prototype.config, {
            Renderer: FsnGanttRenderer,
        }),
    });

    viewRegistry.add('fsn_gantt', FsnGanttView);

    return FsnGanttView;

});