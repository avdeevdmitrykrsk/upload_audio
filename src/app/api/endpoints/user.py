# app/api/endpoints/user.py
import os
from http import HTTPStatus

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, Response
import httpx
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import get_current_superuser, get_current_user, user_manager
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

load_dotenv()

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
    return await user_manager.get_by_id(session, user_id)


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
    await user_manager.delete(session, user_id)


@router.patch(
    '/{user_id}',
    dependencies=[Depends(get_current_user)],
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для superuser."""
    return await user_manager.update(
        session, user_id, user_data.dict(exclude_unset=True)
    )
