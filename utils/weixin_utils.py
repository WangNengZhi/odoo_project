import requests

__all__ = ('get_access_token', 'send_text_to_enterprise_weixin', 'send_markdown_to_enterprise_weixin', 
           'send_app_group_info_text_weixin', 'send_app_group_info_markdown_weixin')

# content 的消息内容，最长要求不超过2048个字节
TEXT_MAX_BYTES = 2048

_CORPID = 'wwb23e2c5014887d84'   
                            # 企业 ID
_CORPSECRET = 'v3grASce-vMGmJuFA5EY4nN6ZF3qlAyc3VaE7ZC-89k'  # 应用的凭证密钥（消息通知）
_AGENTID = 1000002  # 应用id

_CORPSECRET_APPROVE = 'qqEISBLfI5hHze4P6Ytc1j1zBNYdg-PhIOSkmmZ3n0M'  # 应用的凭证密钥（审批）
_AGENTID_APPROVE = 3010040  # 应用id

# 总部 ('2'), 开发部 ('3')
HEAD_DEPT, DEV_DEPT = '2', '3'

# 风丝袅管理群 ('fsn02') 
ADMIN_GROUP = "fsn02"
# 开发测试群 ('fsn03')
DEVELOPMENT_AND_TEST = "fsn03"
# 风丝袅总部群 ('fsn04')
FAN_HQ = 'fsn04'
# 风丝袅全员群 ('fsn05')
ALL_PERSONNEL = "fsn05"
# 风丝袅车间群 (fsn06)
WORK_SHOW = 'fsn06'
# 风丝袅后道群 (fsn07)
AFTER_THE_ROAD = 'fsn07'
# 风丝袅外发群 (fsn08)
SEND_OUT = 'fsn08'
# 风丝袅人事群 (fsn09)
PERSONNEL_DEP = 'fsn09'
# 风丝袅销售群 (fsn10)
SALES_GROUP = 'fsn10'
# 风丝袅财务群
financial_group = 'wreOL6DQAA_57KpSTB10OHRCy6DsYBhA'
# 风丝袅技术科群
technology_group = 'wreOL6DQAARHLvzyCahthTtIZUnMI6JA'



def split_text(text, max_bytes=2048, encoding='utf8'):
    ''' 将文本按字节限长 `max_bytes` 分割成多个部分 '''
    if not text:
        return
    nbytes = start = 0
    for i, c in enumerate(text):
        m = len(c.encode(encoding))
        if nbytes + m <= max_bytes:
            nbytes += m
        else:
            yield text[start:i]
            nbytes, start = m, i
    yield text[start:]


def get_access_token(CORPSECRET):
    ''' 获取企业微信 token'''
    get_token_url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={_CORPID}&corpsecret={CORPSECRET}'
    resp = requests.get(get_token_url)
    assert resp.status_code == 200
    resp = resp.json()
    assert resp['errcode'] == 0
    return resp['access_token']



def send_text_to_enterprise_weixin(text, to_party):
    ''' 发送文本到企业微信 '''
    access_token = get_access_token(_CORPSECRET)

    send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    post_data = dict(
        toparty = to_party,
        msgtype = 'text',
        agentid = _AGENTID,
        text = dict(content = text),
        safe = 0,
        enable_id_trans = 0,
        enable_duplicate_check = 0,
        duplicate_check_interval = 1800
    )
    resp = requests.post(send_msg_url, json=post_data)  # !!
    assert resp.status_code == 200
    resp = resp.json()
    assert resp['errcode'] == 0


def send_markdown_to_enterprise_weixin(markdown, to_party):
    ''' 发送 markdown 到企业微信 '''
    for markdown in split_text(markdown, TEXT_MAX_BYTES):
        if not markdown.strip():
            continue

        access_token = get_access_token(_CORPSECRET)

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        post_data = dict(
            toparty = to_party,
            msgtype = 'markdown',
            agentid = _AGENTID,
            markdown = dict(content = markdown),
            enable_duplicate_check = 0,
            duplicate_check_interval = 1800
        )
        resp = requests.post(send_msg_url, json=post_data)  # !!
        assert resp.status_code == 200
        resp = resp.json()
        assert resp['errcode'] == 0


