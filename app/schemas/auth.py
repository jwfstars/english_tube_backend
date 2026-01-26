from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class SmsSendRequest(BaseModel):
    phone: str = Field(..., description="手机号")


class SmsVerifyRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=4, max_length=8, description="验证码")


class ActivationVerifyRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=64, description="激活码")


class ActivationVerifyResponse(BaseModel):
    pre_token: str
    expires_at: datetime


class ActivationRegisterRequest(BaseModel):
    pre_token: str = Field(..., min_length=10, description="预激活令牌")
    email: EmailStr = Field(..., description="邮箱")
    username: str = Field(..., min_length=3, max_length=32, description="账号")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class ActivationGenerateRequest(BaseModel):
    count: int = Field(1, ge=1, le=100, description="生成数量")
    expires_in_days: int | None = Field(None, ge=1, le=365, description="有效期天数")


class ActivationGenerateResponse(BaseModel):
    codes: list[str]
    expires_at: datetime | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
