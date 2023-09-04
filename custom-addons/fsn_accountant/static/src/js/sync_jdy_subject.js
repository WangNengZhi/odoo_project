odoo.define('/fsn_accountant/static/src/js/sync_jdy_subject.js', function (require) {
    "use strict";
    

    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "jdy_subject"; // 指定那个模型添加：想要自定义内容的模型
    var Dialog = require('web.Dialog'); //引入odoo的dialog弹窗对象
    var rpc = require('web.rpc');


    ListController.include({

        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                let day_qing_day_bi_button = $("<button id='middle_check_return_ids' type='button' class='btn btn-primary'>会计科目更新同步</button>").click(this.proxy("sync_jdy_subject"))

                this.$buttons.append(day_qing_day_bi_button);
            }

            return $buttons;
        },


        sync_jdy_subject: function () {


            var affirm = function () {

                rpc.query({
                    model: 'jdy_subject',
                    method: 'sync_jdy_subject',
                    args: [[]],
                }).then(function (data) {
                    console.log(data);
                    if (data) {

                        alert("会计科目更新同步成功！点击后刷新页面！")
                        location.reload();
                    }
                })


                dialog.close();
 
            };

            let input_text = "<div>会计科目更新同步</div>";

            var dialog = new Dialog(this, {
                title: '会计科目更新同步',
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


})