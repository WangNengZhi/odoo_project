// js模板名称，可随便写
odoo.define('salary_management/static/src/js/workshop_pie_chart.js', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    // const { echarts } = require('salary_management/static/src/lib/echarts.min.js');



    var CustomPageDemo = AbstractAction.extend({
        // Qweb模板名称
        template: 'workshop_pie_chart',
        events: {

        },

        start: function () {

            // console.log(echarts);

        },
    


    });


    // 客户端动作id：client_action_id
    core.action_registry.add('workshop_pie_chart', CustomPageDemo);
    
    return CustomPageDemo;
    
});