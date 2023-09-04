odoo.define('/hr_pay/static/src/js/sync_punch_card_record.js', function (require) {
    "use strict";
    var Dialog = require('web.Dialog'); //引入odoo的dialog弹窗对象
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "punch.in.record"; // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');

    ListController.include({


        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_01 = $("<button id='sync_punch_card_record_but' type='button' class='btn btn-primary'>同步打卡记录</button>").click(this.proxy("sync_punch_card_record"))

                this.$buttons.append(button_01);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        sync_punch_card_record: function () {


            document.getElementById("sync_punch_card_record_but").setAttribute("disabled", true);


            rpc.query({
                route: "/sync_attendance_record",
            }).then(function (data) {
                if (data) {
                    alert("同步成功！点击后刷新页面！")
                    location.reload();
                }
            })



        },


    });
});