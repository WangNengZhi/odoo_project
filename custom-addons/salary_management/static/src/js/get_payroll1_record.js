odoo.define('salary_management.get_payroll1_record', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "payroll1"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var session = require('web.session');


    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var button_payroll1 = $("<button id='but' type='button' class='btn btn-info'>薪资人员名单刷新</button>").click(this.proxy("get_payroll1_record"))
                this.$buttons.append(button_payroll1);    // 添加到已有按钮的后面

                var payroll_switch = $("<button id='payroll_switch' type='button'  class='btn btn-warning'>修改可编辑状态</button>").click(this.proxy("payroll_switch"))
                this.check_is_super_user(payroll_switch)
 
            }
            return $buttons;
        },

        // 检测是否是超级用户
        check_is_super_user: function (payroll1_restriction_switch) {
            if (session.is_admin) {
                this.$buttons.append(payroll1_restriction_switch);
            } else {

                rpc.query({
                    route: "/inherit_mail/daily_newspaper_refresh",
                }).then((res) => {

                    if (res.is_show) {
                        this.$buttons.append(payroll1_restriction_switch);
                    }
                })

            }

        },


        payroll_switch: function () {
            this.do_action({
                name: "修改可编辑状态",
                type: 'ir.actions.act_window',
                res_model: 'salary_lock_setting',
                views: [[false, 'list']],
                target: 'new',
                context: {
                    create: false,
                    edit: false,
                    delete: false,
                    import:false,
                    export:false,
                }
            });
        },


        get_payroll1_record: function () {

            var affirm = function () {


                let start_time = $("#start_time").val()
                let end_time = $("#end_time").val()

                if (start_time) {
                    console.log("成功");


                    rpc.query({
                        route: "/get_payroll1_record",
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


    });
});