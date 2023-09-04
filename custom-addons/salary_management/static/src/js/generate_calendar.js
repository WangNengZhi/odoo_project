odoo.define('salary_management/static/src/js/generate_calendar.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "custom.calendar"; // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');

    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_01 = $("<button id='but' type='button' class='btn btn-primary'>一键生成日历</button>").click(this.proxy("generate_calendar"))
                this.$buttons.append(button_01);    // 添加到已有按钮的后面
            }

            return $buttons;
        },
        
        // 一键生成日历
        generate_calendar: function () {

            var affirm = function () {

                let month = $("#calendar_month").val()

                if (month) {
                    console.log("成功");
                    console.log(month);


                    rpc.query({
                        route: "/generate_calendar",
                        params: {
                            "month": month,
                        },
                    }).then(function (data) {
                        if (data) {
                            alert("同步成功！点击后刷新页面！")
                            location.reload();
                        }
                    })



                    dialog.close();
                } else {
                    alert("请填写月份信息！")
                }
            };

            let input_text = "<span><input id='calendar_month' type='month' name='月份'/>"

            var dialog = new Dialog(this, {
                title: '请选择月份!',
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

        }
    });
});