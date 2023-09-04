odoo.define('fsn_production_preparation/static/src/js/refresh_prenatal_preparation_progress.js', function (require) {
    "use strict";

    var ListController = require('web.ListController');


    ListController.include({

        init: function(parent, action) {

            this.odoo_context = action.loadParams.context

            return this._super.apply(this, arguments);
        },


        renderButtons: function () {
            var $buttons = this._super.apply(this, arguments);

            if (this.odoo_context.show_refresh_button) {

                var refresh_prenatal_preparation_progress_button = $("<button id='but' type='button' class='btn btn-primary'>更新数据</button>").click(this.proxy("refresh_prenatal_preparation_progress"))

                this.$buttons.append(refresh_prenatal_preparation_progress_button);
            }


            return $buttons;
        },

        refresh_prenatal_preparation_progress: function () {

            let is_refresh = confirm("确认更新数据吗？")

            if (is_refresh){

                this._rpc({
                    model: 'prenatal_preparation_progress',
                    method: 'refresh_prenatal_preparation_progress_info',
                    args: [[]],
                }).then(() => {
                    alert("更新成功！点击后刷新页面！")
                    location.reload();
                })
        
            }

        },

    });

})