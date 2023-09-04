odoo.define('fsn_employee/static/src/js/allowance_subsidy_detection.js', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var show_button_import = "allowance_subsidy_detection";

    ListController.include({

        renderButtons: function ($node){
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;

            if (tree_model == show_button_import) {

                let allowance_subsidy_detection_button = $("<button id='allowance_subsidy_detection_button' type='button' class='btn btn-primary'>检测</button>").click(this.proxy("allowance_subsidy_detection"))
                this.$buttons.append(allowance_subsidy_detection_button);
            }

            return $buttons;
        },


        allowance_subsidy_detection: function () {

            document.getElementById("allowance_subsidy_detection_button").setAttribute("disabled", true);

            this._rpc({
                model: 'allowance_subsidy_detection',
                method: 'allowance_subsidy_detection',
                args: [[]]
            }).then((res) => {
                if (res) {
                    alert("同步成功！点击后刷新页面！");
                    location.reload();
                }
            })

        },

    });
});