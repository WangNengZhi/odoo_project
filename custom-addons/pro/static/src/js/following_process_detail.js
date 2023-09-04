odoo.define('/pro/static/src/js/following_process_detail.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "following_process_detail"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog');

    ListController.include({
        
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                let button_01 = $("<button id='middle_check_return_ids' type='button' class='btn btn-primary'>中查退修明细</button>").click(this.proxy("middle_check_return_ids"))
                let button_02 = $("<button id='always_check_return_ids' type='button' class='btn btn-primary'>总检退修明细</button>").click(this.proxy("always_check_return_ids"))
                this.$buttons.append(button_01, button_02);    // 添加到已有按钮的后面
            }

            return $buttons;
        },


        middle_check_return_ids: function () {

            var affirm = function () {

                let start_time = $("#start_time").val()
                let end_time = $("#end_time").val()

                if (start_time && end_time) {
                    console.log("成功");

                    this.do_action({
                        name: "中查退修明细",
                        type: 'ir.actions.act_window',
                        res_model: 'middle_check_return_line',
                        views: [[false, 'list']],
                        target: 'new',
                        domain: [['dDate', '>=', start_time], ['dDate', '<=', end_time]],
                        context: {
                            create: false,
                            edit: false,
                            delete: false,
                        }
                    });

                    dialog.close();
                } else {
                    alert("请正确填写时间信息！")
                }
            };


            let input_text = "<div>开始时间:<input id='start_time' type='date' name='开始时间'/></div><div>结束时间:<input id='end_time' type='date' name='结束时间'/></div>"

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

        always_check_return_ids: function () {


            var affirm = function () {

                let start_time = $("#start_time").val()
                let end_time = $("#end_time").val()

                if (start_time && end_time) {
                    console.log("成功");

                    this.do_action({
                        name: "总检退修明细",
                        type: 'ir.actions.act_window',
                        res_model: 'always_check_return_line',
                        views: [[false, 'list']],
                        target: 'new',
                        domain: [['dDate', '>=', start_time], ['dDate', '<=', end_time]],
                        context: {
                            create: false,
                            edit: false,
                            delete: false,
                        }
                    });

                    dialog.close();
                } else {
                    alert("请正确填写时间信息！")
                }
            };



            let input_text = "<div>开始时间:<input id='start_time' type='date' name='开始时间'/></div><div>结束时间:<input id='end_time' type='date' name='结束时间'/></div>"

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