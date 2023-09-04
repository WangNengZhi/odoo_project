// js模板名称，可随便写
odoo.define('js_wdc', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');


    var SuspensionSystemIndex = AbstractAction.extend({
        // Qweb模板名称
        template: 'qweb_suspension_system_index',
        events: {
            'click #wdc': '_onSubmitClick',
        },
    
        _onSubmitClick: function () {
            alert("测试弹出")
        },

    });


    // 客户端动作id：client_action_id
    core.action_registry.add('suspension_system_index', SuspensionSystemIndex);
    
    return SuspensionSystemIndex;
    
});