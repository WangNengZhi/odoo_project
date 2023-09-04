odoo.define('fsn_base/static/src/js/file_upload.js', function (require) {
    "use strict";
    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    const core = require('web.core');
    const QWeb = core.qweb;

    const FsnFileUpload = AbstractField.extend({
        supportedFieldTypes: ['char'],

        init: function (parent, fieldName, record, widgetOptions) {
            console.log(1);
            return this._super.apply(this, arguments);
        },

        willStart: function () {
            console.log(2);
            return this._super.apply(this, arguments);
        },

        start: function () {
            console.log(3);
            return this._super.apply(this, arguments);
        },

        template: 'fsn_base_file_upload_template',

        events: {
            'change #portrait_file': 'on_file_change',
        },
        // 选择文件后触发
        on_file_change: function (e) {
            
            var self = this;
            if (self.res_id) {
                var files = e.target.files || e.dataTransfer.files;

                self.http_up_file(files[0])
            }
        },

        // 上传附件
        http_up_file: function (file) {

            let formData = new FormData();

            formData.append("file", file);

            formData.append("name","aaaaaa")


            $.ajax({
                url: 'http://192.168.20.149:5000/file_server/uploader',
                // url: "/file_server/uploader,
                type: "POST",
                data: formData,
                async: false,
        		contentType : false,
				processData : false,
                success: (res) => {
                    console.log(res);
                },


            })
            // this._setValue("hioihgojh")

        },


    });

    fieldRegistry.add('fsn_file_upload', FsnFileUpload);

    return FsnFileUpload;
    
})
