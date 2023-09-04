
layui.use(function() {
    var form = layui.form;

    var key = document.getElementById("key").value

    form.on('select(fsn_workwx_outsource_order_line_select)', function(data){

        var value = data.value;
        var name = document.getElementById(value).innerText
        var selectedData = JSON.stringify([{"key": value, "value": name}])

        var url = location.href.split('#')[0]
        
        $.ajax({
            type: "get",        // 请求方式
            url: "/get_workwx_signature", // 请求路径
            data: {"url": url},
            dataType: "json",   // 预期返回一个 json 类型数据
            success: function (data) {   // data是形参名，代表返回的数据
                
                wx.agentConfig({
                    beat: true,
                    debug: true,
                    corpid: data.corpid, // 必填，企业微信的corpid，必须与当前登录的企业一致
                    agentid: data.agentid, // 必填，企业微信的应用id （e.g. 1000247）
                    timestamp: data.timestamp, // 必填，生成签名的时间戳
                    nonceStr: data.noncestr, // 必填，生成签名的随机串
                    signature: data.sha_str,// 必填，签名，见附录-JS-SDK使用权限签名算法
                    jsApiList: ['getApprovalSelectedItems', 'saveApprovalSelectedItems'], //必填，传入需要使用的接口名称
                    success: function(res) {

                        wx.invoke('saveApprovalSelectedItems', {
                            "key": key, // 字符串，从 URL 中获取到的 key
                            "selectedData": selectedData, // 字符串，选中的选项格式化为 JSON 字符串，格式见下文
                        }, (res) => {
                            if (res.err_msg === 'saveApprovalSelectedItems:ok') {
                                // 保存成功
                            }
                        });

                    },
                    fail: function(res) {
                        if(res.errMsg.indexOf('function not exist') > -1){
                            alert('版本过低请升级')
                        }
                    }
                });
    
            }
        });




    });
});