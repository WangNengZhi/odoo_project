odoo.define('fsn_base/static/js/data_export.js', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var session = require('web.session');
    var rpc = require("web.rpc");

    ListController.include({

        check_the_permissions: async function () {

            // 判断是否是超级用户
            if (session.is_admin) {
                return true
            } else {

                var is_show = rpc.query({  // POST
                    route: "/fsn_base/check_the_permissions",
                    params: {
                        "model": this.modelName,
                        "user_id": session.uid,
                    }
                }).then((res) => {
                    return res.is_show
                })

                return is_show
            }

        },

        willStart: function() {
            const sup = this._super(...arguments);

            const exp = this.check_the_permissions().then(isExportEnable => {

                this.isExportEnable = isExportEnable;
            })

            return Promise.all([sup, exp]);

        }
    });

});