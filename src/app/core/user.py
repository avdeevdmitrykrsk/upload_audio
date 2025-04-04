import os
from datetime import timedelta
from http import HTTPStatus
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.security import access_security
from app.crud.user import crud_user
from app.models.user import User


async def get_current_user(
    credentials: JwtAuthorizationCredentials = Depends(access_security),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    return await crud_user.get_or_404(session, credentials.subject['user_id'])


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Forbidden'
        )
    return current_user


async def check_owner_or_superuser(
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Проверяет, может ли текущий пользователь редактировать
    указанного пользователя
    """
    if current_user.is_superuser:
        return

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Можно редактировать только свой профиль.',
        )

    return
