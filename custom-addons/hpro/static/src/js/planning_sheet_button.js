odoo.define('hpro/static/src/js/planning_sheet_button.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "work.work"; // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');


    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_02 = $("<button id='but_02' type='button' class='btn btn-primary'>同步GST数据</button>").click(this.proxy("sync_gst_data"))

                this.$buttons.append(button_02);    // 添加到已有按钮的后面

                // 定义一个html按钮，点击时出发test函数
                var button_01 = $("<button id='but' type='button' class='btn btn-primary'>获取工序</button>").click(this.proxy("get_planning_sheet"))

                this.$buttons.append(button_01);    // 添加到已有按钮的后面

            }

            return $buttons;
        },
        
        get_planning_sheet: function () {

            rpc.query({
                route: "/planning_sheet",
                params: {
                    "start_time": 666,
                    "end_time": 777,
                },
            }).then(function (data) {
                if (data) {
                    // console.log(data);
                    alert("同步成功！点击刷新页面。")
                    location.reload();
                }
            })

        },

        sync_gst_data: function () {

            rpc.query({
                route: "/sync_gst_data",
                params: {
                    "start_time": 666,
                    "end_time": 777,
                },
            }).then(function (data) {
                if (data) {
                    console.log(data);
                    // alert("同步成功！点击刷新页面。")
                    // location.reload();
                }
            })
        }

    });
});