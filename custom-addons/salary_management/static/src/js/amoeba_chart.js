// js模板名称，可随便写
odoo.define('salary_management/static/src/js/amoeba_chart.js', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');



    var CustomPageDemo = AbstractAction.extend({
        // Qweb模板名称
        template: 'amoeba_chart',
        events: {

        },

        start: function () {

        },
    


    });


    // 客户端动作id：client_action_id
    core.action_registry.add('amoeba_chart', CustomPageDemo);
    
    return CustomPageDemo;
    
});