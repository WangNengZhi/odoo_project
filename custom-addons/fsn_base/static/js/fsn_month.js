odoo.define('fsn_base/static/src/js/fsn_month.js', function (require) {
    "use strict";
    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');
    var core = require('web.core');
    var QWeb = core.qweb;


    const FsnMonth = AbstractField.extend({
        supportedFieldTypes: ['char'],

        template: 'fsn_base_fsn_month_template',

        events: {
            'change #fsn_month': 'set_month_value',
        },

        set_month_value: function () {

            let value  = $("#fsn_month").val()

            this._setValue(value)
        },


        _renderReadonly: function () {
            this._super.apply(this, arguments);
            let value = this.value
            if (value) {
                this.$el.html(value);
            }
        },
        _renderEdit: function () {
            this._super.apply(this, arguments);

            let value = this.value

            if (value) {
                this.$el.html(QWeb.render("fsn_base_fsn_month_template", {"month": value}));
            }
        },

    });

    fieldRegistry.add('fsn_month', FsnMonth);

    return FsnMonth;
    
})
