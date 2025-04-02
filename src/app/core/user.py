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
from app.models.user import User


access_security = JwtAccessBearer(
    secret_key=settings.secret_key,
    auto_error=True,
    access_expires_delta=timedelta(hours=settings.exp_access_token),
)


class UserManager:

    async def get_by_id(self, session: AsyncSession, user_id: int) -> User:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Пользователь с данным id не найден.',
            )

        return user

    async def create(self, session: AsyncSession, user_data: dict) -> User:
        user = User(**user_data)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user

    async def delete(self, session: AsyncSession, user_id: int) -> None:
        user = await self.get_by_id(session, user_id)

        await session.delete(user)
        await session.commit()

    async def update(
        self, session: AsyncSession, user_id: int, user_data: dict
    ) -> User:
        user = await self.get_by_id(session, user_id)

        for field, value in user_data.items():
            setattr(user, field, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user


async def get_current_user(
    credentials: JwtAuthorizationCredentials = Depends(access_security),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    user_id = credentials.subject['user_id']

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User inactive or deleted'
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Forbidden'
        )
    return current_user


user_manager = UserManager()
