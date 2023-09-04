odoo.define('hr_pay.shuaxin_js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "attendance.days.statistics.table"; // 指定那个模型添加：想要自定义内容的模型

    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_01 = $("<button id='but' type='button' class='btn btn-primary'>刷新</button>").click(this.proxy("test"))
                this.$buttons.append(button_01);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        test: function () {
            this._rpc({
                model: 'attendance.days.statistics.table',
                method: 'test1',
                args: [[]]
                })

        }

    });
});