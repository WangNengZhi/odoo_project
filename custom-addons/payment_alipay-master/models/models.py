# -*- coding: utf-8 -*-

from wsgiref.util import request_uri
from odoo import models, fields, api
from alipay import AliPay
from Crypto.PublicKey import RSA
import base64
from urllib.parse import quote_plus
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AcquirerAlipay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('alipay', "AliPay")], ondelete={'alipay': 'cascade'})
    seller_id = fields.Char("Alipay Seller Id")
    alipay_appid = fields.Char("Alipay AppId")
    alipay_secret = fields.Binary("Merchant Private Key")
    alipay_public_key = fields.Binary("Alipay Public Key")
    alipay_sign_type = fields.Selection(selection=[('rsa', 'RSA'), ('rsa2', 'RSA2')], string="Sign Type")
    fsn_public_key = fields.Text(string="支付宝公钥")
    fsn_private_key = fields.Text(string="应用私钥")

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerAlipay, self)._get_feature_support()
        res['fees'].append('alipay')
        return res

    def _get_alipay(self):
        """
        获取支付宝sdk
        """
        try:

            private_key = RSA.importKey(base64.b64decode(
                self.alipay_secret).decode('utf-8'), passphrase='BiD2fT29DdkrA+DJllhtxQ==')
            public_key = RSA.importKey(base64.b64decode(
                self.alipay_public_key).decode('utf-8'), passphrase='BiD2fT29DdkrA+DJllhtxQ==')

            # public_key = """-----BEGIN PUBLIC KEY-----
            #             MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlINskrOoyxG6xNBK9MgQYlUJAGgVhfUi/77v75/8aYModF7KUB13Y9JDnMgiMZ1v9rlK9x19Phv/TI3lY5MiFAojDj3v11SYU5QmzlNYMuBv9xvOHHkZOxqCXBzbzBBD3ds5f0xO9rbNXEaY++KVyOzoLtlx2YmLJ5Ze6XKIkEAuc2n60QdJM+gor48kbwvhtGqsMXyZ2XCxgyVYPGSURjGgcJrovqeKWPcXO348VHRvf6panS7iRrbsA8V09x66aUXGH4g9LZqTa2jliRz42YoDJ2GzdDmYLoS0oAIeeaUcQLb44wCk9Eb2wPViYTygusQqv+1QcsqoFgO2BHFECwIDAQAB
            #             -----END PUBLIC KEY-----"""
            # private_key = """-----BEGIN RSA PRIVATE KEY-----
            #             MIIEpgIBAAKCAQEA0emCKBRv+ii4KHEJyUd8/b+VaRLWVU8rJbwCfD+J1ys2w/FJvDY47Kt1NdUNPOsa9hmCoVOtlXF52nToqSxu1+RCVAzGwIjVyYWOLl54wJ+c5LBp4BxNoo/FJhS41PTh23cHL3RxPuG6/BjikgfuQQypLMX3t9h6/CFq/5JSedFLROWEvZtsPm9yONYV4Sj6vn73XHjCUU1yVIEh+v/oAoHFg+semkqg9KgqmSLBSoHQf5GhTcige890o35f8M1c/zWwT9T9Gg2A1dxq2j4mXLfFV8w/Urw1WO8RPBpFGC7WP5OR4zPqpzPdOdYn+BcH4yvtdb3E+SKvJSyTJwRWewIDAQABAoIBAQDERiHklg+KCk7/yYpMASM3JM9wuyNcCzWeB+kPAl5Bqe+AUXoPmWeqrDthhX/mSTMhkALcFCEHzl4QzSXLIXfXOGBotLWWy5uS3eVvJ/iiq9wI3Ydx/ST+bo36KIAW547UJby7O5a0JF8xX5di0jWN72e0LLuO1MVSQXEJ3Whu63hQ6NH4bs6vuiQINmF2nZNX1fqSx6+hdfpoC+HJgFZYhMua7r5C32UkiSTG5YFH4BZr153lWSmdjnWHb8bK+C3VHPvrv7O3H79nvuykgbtDgU+AXrbfwNnewLJwqmzF+9BO7jF8xCIAT+MC5pcUPKCeP7SL4W/TXCUA73qcL3BpAoGBAPmlyM7Iy8V664g/MnlrfSf2Wr5nEqT0h6P3R789wi7aPgfsZ7F/L4TPtGopewGsiwsA4DSIrOpBoYgk3rm3Y+41jvQxG1219nz5N/TtJLAeQMUs6yS3uU6NoQYBMO1+FnSOYLKTBqdUAMYAlLH9amvOFANOUJT1ydJ3AkZcnWqPAoGBANdA4rA6TF6RcoLS/6ZH/0aKsQ53BEGtgskDNTm52kAw3rI1gDzkxfY1LUN7ykE+HYv9hney4Hxm402Lkq1G8or6Hde37IdyFCwOi/yPfXdxJkF19E2f8BmEJ07n7HtfhcvYrvVO+al9qUuB46185ViysDkUR9QQjGqcOXu6PztVAoGBAIMkNp+B1aFwl+fjouUrtPxYKoUY6i9jERnuHW91xtsL5EgPRM12DYVMAu89yRMxC32FQUH3hjYssektzR5sGv+YfPcEEOciXlB6Lo3oQTyPN+EcXo3UQXDlb3ATEhu//5XM8Tj9iSI/O4TH61Sw1cW55MNz0Vre3t1DjRtfLYY7AoGBAJMO61CGo8JAEEG8sZgCvC6PdmNxgGD2j9GQ9X4YsTkFqj+KObBgg7avodrm6cklDL6lWIbSmHelO0mxP2ZOgEnekyDbsSbgE1P+JDlKNuexT/eNBHk7+acVGF3aKUAohJo90VoauIrJJS5G8SuHlpDAk5CLgH8rRyNW1BbpqWV5AoGBAI+NZZvKyo6wnR9ECOm9iQehKlBzkGFYnoz060iH8d1GARwWLkN0attjyHzZatIe8TWHv8LZcikTDay+UwLxWYLYGEwOXpdymY1lmizQzkWRhQrsIbOIny9EYPvvSYnKwcySN53KcXceCTTMavmxxUyyBFNqVWBL/OIk9MdnnU0S
            #             -----END RSA PRIVATE KEY-----"""
            public_key = self.fsn_public_key
            private_key = self.fsn_private_key

            print("-----------")
            print(self.state)
            if self.state == "enabled":
                # alipay = AliPay(self.alipay_appid, private_key, ali_public_key=public_key,
                #                 sign_type=self.alipay_sign_type)
                alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
                            appid=2021000121617060,  # 应用ID
                            app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
                            # 应用的私钥和支付宝公钥的路径
                            app_private_key_string=private_key,
                            alipay_public_key_string=public_key,
                            sign_type="RSA2",  # 加密标准
                            debug=False  # 指定是否是开发环境
                        )
            else:
                # alipay = AliPay(self.alipay_appid, private_key, ali_public_key=public_key,
                #                 sign_type=self.alipay_sign_type, sandbox=True)
                alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
                            appid=2021000121617060,  # 应用ID
                            app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
                            # 应用的私钥和支付宝公钥的路径
                            app_private_key_string=private_key,
                            alipay_public_key_string=public_key,
                            sign_type="RSA2",  # 加密标准
                            debug=True  # 指定是否是开发环境
                        )
            return alipay
        except Exception as err:
            _logger.exception(f"生成支付宝客户端失败：{err}")

    @api.model
    def _get_alipay_url(self, params=None):
        """Alipay URL"""
        # base_url = self.env['ir.config_parameter'].sudo(
        # ).get_param('web.base.url')
        base_url = "http://192.168.20.149:8069"

        alipay = self._get_alipay()

        return_url = f'{base_url}{params["return_url"]}'
        # return_url = f'{base_url}/payment_alipay/payment_successful/'
        notify_url = f'{base_url}{params["notify_url"]}'


        # SDK对象对接支付宝支付的接口，得到登录页的地址
        order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=params["reference"], # 商品编号，每次提交的时候，不能相同
                total_amount=params["amount"], # 商品价钱
                subject="FSN商城", # 名字
                return_url=return_url # 回调地址
                
        )
        # 电脑网站支付(正式环境)，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付(开发环境)，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = 'https://openapi.alipaydev.com/gateway.do' + '?' + order_string

        return alipay_url

    @api.model
    def alipay_compute_fees(self, amount, currency_id, country_id):
        """
            支付宝也是要恰饭的
            单笔费率 0.6%
        """
        if not self.fees_active:
            return 0.0
        return self.fees_dom_var / 100 * amount

    @api.model
    def alipay_get_form_action_url(self):
        return "/payment_alipay/jump"

    @api.model
    def alipay_form_generate_values(self, values):
        alipay_tx_values = dict(values)
        alipay_tx_values.update({
            "return_url": "/payment/alipay/validate",
            "notify_url": "/payment/alipay/notify"
        })
        return alipay_tx_values

    def _verify_pay(self, data):
        """
        验证支付宝返回的信息
        """
        alipay = self._get_alipay()
        # 验证是否符合验签逻辑
        if not alipay.comm.validate_sign(data):
            _logger.warn(f"支付宝推送支付结果验签失败：{data}")
            return False
        # 校验收款方
        if self.alipay_appid != data["app_id"]:
            _logger.warn(f"支付宝推送AppID校验失败:{data['app_id']}")
            return False
        if self.seller_id != data["seller_id"]:
            _logger.warn(f"支付宝推送卖家ID校验失败:{data['seller_id']}")
            return False
        # 校验支付信息
        transaction = self.env["payment.transaction"].sudo().search(
            [('reference', '=', data["out_trade_no"])], limit=1)
        if float(transaction.amount) != float(data["total_amount"]):
            _logger.warn(
                f"支付宝推送金额{float(transaction.amount)}与系统订单不符:{float(data['total_amount'])}")
            return False
        # 将支付结果设置完成
        if transaction.state != "done" and data["trade_status"] == "TRADE_SUCCESS":
            transaction.acquirer_reference = data["trade_no"]
            transaction._set_transaction_done()
            # 完成付款单
            sale_order = self.env['sale.order'].search(
                [('name', '=', data["out_trade_no"])], limit=1)
            if sale_order:
                elect = self.env.ref(
                    'payment.account_payment_method_electronic_in').id
                sale_order.custom_payment_id.payment_method_id = elect
                sale_order.custom_payment_id.payment_transaction_id = self.id
                sale_order.custom_payment_id.post()

        return True


