odoo.define('salary_management/static/src/js/compensation_sublevel.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "compensation_sublevel"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var get_hr_employee_ids_button = $("<span>&#160;&#160;&#160;&#160;&#160;&#160;&#160;</span><button id='get_hr_employee_ids' type='button' class='btn btn-info'>获取员工</button>").click(this.proxy("get_hr_employee_ids"))
                this.$buttons.append(get_hr_employee_ids_button);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        get_hr_employee_ids: function () {

            var affirm = function () {


                let month = $("#month").val()

                if (month) {

                    // rpc.query({
                    //     route: "/salary_refresh",
                    //     params: {
                    //         "start_time": start_time,
                    //         "end_time": end_time,
                    //     },
                    // }).then(function (data) {
                    //     if (data) {
                    //         alert("同步成功！点击后刷新页面！")
                    //         location.reload();
                    //     }
                    // })

                    rpc.query({
                        model: 'compensation_sublevel',
                        method: 'generate_records',
                        args: [[]],
                        kwargs: {
                            "year_month": month,
                        },
                    }).then(function (data) {
                        if (data) {
                            alert("同步成功！点击后刷新页面！")
                            location.reload();
                        }
                    })


                    dialog.close();
                } else {
                    alert("请填写开始时间和结束时间！")
                }
            };

            let input_text = "<span>月份:<input id='month' type='month' name='月份'/></span></span>"

            var dialog = new Dialog(this, {
                title: '设置时间范围',
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