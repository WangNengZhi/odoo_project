

function get_today_dg_data(data_type) {

    //data是要被分组的数据[]，key是分组依据的关键字
    let getGroup=(data,key)=>{
        let groups={};
        data.forEach(c=>{
            let value=c[key];
            groups[value]=groups[value]||[];
            groups[value].push(c);
        });
        return groups;
    }

    // 获取吊挂配置参数
    let res_obj
    $.ajax({
        url: "/get_check_position_settings",
        method: "get",
        // dataType: "json",
        async: false,

    }).success(function (res) {

        res_obj = $.parseJSON(res);
    })


    let data_list = []

    // 获取吊挂数据
    function get_data(record) {


        // 循环每个组的组站位
        for (var line of record.line) {

            let url = `http://${res_obj.dg_host}:${res_obj.dg_port}/DgApi/Details?BeginTime=${res_obj.start_date}&EndTime=${res_obj.end_date}&StationID=${line}&WorkLine=${record.group}`
            // let url = `http://${res_obj.dg_host}:${res_obj.dg_port}/DgApi/Details?BeginTime=2021-12-23&EndTime=2021-12-24&StationID=${line}&WorkLine=${record.group}`

            $.ajax({
                url: url,
                method: "get",
                async: false
            }).success(function (res) {

                // 按款号分组
                let MONo_group = getGroup(res.Data, 'ColorNo')

                // 循环每个款号
                for (var MONo_obj of Object.keys(MONo_group)) {

                    let tem_dict = {"dDate": res_obj.start_date, "gGroup": record.group, "MONo": false, "nNumber": 0}

                    // 循环每个款号分组后的数据
                    for (var work_rec of MONo_group[MONo_obj]) {

                        tem_dict.nNumber = tem_dict.nNumber + 1

                        if (tem_dict.MONo == false) {
                            tem_dict.MONo = MONo_obj
                        }

                    }
                    data_list.push(tem_dict)

                }

            })
        }
        return data_list

    }


    // 循环每个组
    for (var record of res_obj.data) {

        if (data_type == "车间") {

            if (record.group != "后整") {

                get_data(record)

            }

        }

        if (data_type == "后道") {

            if (record.group == "后整") {

                get_data(record)

            }

        }
    }


    return data_list

}


export { get_today_dg_data };