class TxAlipay(models.Model):
    _inherit = 'payment.transaction'

    alipay_txn_type = fields.Char('Transaction type')

    @api.model
    def _alipay_form_get_tx_from_data(self, data):
        """获取支付事务"""
        if not data.get("out_trade_no", None):
            raise ValidationError("订单号错误")
        reference = data.get("out_trade_no")
        txs = self.env["payment.transaction"].search(
            [('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Alipay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.model
    def _alipay_form_validate(self, data):
        """验证支付"""
        if self.state == 'done':
            _logger.info(f"支付已经验证：{data['out_trade_no']}")
            return True
        result = {
            "acquirer_reference": data["trade_no"]
        }
        # 根据支付宝同步返回的信息，去支付宝服务器查询
        payment = self.env["payment.acquirer"].sudo().search(
            [('provider', '=', 'alipay')], limit=1)
        alipay = payment._get_alipay()

        res = alipay.api_alipay_trade_query(out_trade_no=data["out_trade_no"])


        # 校验结果
        if res["code"] == "10000" and res["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            _logger.info(f"支付单：{data['out_trade_no']} 已成功付款")
            date_validate = fields.Datetime.now()
            res.update(date=date_validate)
            self._set_transaction_done()
            self.execute_callback()
        if res["code"] == "10000" and res["trade_status"] == "WAIT_BUYER_PAY":
            _logger.info(f"支付单：{data['out_trade_no']} 正等待付款...")
            self._set_transaction_pending()
        if res["code"] == "10000" and res["trade_status"] == "TRADE_CLOSED":
            _logger.info(f"支付单：{data['out_trade_no']} 已关闭或已退款.")
            self._set_transaction_cancel()
        # 完成付款单
        sale_order = self.env['sale.order'].search(
            [('name', '=', data["out_trade_no"])], limit=1)
        if sale_order:
            elect = self.env.ref(
                'payment.account_payment_method_electronic_in').id
            sale_order.custom_payment_id.payment_method_id = elect
            sale_order.custom_payment_id.payment_transaction_id = self.id
            sale_order.custom_payment_id.post()

        return self.write(result)
