odoo.define('custom-addons/salary_management/static/src/js/salary_sheet_check.js.month_import_js', function (require) {
    "use strict";

    var ListController = require('web.ListController'); // 引入列表控制器，用来修改tree视图

    ListController.include({

        // 自定义元素方法
        renderElement: function () {

            var $div = this._super.apply(this, arguments);
            var tree_model = this.modelName;   // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == 'salary'||tree_model == 'fsn_salary_sheet') {

                this._rpc({
                    model: 'fsn_true_salary_sheet',
                    method: 'is_notice',
                    args: [[]],
                }).then((res) => {

                    if (res) {
                        this.do_warn("消息通知！", '工资条中有异常信息！', true, 'bg-warning');
                    }
                });


            }
        },
    });

});