# Standart lib imports
from http import HTTPStatus
from typing import Any, Dict, Optional

# Thirdparty imports
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD:
    """Базовый CRUD-класс"""

    def __init__(self, model: Any):
        self.model = model

    async def get_or_404(
        self,
        session: AsyncSession,
        obj_id: int,
        detail_message: Optional[str] = None,
        extra_filters: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Получает объект из БД по id"""
        stmt = select(self.model).where(self.model.id == obj_id)

        if extra_filters:
            for field, value in extra_filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)
                else:
                    raise ValueError(
                        f'Поле {field} не существует '
                        f'в модели {self.model.__name__}'
                    )

        result = await session.execute(stmt)
        instance = result.scalars().first()

        if not instance:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=detail_message or (
                    f'{self.model.__name__} с id {obj_id} не найден'
                ),
            )

        return instance

    async def create(self, session: AsyncSession, obj_data: dict) -> Any:
        """Создает объект в БД"""
        instance = self.model(**obj_data)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)

        return instance

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        """Удалает объект из БД"""
        instance = await self.get_or_404(session, obj_id)

        await session.delete(instance)
        await session.commit()

    async def update(
        self, session: AsyncSession, obj_id: int, obj_data: dict
    ) -> Any:
        """Обновляет объект в БД"""
        instance = await self.get_or_404(session, obj_id)

        for field, value in obj_data.items():
            setattr(instance, field, value)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)

        return instance
