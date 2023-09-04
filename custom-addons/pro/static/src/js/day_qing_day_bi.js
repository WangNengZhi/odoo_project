odoo.define('/pro/static/src/js/day_qing_day_bi.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "day_qing_day_bi"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var core = require('web.core');
    var qweb = core.qweb;

    ListController.include({

        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                let day_qing_day_bi_button = $("<button id='middle_check_return_ids' type='button' class='btn btn-primary'>日清日毕刷新</button>").click(this.proxy("day_qing_day_bi_refresh"))
                this.check_is_super_user(day_qing_day_bi_button)
            }

            return $buttons;
        },

        // 检测是否是超级用户
        check_is_super_user (day_qing_day_bi_button) {

            if (session.is_admin) {
                this.$buttons.append(day_qing_day_bi_button);
            } else {

                rpc.query({
                    route: "/inherit_mail/daily_newspaper_refresh",
                }).then((res) => {

                    if (res.is_show) {
                        this.$buttons.append(day_qing_day_bi_button);
                    }
                })

            }

        },
        day_qing_day_bi_refresh: function () {

            this.do_action({
                name: "刷新日清日毕",
                res_model: "day_qing_day_bi_wizard",
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                target: 'new',
            });

        },



    });
});