from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    declarative_base,
    declared_attr,
    sessionmaker,
)


class PreBase:
    """Базовая модель для классов SQLAlchemy."""

    @declared_attr
    def __tablename__(cls):
        """Генерирует имя таблицы в lowercase."""
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime, server_default=func.now(), comment='Дата создания'
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment='Дата обновления',
    )


Base = declarative_base(cls=PreBase)
engine = create_async_engine('sqlite+aiosqlite:///audio_db.db')

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    """Генерирует асинхронную сессию для работы с БД."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
