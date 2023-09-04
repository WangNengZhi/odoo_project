odoo.define('wdc_js', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var show_button_import = "on.work";

    var core = require('web.core');
    var _t = core._t;

    ListController.include({
        renderButtons: function ($node) {
            var self = this;
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;

            if (tree_model == show_button_import) {
                var button_01 = $("<button id='but' type='button' class='btn btn-primary'>录入完成</button>").click(this.proxy("send_messages"));

                var upload_input = $("<input type='file' id='file' name='file' style='display:none;'/>");

                var formal_import_button = $("<label for='file' class='btn btn-primary'>正式工导入</label>");
                formal_import_button.on('click', function (event) {
                    event.preventDefault();
                    upload_input.click();
                });

                var temporary_import_button = $("<label for='file' class='btn btn-primary'>临时工导入</label>");
                temporary_import_button.on('click', function (event) {
                    event.preventDefault();
                    upload_input.click();
                });

                // 绑定点击事件时取消按钮的active状态
                formal_import_button.removeClass('active');
                temporary_import_button.removeClass('active');

                // 点击时添加active状态
                formal_import_button.on('click', function(){
                  formal_import_button.addClass('active');
                  temporary_import_button.removeClass('active');
                });

                temporary_import_button.on('click', function(){
                  temporary_import_button.addClass('active');
                  formal_import_button.removeClass('active');
                });

                upload_input.on('change', function (event){
                    var file = event.target.files[0];
                    if (file) {
                        if (temporary_import_button.hasClass('active')) {
                          self.uploadTemporaryFile(file);
                        } else {
                          self.uploadFormalFile(file);
                        }
                    }
                });

                var $button_group = $("<div class='btn-group' style='display: flex;'></div>");
                this.$buttons.append(button_01);
                this.$buttons.append(upload_input);
                $button_group.append(formal_import_button);
                $button_group.append(temporary_import_button);
                this.$buttons.append($button_group);
            }

            return $buttons;
        },

        send_messages: function () {
            let is_send = confirm("确认完成录入吗？");
            if (is_send) {
                this._rpc({
                    model: 'mail.channel',
                    method: 'send_messagrs',
                    args: [[]],
                    kwargs: {
                        "user_id": this.initialState.context.uid,
                    },
                });
            }
        },

        uploadFormalFile: function (file) {
            var self = this;
            var reader = new FileReader();
            reader.onload = function (event) {
                var data = event.target.result;
                self._rpc({
                    model: 'on.work',
                    method: 'process_formal_excel_data',
                    args: [data],
                }).then(function (result) {
                    // Success logic for formal import
                    self.reload();
                    self.do_notify('上传成功', '正式工导入成功！');
                }).catch(function (error) {
                    // Error handling logic
                });
            };
            reader.readAsDataURL(file);
        },

        uploadTemporaryFile: function (file) {
            var self = this;
            var reader = new FileReader();
            reader.onload = function (event) {
                var data = event.target.result;
                self._rpc({
                    model: 'on.work',
                    method: 'process_temporary_excel_data',
                    args: [data],
                }).then(function (result) {
                    // Success logic for temporary import
                    self.reload();
                    self.do_notify('上传成功', '临时工导入成功！');
                }).catch(function (error) {
                    // Error handling logic
                });
            };
            reader.readAsDataURL(file);
        },
    });
});
