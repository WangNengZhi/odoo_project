odoo.define('fsn_plan/static/src/js/target_output_value.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "target_output_value"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog'); //引入odoo的dialog弹窗对象
    var rpc = require('web.rpc');
    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var refresh_target_output_value_button = $("<button id='refresh_target_output_value_button' type='button' class='btn btn-primary'>刷新数据</button>").click(this.proxy("refresh_target_output_value"))

                this.$buttons.append(refresh_target_output_value_button);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        refresh_target_output_value: function () {


            var affirm = function () {


                let refresh_target_output_value_month = $("#refresh_target_output_value_month").val()


                if (refresh_target_output_value_month) {
                    console.log("成功");

                    rpc.query({
                        model: 'target_output_value',
                        method: 'refresh_target_output_value',
                        args: [[]]
                    }).then(function (res) {

                        if (res) {
                            alert("同步成功！点击后刷新页面！");
                            
                            location.reload();
                        }

                    })


                    dialog.close();
                } else {
                    alert("请填写刷新月份！")
                }
            };

            let input_text = "<div>开始时间:<input id='refresh_target_output_value_month' type='month' name='月份'/></div>"

            var dialog = new Dialog(this, {
                title: '选择刷新月份',
                // size: 'medium',
                size: 'small',
                // size: 'large',
                $content: input_text,
                buttons: [{
                    text: '确认',
                    classes: 'btn-primary',
                    close: false,
                    click: affirm
                },
                {
                    text: '取消',
                    close: true
                }]
            }).open();


            },




    });
});