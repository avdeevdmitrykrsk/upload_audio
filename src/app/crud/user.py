from fastapi import HTTPException, status

from app.crud.base import BaseCRUD
from app.models import User


class UserCRUD(BaseCRUD):

    async def get_or_404(
        self, session, obj_id, detail_message=None, extra_filters=None
    ):
        user = await super().get_or_404(
            session, obj_id, detail_message, extra_filters
        )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь неактивен.',
            )

        return user


crud_user = UserCRUD(User)
