odoo.define("fsn_home_page/static/src/js/fsn_home_page_roll.js", function (require) {
    "use strict";

    const { useState } = owl.hooks;
    const { patch } = require('web.utils');

    const HomeMenu = require('web_enterprise.HomeMenu');
    const rpc = require('web.rpc');
    var session = require('web.session');
    
    patch(HomeMenu, 'fsn_home_page/static/src/js/fsn_home_page_roll.js', {

        set_visibility_scroll_bar_info() {

            let res = rpc.query({
                route: "/fsn_home_page/get_visibility_scroll_bar_info",
                params: {
                    "user_id": session.uid,
                },
            })

            return res

        },


        async willStart() {
            await this._super(...arguments);

            let res = await this.set_visibility_scroll_bar_info()

            this.scroll_bar_data = useState({
                text: res.text
            });
        }
        
        
    });



});
