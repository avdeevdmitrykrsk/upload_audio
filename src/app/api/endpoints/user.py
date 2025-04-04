# app/api/endpoints/user.py
from http import HTTPStatus

import httpx
from fastapi import APIRouter, FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, Response
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import (
    check_owner_or_superuser,
    get_current_superuser,
    get_current_user,
)
from app.crud.user import crud_user
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate


router = APIRouter(prefix='/users')


@router.get('/me', response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get('/{user_id}', response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    return await crud_user.get_or_404(session, user_id)


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(get_current_superuser)],
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для superuser."""
    await crud_user.delete(session, user_id)


@router.patch(
    '/{user_id}',
    dependencies=[Depends(check_owner_or_superuser)],
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для superuser."""
    return await crud_user.update(
        session, user_id, user_data.dict(exclude_unset=True)
    )
