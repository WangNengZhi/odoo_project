odoo.define('/suspension_system/static/js/suspension_system_summary_button.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "suspension_system_summary"; // 指定那个模型添加：想要自定义内容的模型

    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_01 = $("<button id='suspension_system_summary_button' type='button' class='btn btn-primary'>同步吊挂数据</button>").click(this.proxy("sync_suspension_system_summary_data"))

                this.$buttons.append(button_01);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        sync_suspension_system_summary_data: function () {

            let is_send = confirm("确认同步吊挂数据吗？")

            if (is_send){

                this._rpc({
                    model: 'suspension_system_summary',
                    method: 'sync_data',
                    args: [[]],
                    // kwargs: {
                    //     "user_id": this.initialState.context.uid,
                    // },
                }).then(res => {
                    // 如果同步成功，则刷新页面
                    if (res) {
                        location.reload();
                    }
                })

            }

        },

    });
});