# todo
def send_image_to_enterprise_weixin(image, to_party):
    ''' 发送图片到企业微信 '''
    access_token = get_access_token(_CORPSECRET)

    send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    post_data = dict(
        toparty = to_party,
        msgtype = 'image',  
        agentid = _AGENTID,
        image = dict(media_id = image),
        safe = 0,
        enable_duplicate_check = 0,
        duplicate_check_interval = 1800
    )
    resp = requests.post(send_msg_url, json=post_data)  # !!
    assert resp.status_code == 200
    resp = resp.json()
    assert resp['errcode'] == 0


def send_app_group_info_text_weixin(text, chatid):
    """ 发送应用群消息text类型"""
    # nbytes = len(text.encode('utf8'))
    # print(len(text), nbytes)

    for text in split_text(text, TEXT_MAX_BYTES):
        if not text.strip():
            continue
        
        access_token = get_access_token(_CORPSECRET)

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/appchat/send?access_token={access_token}'
        post_data = {
            "chatid": chatid,
            "msgtype": "text",
            "text": {
                "content": text,
                },
            "safe": 0
        }
        resp = requests.post(send_msg_url, json=post_data)  # !!
        assert resp.status_code == 200
        resp = resp.json()
        assert resp['errcode'] == 0


def send_app_group_info_markdown_weixin(markdown, chatid):
    """ 发送应用群消息 markdown 类型"""
    for markdown in split_text(markdown, TEXT_MAX_BYTES):
        if not markdown.strip():
            continue

        access_token = get_access_token(_CORPSECRET)

        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/appchat/send?access_token={access_token}'
        post_data = {
            "chatid": chatid,
            "msgtype": "markdown",
            "markdown": {
                "content": markdown,
            },
            "safe": 0
        }
        resp = requests.post(send_msg_url, json=post_data)  # !!
        assert resp.status_code == 200
        resp = resp.json()
        assert resp['errcode'] == 0







########################################################################################################

def test_send_text():
    text = '''
<h4>吊挂组产量汇总</h4>
<table>
  <tr>
    <th>日期</th>
    <th>时间</th>
    <th>组别</th>
    <th>款号</th>
    <th>总件数</th>
    <th>件数差值</th>
    <th>产值</th>
  </tr>

  <tr>
    <td>2021年12月01日</td>
    <td>9</td>
    <td>车缝五组</td>
    <td>1552-PL</td>
    <td>11</td>
    <td>0</td>
    <td>0.00</td>
  </tr>
  <tr>
    <td>2021年12月01日</td>
    <td>9</td>
    <td>车缝六组</td>
    <td>1891-CR</td>
    <td>23</td>
    <td>0</td>
    <td>0.00</td>
  </tr>

</table>'''
    send_text_to_enterprise_weixin(text, to_party=DEV_DEPT)  # 开发部门


def test_send_markdown():
    markdown = '''#### 吊挂组产量汇总
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
'''
    send_markdown_to_enterprise_weixin(markdown, to_party=DEV_DEPT)  # 开发部门


def test_send_markdown_to_app_group():
    markdown = '''#### 吊挂组产量汇总
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝五组
>款号：1552-PL
>总件数：11
>件数差值：0
>产值：0.00
>
>日期：2021年12月01日
>时间：9
>组别：车缝六组
>款号：1891-CR
>总件数：23
>件数差值：0
>产值：0.00
'''
    send_app_group_info_markdown_weixin(markdown, DEVELOPMENT_AND_TEST)  # 开发部门


if __name__ == '__main__':
    ...
    # test_send_markdown()
