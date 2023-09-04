odoo.define('procurement/static/description/src/js/fabric_ingredients_refund.js', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var show_button_import = "fabric_ingredients_refund";
    var core = require('web.core');
    var QWeb = core.qweb;
    var Dialog = require('web.Dialog');

    ListController.include({
        // 自定义按钮方法
        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                // 定义一个html按钮，点击时出发test函数
                var web_create_button = $("<button id='web_create' type='button' class='btn btn-info'>创建</button>").click(this.proxy("web_create"))
                this.$buttons.append(web_create_button);    // 添加到已有按钮的后面
            }


            return $buttons;
        },

        web_create: function () {

            var affirm = function () {

                let material_type = $('#material_type_selection option:selected').val()

                let res_model = ""
                let name = ""

                if (material_type == "面料") {
                    res_model = "plus_material_inventory"
                    name = "面料选择"
                } else {
                    res_model = "warehouse_bom_inventory"
                    name = "物料选择"
                }
                this.do_action({
                    name: name,
                    res_model: res_model,
                    type: 'ir.actions.act_window',
                    views: [[false, 'list']],
                    target: 'new',
                    domain: [['amount', '!=', 0]],
                    context: {
                        "show_button": true,
                    },
                });
                dialog.close();
            };



            let qweb_content = $(QWeb.render('procurement_material_type_selection'));

            var dialog = new Dialog(this, {
                title: '选择物料类型',
                size: 'small',
                $content: qweb_content,
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