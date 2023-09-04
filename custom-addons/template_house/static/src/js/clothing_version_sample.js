odoo.define('template_house/static/src/js/clothing_version_sample.js', function (require) {
    "use strict";


    var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');
    var view_registry = require('web.view_registry');
    var session = require('web.session');

    var SpsServiceFormRenderer = FormRenderer.extend({
        events: _.extend({}, FormRenderer.prototype.events, {
            'click .add_attachment': 'local_sync_oss',
        }),

        init: function () {
            this._super.apply(this, arguments);
        },
        // 这里可以在页面打开时提前获取一些需要的数据，和执行一些函数
        start: function () {

            this._super.apply(this, arguments);

        },

        local_sync_oss: function () {
            console.log("点击按钮执行的函数");
            let input_obj = document.getElementById("btn_file")
            console.log(input_obj);
            console.log(input_obj.value);
        },




    })



    var SpsServiceFormView = FormView.extend({
        jsLibs: [],
    
        config: _.extend({}, FormView.prototype.config, {
            Renderer: SpsServiceFormRenderer,
        }),
    });


    view_registry.add('local_sync_oss', SpsServiceFormView);


    return {
        Renderer: SpsServiceFormRenderer,
    };

})





