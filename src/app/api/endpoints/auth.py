from datetime import datetime, timedelta
import os
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    FastAPI,
    Request,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi_jwt import (
    JwtAccessBearer,
    JwtAuthorizationCredentials,
    JwtRefreshBearer,
)
from jose import jwt, JWTError
from pydantic import BaseModel
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import user_manager
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/auth')


access_security = JwtAccessBearer(
    secret_key=settings.secret_key,
    access_expires_delta=timedelta(hours=settings.exp_access_token),
)
refresh_security = JwtRefreshBearer(
    secret_key=settings.secret_key,
    refresh_expires_delta=timedelta(days=settings.exp_refresh_token),
)


@router.get('/yandex')
async def auth_yandex():
    """Перенаправление на страницу авторизации Яндекс"""
    return RedirectResponse(
        f'{settings.yandex_auth_url}?'
        f'response_type=code&'
        f'client_id={settings.client_id}&'
        f'redirect_uri={settings.redirect_uri}&'
        f'scope=login:email'
    )


@router.get('/yandex/callback')
async def auth_yandex_callback(
    code: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Обработка callback от Яндекс OAuth"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.yandex_token_url,
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': settings.client_id,
                    'client_secret': settings.client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            token_data = response.json()
    except (httpx.HTTPError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Ошибка при получении токена от Яндекс',
        ) from e

    access_token = token_data['access_token']

    try:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                settings.yandex_user_info_url,
                headers={'Authorization': f'OAuth {access_token}'},
                timeout=10.0,
            )
            user_response.raise_for_status()
            user_data = user_response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Ошибка при получении данных пользователя от Яндекс',
        ) from e

    if not all(k in user_data for k in ['id', 'default_email']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неполные данные от Яндекс',
        )

    yandex_id = str(user_data['id'])
    email = user_data['default_email']
    login = user_data.get('login') or email.split('@')[0]

    result = await session.execute(
        select(User).where(
            (User.email == email) | (User.yandex_id == yandex_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        user_data = {
            'email': email,
            'login': login,
            'is_active': True,
            'is_superuser': False,
            'yandex_id': yandex_id,
        }
        user: User = await user_manager.create(session, user_data)
    else:
        if not user.yandex_id:
            user.yandex_id = yandex_id
            session.add(user)
            await session.commit()

    access_token = access_security.create_access_token(
        subject={'user_id': str(user.id)}
    )
    refresh_token = refresh_security.create_refresh_token(
        subject={'user_id': str(user.id)}
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
    }


@router.post('/refresh')
async def refresh(
    credentials: JwtAuthorizationCredentials = Depends(refresh_security),
):
    new_access_token = access_security.create_access_token(
        subject=credentials.subject
    )
    return {'access_token': new_access_token}
