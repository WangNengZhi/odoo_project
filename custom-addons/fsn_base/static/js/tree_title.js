odoo.define('fsn_base/static/src/js/tree_title.js', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({

        init: function(parent, action) {

            this.odoo_context = action.context;

            return this._super.apply(this, arguments);
        },

        _renderHeaderCell: function (node) {
            var $th = this._super.apply(this, arguments);

            const { name } = node.attrs;

            if (this.odoo_context.factory_delivery_variance) {

                const head_red_arr = ["difference_delivery", "factory_delivery_variance", "attrition_rate"]

                if (head_red_arr.includes(name)) {

                    $th.css("color", "red");

                }

            }

            return $th;

        },


    })

});
