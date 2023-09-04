
odoo.define('fsn_bom/static/description/src/js/material_summary_sheet.js', function (require) {
    "use strict";
    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图
    var show_button_import = "material_summary_sheet"; // 指定那个模型添加：想要自定义内容的模型
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
                var material_summary_sheet_button = $("<span>&#160;&#160;&#160;&#160;&#160;&#160;&#160;</span><button id='but' type='button' class='btn btn-info'>物料汇总刷新</button>").click(this.proxy("refresh_material_summary_sheet"))
                this.$buttons.append(material_summary_sheet_button);    // 添加到已有按钮的后面

            }


            return $buttons;
        },


        refresh_material_summary_sheet: function () {

            var affirm = function () {

                this._rpc({
                    model: "material_summary_sheet",
                    method: 'refresh_material_summary_sheet',
                    args: [[]],
                }).then((res) => {
                    if (res) {
                        alert("同步成功！点击后刷新页面！");
                        location.reload();
                    }
                })

            };

            let input_text = "<span>确定要刷新吗</span>"

            var dialog = new Dialog(this, {
                title: '确定要刷新吗',
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