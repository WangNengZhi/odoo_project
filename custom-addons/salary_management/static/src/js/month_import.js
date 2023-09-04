odoo.define('salary_management.month_import_js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "salary"; // 指定那个模型添加：想要自定义内容的模型
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
                var button_01 = $("<span>&#160;&#160;&#160;&#160;&#160;&#160;&#160;</span><button id='but' type='button' class='btn btn-info'>薪资人员名单刷新</button>").click(this.proxy("refresh_emp_list"))
                this.$buttons.append(button_01);    // 添加到已有按钮的后面

            }


            return $buttons;
        },


        refresh_emp_list: function () {

            var affirm = function () {


                let start_time = $("#start_time").val()
                let end_time = $("#end_time").val()

                if (start_time) {
                    console.log("成功");


                    rpc.query({
                        route: "/salary_refresh",
                        params: {
                            "start_time": start_time,
                            "end_time": end_time,
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

            let input_text = "<span>年:<input id='start_time' type='text' name='年'/></span><span>月:<input id='end_time' type='text' name='月'/></span>"

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


        },



//        ===================








    });
});