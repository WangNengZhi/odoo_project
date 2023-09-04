odoo.define('template_house/static/src/js/sync_machine_data.js', function (require) {
    "use strict";

    var ListController = require('web.ListController');  // 引入列表控制器，用来修改 tree 视图
    var show_button_import = "template_machine_record";  // 指定那个模型添加：想要自定义内容的模型
    var rpc = require('web.rpc');

    ListController.include({

        // 自定义按钮方法
        renderButtons: function($node) {
            var $buttons = this._super.apply(this, arguments);
            var tree_model = this.modelName;    // 当前模型名称
            // 如果当前模型名称为上面定义的模型名称
            if (tree_model == show_button_import) {
                setInterval(function() {
                        // console.log("Here!!");
                        var obj = $('.o_pager_limit');
                        if (! (obj.length && obj.text())) {
                            return;
                        }
                        var count = obj.text();
                        // console.log(count, typeof count);
                        count = parseInt(count, 10);
                        rpc.query({  // POST
                            route: "/check_update",
                            params: {
                                "count": count
                            }
                        }).then(function(resp) {
                            // console.log(resp + " " + typeof resp);

                            resp = JSON.parse(resp);
                            if (resp.status == 0) {
                                if (resp.changed) {
                                    // alert("有更新！点击后刷新页面！");
                                    location.reload();
                                }
                            } else {
                                console.log("check update 出错！");
                            }
                        });
                    }, 60*1000/*ms*/);
            }
            return $buttons;
        },

        sync_machine_data: function() {
            // console.log("here!");

            rpc.query({  // POST
                route: "/sync_machine_data"
            }).then(function(resp) {
                // alert(resp + " " + typeof resp);  // {"status": 0, "messages": "\u6210\u529f\uff01"} string

                resp = JSON.parse(resp);
                if (resp.status == 0) {
                    alert("同步成功！点击后刷新页面！");
                    location.reload();
                } else {
                    alert("同步出错！");
                }
            });
        }

    });
});