odoo.define('GanttRow_punch', function (require) {
    "use strict";

    const HrGanttView = require('web_gantt.GanttView');
    const viewRegistry = require('web.view_registry');
    const HrGanttRow = require('web_gantt.GanttRow');
    const GanttRenderer = require('web_gantt.GanttRenderer');


    const punch_ganttRow = HrGanttRow.extend({

        init: function (parent, pillsInfo, viewInfo, options) {
            this._super.apply(this, arguments);
            $(function(){
                setTimeout(function(){
                    // 循环获取数据
                    for (let pill of pillsInfo.pills) {
                        // 获取dom元素并赋值
                        let div_dom = document.querySelector(`[data-id="${pill.id}"]`)
                        if (pill.check_sign){
                            div_dom.style.backgroundColor  = '#FFFAF0'
                            div_dom.style.color = '	#000000'
                            console.log(pillsInfo.pills)
                            div_dom.getElementsByTagName('p')[0].innerText = pill.check_sign

                        } else{
                            div_dom.style.background = '#FFFAF0'
                            console.log(pillsInfo.pills)
                            div_dom.getElementsByTagName('p')[0].innerText = ''
                        }
                    }
            　　},10);　　　　
            });
        },
    });
    const FsnGanttRenderer = GanttRenderer.extend({
        config: Object.assign({}, GanttRenderer.prototype.config, {
            GanttRow: punch_ganttRow
        }),
    });

    const PunchGanttView = HrGanttView.extend({
        config: Object.assign({}, HrGanttView.prototype.config, {
            Renderer: FsnGanttRenderer,
        }),
    });

    viewRegistry.add('fsn_punch_gantt', PunchGanttView);

    return PunchGanttView;

});