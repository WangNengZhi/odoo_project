odoo.define('/hr_pay/static/src/js/update_punch_record_stats.js', function (require) {
    "use strict";

    var ListController = require('web.ListController');  // 引入列表控制器，用来修改 tree 视图
    var show_button_import = "punch_record_with_missing_time";  // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');

    ListController.include({

        // 自定义按钮方法
        renderButtons: function($node) {
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个 HTML 按钮，点击时出发 test 函数
                var button = $("<button id='update_punch_record_stats' type='button' class='btn btn-primary'>更新</button>").click(
                                this.proxy("update_punch_record_stats"));
                this.$buttons.append(button);    // 添加到已有按钮的后面
            }
            return $buttons;
        },

        update_punch_record_stats: function() {
            // console.log("Here!");

            rpc.query({  // POST
                route: "/update_punch_record_stats"
            }).then(function(resp) {
                resp = JSON.parse(resp);
                if (resp.status == 0) {
                    // alert("刷新成功！点击后刷新页面！");
                    location.reload();
                } else {
                    alert("刷新出错！");
                }
            });
        }
    
    });
});