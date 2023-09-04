odoo.define('inherit_mail/static/src/js/send_daily.js', function (require) {
    "use strict";

    const Discuss = require('mail/static/src/widgets/discuss/discuss.js');
    var rpc = require('web.rpc');
    var session = require('web.session');

    Discuss.include({

        init(parent, action, options={}) {
            this._super(...arguments);

            var send_daily_button = $("<button class='send_daily btn btn-primary' type='button' title='发送日报'>发送日报</button>").click(this.proxy("send_daily"));
            this.check_is_super_user(send_daily_button)

        },

        // 检测是否是超级用户
        check_is_super_user (send_daily_button) {
            if (session.is_admin) {
                this.$buttons.append(send_daily_button);
            } else {

                rpc.query({
                    route: "/inherit_mail/daily_newspaper_refresh",
                }).then((res) => {

                    if (res.is_show) {
                        this.$buttons.append(send_daily_button);
                    }
                })

            }

        },
        // 发送日报
        send_daily () {

            document.getElementsByClassName("send_daily")[0].setAttribute("disabled", true);

            rpc.query({
                model: 'fsn_daily',
                method: 'send_fsn_daily',
                args: [[]],
                kwargs: {
                    "internal_message_type": "only_daily"
                }
            }).then(res => {
                alert("发送成功！")
            })
        },

    })

})