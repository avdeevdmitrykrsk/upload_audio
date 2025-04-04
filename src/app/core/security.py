from datetime import timedelta

from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer

from app.core.config import settings


access_security = JwtAccessBearer(
    secret_key=settings.secret_key,
    access_expires_delta=timedelta(hours=settings.exp_access_token),
)
refresh_security = JwtRefreshBearer(
    secret_key=settings.secret_key,
    refresh_expires_delta=timedelta(days=settings.exp_refresh_token),
)
