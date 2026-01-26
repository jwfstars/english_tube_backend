from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

from app.core.config import settings


class TencentSmsClient:
    def __init__(self):
        if not settings.TENCENT_SMS_SECRET_ID or not settings.TENCENT_SMS_SECRET_KEY:
            raise ValueError("缺少腾讯云短信密钥配置")
        if not settings.TENCENT_SMS_SDK_APP_ID:
            raise ValueError("缺少腾讯云短信 SDK AppId 配置")
        if not settings.TENCENT_SMS_SIGN_NAME:
            raise ValueError("缺少腾讯云短信签名配置")
        if not settings.TENCENT_SMS_TEMPLATE_ID:
            raise ValueError("缺少腾讯云短信模板 ID 配置")

        cred = credential.Credential(
            settings.TENCENT_SMS_SECRET_ID,
            settings.TENCENT_SMS_SECRET_KEY,
        )
        http_profile = HttpProfile()
        http_profile.endpoint = "sms.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        self.client = sms_client.SmsClient(
            cred,
            settings.TENCENT_SMS_REGION,
            client_profile,
        )

    def send_sms(self, phone: str, code: str) -> None:
        req = models.SendSmsRequest()
        req.SmsSdkAppId = settings.TENCENT_SMS_SDK_APP_ID
        req.SignName = settings.TENCENT_SMS_SIGN_NAME
        req.TemplateId = settings.TENCENT_SMS_TEMPLATE_ID
        req.PhoneNumberSet = [phone]
        req.TemplateParamSet = [code]
        self.client.SendSms(req)
