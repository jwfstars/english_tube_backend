from datetime import datetime, timedelta, timezone
import random
import re
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.auth import fastapi_users, auth_backend, get_jwt_strategy, get_user_manager
from app.core.config import settings
from app.core.database import get_db
from app.models.activation_code import ActivationCode
from app.models.activation_session import ActivationSession
from app.models.sms_code import SmsCode
from app.models.user import User
from app.schemas.auth import (
    SmsSendRequest,
    SmsVerifyRequest,
    ActivationVerifyRequest,
    ActivationVerifyResponse,
    ActivationRegisterRequest,
    ActivationGenerateRequest,
    ActivationGenerateResponse,
    TokenResponse,
)
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.sms import TencentSmsClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PHONE_PATTERN = re.compile(r"^\+?\d{6,20}$")
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
PASSWORD_MIN_LENGTH = 6
ACTIVATION_CODE_LENGTH = 12
ACTIVATION_CODE_ALPHABET = string.ascii_uppercase + string.digits

router = APIRouter()
current_superuser = fastapi_users.current_user(active=True, superuser=True)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.post("/auth/sms/send")
async def send_sms_code(payload: SmsSendRequest, db: AsyncSession = Depends(get_db)):
    phone = payload.phone.strip()
    if not PHONE_PATTERN.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    code = f"{random.randint(0, 999999):06d}"
    code_hash = pwd_context.hash(code)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.SMS_CODE_EXPIRE_MINUTES
    )

    await db.execute(delete(SmsCode).where(SmsCode.phone == phone))
    sms_code = SmsCode(
        phone=phone,
        code_hash=code_hash,
        expires_at=expires_at,
    )
    db.add(sms_code)
    await db.commit()

    if settings.SMS_DEBUG:
        return {"sent": True, "code": code}

    client = TencentSmsClient()
    try:
        client.send_sms(phone, code)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"短信发送失败: {exc}")

    return {"sent": True}


@router.post("/auth/sms/verify", response_model=TokenResponse)
async def verify_sms_code(
    payload: SmsVerifyRequest,
    db: AsyncSession = Depends(get_db),
    user_manager=Depends(get_user_manager),
):
    phone = payload.phone.strip()
    code = payload.code.strip()
    if not PHONE_PATTERN.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    result = await db.execute(
        select(SmsCode)
        .where(SmsCode.phone == phone, SmsCode.is_used.is_(False))
        .order_by(SmsCode.created_at.desc())
    )
    sms_code = result.scalars().first()
    if not sms_code:
        raise HTTPException(status_code=400, detail="验证码无效")

    if sms_code.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="验证码已过期")

    if sms_code.attempts >= 5:
        raise HTTPException(status_code=400, detail="验证码尝试过多")

    if not pwd_context.verify(code, sms_code.code_hash):
        sms_code.attempts += 1
        await db.commit()
        raise HTTPException(status_code=400, detail="验证码错误")

    sms_code.is_used = True
    await db.commit()

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalars().first()
    if not user:
        placeholder_email = f"{phone}@sms.local"
        random_password = secrets.token_urlsafe(16)
        user_in = UserCreate(
            email=placeholder_email,
            password=random_password,
            phone=phone,
            display_name=None,
        )
        user = await user_manager.create(user_in, safe=True)

    strategy = get_jwt_strategy()
    token = await strategy.write_token(user)
    return TokenResponse(access_token=token)


@router.post("/activation/verify", response_model=ActivationVerifyResponse)
async def verify_activation_code(
    payload: ActivationVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    code = payload.code.strip()
    result = await db.execute(
        select(ActivationCode).where(ActivationCode.code == code)
    )
    activation = result.scalars().first()
    if not activation:
        raise HTTPException(status_code=400, detail="激活码无效")

    if activation.is_used:
        raise HTTPException(status_code=400, detail="激活码已使用")

    now = datetime.now(timezone.utc)
    if activation.expires_at and activation.expires_at < now:
        raise HTTPException(status_code=400, detail="激活码已过期")

    await db.execute(
        delete(ActivationSession).where(
            ActivationSession.code_id == activation.id,
            ActivationSession.is_used.is_(False),
        )
    )

    token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(minutes=settings.ACTIVATION_SESSION_EXPIRE_MINUTES)
    session = ActivationSession(
        token=token,
        code_id=activation.id,
        expires_at=expires_at,
    )
    db.add(session)
    await db.commit()

    return ActivationVerifyResponse(pre_token=token, expires_at=expires_at)


@router.post("/activation/register", response_model=TokenResponse)
async def register_with_activation(
    payload: ActivationRegisterRequest,
    db: AsyncSession = Depends(get_db),
    user_manager=Depends(get_user_manager),
):
    pre_token = payload.pre_token.strip()
    result = await db.execute(
        select(ActivationSession).where(
            ActivationSession.token == pre_token,
            ActivationSession.is_used.is_(False),
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=400, detail="预激活令牌无效")

    now = datetime.now(timezone.utc)
    if session.expires_at < now:
        raise HTTPException(status_code=400, detail="预激活令牌已过期")

    result = await db.execute(
        select(ActivationCode).where(ActivationCode.id == session.code_id)
    )
    activation = result.scalars().first()
    if not activation or activation.is_used:
        raise HTTPException(status_code=400, detail="激活码不可用")

    username = payload.username.strip()
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(status_code=400, detail="账号格式不正确")

    if len(payload.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(status_code=400, detail="密码长度不足")

    result = await db.execute(select(User).where(User.username == username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="账号已存在")

    email = payload.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")

    user_in = UserCreate(
        email=email,
        password=payload.password,
        username=username,
        display_name=username,
    )
    user = await user_manager.create(user_in, safe=True)

    activation.is_used = True
    activation.used_at = now
    activation.used_by_user_id = user.id
    session.is_used = True
    session.used_at = now
    await db.commit()

    strategy = get_jwt_strategy()
    token = await strategy.write_token(user)
    return TokenResponse(access_token=token)


@router.post("/activation/generate", response_model=ActivationGenerateResponse)
async def generate_activation_codes(
    payload: ActivationGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    now = datetime.now(timezone.utc)
    expires_at = None
    if payload.expires_in_days:
        expires_at = now + timedelta(days=payload.expires_in_days)

    codes: list[str] = []
    attempts = 0
    while len(codes) < payload.count:
        if attempts > payload.count * 10:
            raise HTTPException(status_code=500, detail="激活码生成失败")
        attempts += 1
        raw = "".join(secrets.choice(ACTIVATION_CODE_ALPHABET) for _ in range(ACTIVATION_CODE_LENGTH))
        code = f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"
        result = await db.execute(
            select(ActivationCode).where(ActivationCode.code == code)
        )
        exists = result.scalars().first()
        if exists:
            continue
        db.add(
            ActivationCode(
                code=code,
                expires_at=expires_at,
            )
        )
        codes.append(code)

    await db.commit()
    return ActivationGenerateResponse(codes=codes, expires_at=expires_at)
