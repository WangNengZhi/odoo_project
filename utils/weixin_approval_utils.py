from utils import weixin_utils
import requests

__all__ = ('get_jsapi_ticket', 'get_approval_number_info', 'get_approval_details_info')

# sp_status-审批单状态（1-审批中；2-已通过；3-已驳回；4-已撤销；6-通过后撤销；7-已删除；10-已支付）
UNDER_APPROVAL, HAVE_PASSED, REJECTED, REVOKED, REVOCATION_AFTER_ADOPTION, DELETED, PAID = 1, 2, 3, 4, 6, 7, 10

SP_TEMPLATE_ID = "3WLJP2o8AhuNAELbtqnKuZLRpw44Yna58XGkneNf"     # 外发收货审批模板
INVEST_SP_TEMPLATE_ID = "C4UCHtvPzBirVuNM4WeEF2iCrSDt15GStjbZEgzHd"     # 中查交货审批模板


def get_jsapi_ticket():
    """
    通过access_token获取到应用jsapi_ticket
    jsapi_ticket是H5应用调用企业微信JS接口的临时票据
    分为企业 jsapi_ticket和 应用jsapi_ket
    详情 https://developer.work.weixin.qq.com/document/path/90506
    """
    access_token = weixin_utils.get_access_token(weixin_utils._CORPSECRET)

    url = 'https://qyapi.weixin.qq.com/cgi-bin/ticket/get?access_token={}&type=agent_config'.format(access_token)
    resp = requests.get(url).json()
    if resp['errmsg'] == 'ok':
        return resp['ticket']
    else:
        print('请求错误', resp['errmsg'])
        return ''


def get_approval_number_info(last_time_stamp, now_time_stamp, sp_template_id, sp_status):
    ''' 获取企业微信审批编号'''

    access_token = weixin_utils.get_access_token(weixin_utils._CORPSECRET_APPROVE)

    url = f'https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovalinfo?access_token={access_token}'
    data = {
        "starttime": last_time_stamp,
        "endtime": now_time_stamp,
        "cursor": 0,
        "size": 100,
        "filters" : [
            {
                "key": "template_id",
                "value": sp_template_id
            },
            {
                "key" : "sp_status",
                "value" : sp_status
            }     
        ]
    }
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    resp = resp.json()
    assert resp['errcode'] == 0
    return resp['sp_no_list']



def get_approval_details_info(sp_no):
    ''' 获取企业微信审批详情'''

    access_token = weixin_utils.get_access_token(weixin_utils._CORPSECRET_APPROVE)

    url = f'https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovaldetail?access_token={access_token}'
    data = {
        "sp_no" : sp_no
    }

    resp = requests.post(url, json=data)

    assert resp.status_code == 200
    resp = resp.json()
    assert resp['errcode'] == 0
    return resp['info']

