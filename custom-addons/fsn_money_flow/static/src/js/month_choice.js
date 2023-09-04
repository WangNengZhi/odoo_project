odoo.define('month_choice', function (require) {
    "use strict";
    var core = require('web.core');
    // var Qweb = core.qweb;
    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');



    var AbstractFieldPortrait = AbstractField.extend({


        init: function (parent, record, node, options) {

            this._super.apply(this, arguments);

        },


        template: 'month_choice',
        events: {

        },
        _renderEdit: function () {
            let self = this

            this._rpc({
                model: this.model,
                method: 'read',
                args: [this.res_id, ['month']],
            }).then((res) => {

                if (res.length != 0) {
                    this.$("#month_choice").val(res[0].month)
                } else {

                }

                this.$("#month_choice").removeAttr("readonly")

            });

        },

        _renderReadonly: function () {
            let self = this

            this.date_month = $("#month_choice").val()
            
            if (this.date_month) {
                this._setValue(this.date_month)
            }

            this._rpc({
                model: this.model,
                method: 'read',
                args: [this.res_id, ['month']],
            }).then((res) => {

                this.$("#month_choice").val(res[0].month)
                this.$("#month_choice").attr("readonly", "readonly");   // 只读
                this.$("#month_choice").attr("style", "border:none;");  // 隐藏边框

            });

        },


        _setValue: function (value, options) {

            if (this.field.trim) {
                value = value.trim();
            }
            return this._super(value, options);
        },

    });

    // 注册为 widget
    field_registry.add('month_choice', AbstractFieldPortrait);
});
