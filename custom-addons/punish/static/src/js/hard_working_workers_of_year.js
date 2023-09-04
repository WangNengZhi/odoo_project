odoo.define('/punish/static/src/js/hard_working_workers_of_year.js', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');  //引入 Odoo 的 dialog 弹窗对象
    var ListController = require('web.ListController');  // 引入列表控制器，用来修改 tree 视图
    var show_button_import = "hard_working_workers_of_year";  // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');

    ListController.include({

        // 自定义按钮方法
        renderButtons: function($node) {
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个 HTML 按钮，点击时出发 test 函数
                var button = $("<button id='hard_working_workers_of_year' type='button' class='btn btn-primary'>创建</button>").click(
                                this.proxy("hard_working_workers_of_year"));
                this.$buttons.append(button);    // 添加到已有按钮的后面
            }
            return $buttons;
        },

        hard_working_workers_of_year: function() {
            // console.log("Here!");

            var affirm = function () {
                // let start_month = $("#start_month").val();
                let end_month = $("#end_month").val();

                if (! (end_month)) {
                    alert("请录入合法的开始月份和结束月份！");
                    return;
                }

                // console.log(start_month, end_month);

                rpc.query({  // POST
                    route: "/hard_working_workers_of_year",
                    params: {
                        // "start_month": start_month,
                        "end_month": end_month
                    }
                }).then(function (resp) {

                    resp = JSON.parse(resp);
                    if (resp.status == 0) {
                        // alert("刷新成功！点击后刷新页面！");
                        location.reload();
                    } else {
                        alert("刷新出错！");
                    }
                })

                // alert("=========================")
                dialog.close();
            };

            // let input_text = "<div>开始月份:<input id='start_month' type='month' name='开始月份'/></div>" + "<div>结束月份:<input id='end_month' type='month' name='结束月份'/></div>";
            let input_text = "<div>计算月份:<input id='end_month' type='month' name='计算月份'/></div>";

            var dialog = new Dialog(this, {
                title: '设置时间范围',
                size: 'small', // 'medium', 'large'
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