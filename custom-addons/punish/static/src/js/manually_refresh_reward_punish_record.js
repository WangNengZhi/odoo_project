odoo.define('/punish/static/src/js/manually_refresh_reward_punish_record.js', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var ListController = require('web.ListController');
    var show_button_import = "reward_punish_record";
    var rpc = require('web.rpc');
    var session = require('web.session');

    ListController.include({

        renderButtons: function($node) {
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;

            if (tree_model == show_button_import) {
                var lack_card_generate_ticket = $("<button id='manually_refresh_reward_punish_record' type='button' class='btn btn-primary'>缺卡生成罚单</button>").click(
                                this.proxy("lack_card_generate_ticket"));
                this.$buttons.append(lack_card_generate_ticket);

                this.$buttons.append("&nbsp;")

                var check_attendance = $("<button id='checkout_attendance_punish_record' type='button' class='btn btn-primary'>迟到早退生成罚单</button>").click(
                                this.proxy("check_attendance"));
                this.$buttons.append(check_attendance);
            }
            return $buttons;
        },
        lack_card_generate_ticket: function () {

            this.do_action({
                name: "缺卡生成罚单",
                res_model: "lack_card_generate_ticket_wizard",
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                target: 'new',
            });


            // var affirm = function () {

            //     let generate_month = $("#generate_month").val();

            //     if (generate_month) {

            //         rpc.query({
            //             model: 'reward_punish_record',
            //             method: 'monthly_number_one_auto_rpr',
            //             args: [[]],
            //             kwargs: {
            //                 "generate_month": generate_month,
            //             },
            //         }).then(function (data) {
            //             if (data) {

            //                 alert("生成完成！点击后刷新页面！")
            //                 location.reload();
            //             }
            //         })

            //     } else {
            //         alert("请录入合法月份！");
            //     }



            //     dialog.close();
            // };


            // let input_text = "<div><h2>请确认自定义日历已经设置完成，否则生成数据将会发生错误！</h2></div><div>生成月份:<input id='generate_month' type='month' name='生成月份'/></div>";

            // var dialog = new Dialog(this, {
            //     title: '缺卡生成罚单',
            //     size: 'small', // 'medium', 'large'
            //     $content: input_text,
            //     buttons: [{
            //         text: '确认',
            //         classes: 'btn-primary',
            //         close: false,
            //         click: affirm
            //     },
            //     {
            //         text: '取消',
            //         close: true
            //     }]
            // }).open();
        },

        check_attendance: function () {
          this.do_action({
              name: "迟到早退生产罚单",
              res_model: "lock_grade_check_attendance",
              type: 'ir.actions.act_window',
              views: [[false, 'form']],
              target: 'new',
          })
        },




        // 检测是否是超级用户
        check_is_super_user (manually_refresh_reward_punish_record) {
            if (session.is_admin) {
                this.$buttons.append(manually_refresh_reward_punish_record);
            } else {

                rpc.query({
                    route: "/fsn_base/check_is_super_user",
                }).then((res) => {

                    if (res.is_show) {
                        this.$buttons.append(manually_refresh_reward_punish_record);
                    }
                })

            }

        },

        manually_refresh_reward_punish_record: function() {

            var affirm = function () {

                let generate_date = $("#generate_date").val();

                if (generate_date) {

                    rpc.query({
                        model: 'reward_punish_record',
                        method: 'performed_manually',
                        args: [[]],
                        kwargs: {
                            "generate_date": generate_date,
                        },
                    }).then(function (data) {
                        console.log(data);
                        if (data) {

                            alert("同步成功！点击后刷新页面！")
                            location.reload();
                        }
                    })

                } else {
                    alert("请录入合法的开始月份和结束月份！");
                }



                dialog.close();
            };

            let input_text = "<div>生成日期:<input id='generate_date' type='date' name='生成日期'/></div>";

            var dialog = new Dialog(this, {
                title: '设置日期',
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
