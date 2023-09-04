odoo.define('/salary_management/static/src/js/outsourcing_wages_for_work_done.js', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');  //引入 Odoo 的 dialog 弹窗对象
    var ListController = require('web.ListController');  // 引入列表控制器，用来修改 tree 视图
    var show_button_import = "outsourcing_wages";  // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');

    ListController.include({

        // 自定义按钮方法
        renderButtons: function($node) {
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个 HTML 按钮，点击时出发 test 函数
                if (this._title == '外包计时薪酬') {
                    var button = $("<button id='outsourcing_wages_per_work_time' type='button' class='btn btn-primary'>创建</button>").click(
                                    this.proxy("outsourcing_wages_per_work_time_wizard"));
                } else {
                    var button = $("<button id='outsourcing_wages_for_work_done' type='button' class='btn btn-primary'>创建</button>").click(
                                    this.proxy("outsourcing_wages_for_work_done_wizard"));
                }
                this.$buttons.append(button);    // 添加到已有按钮的后面
            }
            return $buttons;
        },

        outsourcing_wages_per_work_time_wizard: function() {

            const context = {"default_contract": "外包(计时)"}

            this.do_action({
                name: "外包员工月工资计算",
                res_model: "outsourcing_wages_wizard",
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            });

        },

        outsourcing_wages_for_work_done_wizard: function() {
            
            const context = {"default_contract": "外包(计件)"}

            this.do_action({
                name: "外包员工月工资计算",
                res_model: "outsourcing_wages_wizard",
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            });

        },

    });
});