// js模板名称，可随便写
odoo.define('/my_dashboard/static/src/js/fsn_dashboard.js', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');


    var FsnDashboard = AbstractAction.extend({
        // Qweb模板名称
        template: 'qweb_suspension_system_index',
        events: {
            'click #wdc': '_get_lowest_efficiency_employee',
        },

        // 获取各组产量最低员工(最近一天)
        _get_minimum_number_employee: function () {

            this._rpc({
                model: "suspension_system_station_summary",
                method: 'fsn_dashboard_search',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#min_number_table_date").html(res.date);     //  日期

                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.number}</td></tr>`
                    }

                } else {

                    content_text = "获取不到数据信息！"

                }

                $("#min_number_table").html(content_text);

            });
        },

        // 获取各组产量最低员工(上一周)
        _get_last_week_minimum_number_employee: function () {
            this._rpc({
                model: "suspension_system_station_summary",
                method: 'get_last_week_data',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#last_week_min_number_table_date").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期

                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.number.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }
                $("#last_week_min_number_table").html(content_text);
            })
        },

        // 获取各组质量最差员工(最近一天)
        _get_quality_worst_employee: function () {
            this._rpc({
                model: "invest.invest",
                method: 'get_quality_worst_employee',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#max_quality_worst_date").html(res.date);     //  日期

                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.repairs_number}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }
                $("#max_quality_worst").html(content_text);

            })
        },

        // 获取各组质量最差员工(上一周)
        _get_last_week_quality_worst_employee: function () {
            this._rpc({
                model: "invest.invest",
                method: 'get_last_week_data',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#last_week_max_quality_worst_date").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期

                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.repairs_number.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }
                $("#last_week_min_min_lowest_efficiency").html(content_text);
            })
        },

        // 获取各组效率最低员工(最近一天)
        _get_lowest_efficiency_employee: function () {
            this._rpc({
                model: "eff.eff",
                method: 'get_lowest_efficiency_employee',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#min_lowest_efficiency_date").html(res.date);     //  日期

                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.efficiency.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }
                $("#min_lowest_efficiency").html(content_text);

            })
        },

        // 获取各组效率最低员工(上一周)
        _get_last_week_lowest_efficiency_employee: function () {
            this._rpc({
                model: "eff.eff",
                method: 'get_last_week_data',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#last_week_min_lowest_efficiency_date").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期
                    for (let record of res.data) {

                        content_text = content_text + `<tr><th scope="row">${record.group}</th><td>${record.name}</td><td>${record.efficiency.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }
                $("#last_week_min_lowest_efficiency").html(content_text);

            })
        },


        //  获取组产值排名
        _get_group_output: function () {
            this._rpc({
                model: "pro.pro",
                method: 'get_group_output',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#last_week_group_output_data").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期
                    for (let record in res.data) {

                        content_text = content_text + `<tr><th scope="row">${Number(record) + 1}</th><td>${res.data[record].group}</td><td>${res.data[record].pro_value.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }

                $("#last_week_group_output").html(content_text);


            })
        },

        // 获取组返修率排名
        _get_group_repair_rate: function () {
            this._rpc({
                model: "group_statistical",
                method: 'get_group_repair_rate',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#last_week_group_repair_rate_data").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期
                    for (let record in res.data) {

                        content_text = content_text + `<tr><th scope="row">${Number(record) + 1}</th><td>${res.data[record].group}</td><td>${res.data[record].repair_rate.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"

                }

                $("#last_week_group_output_repair_rate").html(content_text);

            })
        },

        //  获取组人均产值排名
        _get_group_avg_output: function () {
            this._rpc({
                model: "pro.pro",
                method: 'get_group_avg_output',
                args: [[]],
            }).then((res) => {

                let content_text = ""

                if (res.data.length != 0) {

                    $("#fsn_group_avg_output_date").html(`${res.date.begin_date}到${res.date.end_date}`);     //  日期
                    for (let record in res.data) {

                        content_text = content_text + `<tr><th scope="row">${Number(record) + 1}</th><td>${res.data[record].group}</td><td>${res.data[record].avg_value.toFixed(2)}</td></tr>`

                    }
                } else {

                    content_text = "获取不到数据信息！"
                }

                $("#fsn_group_avg_output").html(content_text);

            })
        },

        // 获取昨天计划数据
        _get_yesterday_plan_data: function () {
            this._rpc({
                model: "planning.slot",
                method: 'get_yesterday_plan_data',
                args: [[]],
            }).then((res) => {

                $("#fsn_production_plan_progress_date").html(res.today);     //  日期

                let content_text = ""

                for (let record of res.planning_slot_obj_list) {

                    content_text = content_text + `<tr>
                    <th scope="row" width="70px">${record.staff_group}</th>
                        <td>
                            <div class="progress">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="${record.progress_bar.toFixed(2)}" aria-valuemin="0" aria-valuemax="100" style="width: ${record.progress_bar.toFixed(2)}%">${record.progress_bar.toFixed(2)}%</div>
                            </div>
                        </td>
                    </tr>`
                }

                $("#fsn_production_plan_progress").html(content_text);

            })
        },


        init: function (parent, record, node, options) {
            this._super.apply(this, arguments);
            // console.log(parent);
            // console.log(record);
            // console.log(node);
            // console.log(options);
        },

        start: function () {
            this._super.apply(this, arguments);

            // 获取各组产量最低员工(最近一天)
            this._get_minimum_number_employee()
            // 获取各组产量最低员工(上一周)
            this._get_last_week_minimum_number_employee()

            // 获取各组质量最差员工(最近一天)
            this._get_quality_worst_employee()
            // 获取各组质量最差员工(上一周)
            this._get_last_week_quality_worst_employee()

            // 获取各组效率最低员工(最近一天)
            this._get_lowest_efficiency_employee()
            // 获取各组效率最低员工(上一周)
            this._get_last_week_lowest_efficiency_employee()

            //  获取组产值排名
            this._get_group_output()
            //  获取组返修率排名
            this._get_group_repair_rate()
            //  获取组人均产值排名
            this._get_group_avg_output()

            // 获取昨天计划数据
            this._get_yesterday_plan_data()


        }

    });


    // 客户端动作id：client_action_id
    core.action_registry.add('fsn_dashboard', FsnDashboard);

    return FsnDashboard;

});